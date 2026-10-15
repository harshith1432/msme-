"""
Production Hugging Face Inference Provider Client for MSME Navigator.
Handles:
  - Official huggingface_hub.InferenceClient interaction
  - Request timeouts, bounded exponential backoff retries
  - Structured error classification (Rate limit, Timeout, Auth, Model Unavailable)
  - Safe logging without token leakage or prompt leakage
  - Strict provider adherence (no silent fallbacks to unrestricted models)
"""
import os
import time
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("msme.rag.hf_client")

class HFClientError(Exception):
    """Base exception for Hugging Face integration errors."""
    pass

class HFAuthError(HFClientError):
    """Missing, invalid, or unauthorized Hugging Face token."""
    pass

class HFRateLimitError(HFClientError):
    """Rate limit (429) exceeded on Hugging Face Inference API."""
    pass

class HFTimeoutError(HFClientError):
    """Network or execution timeout contacting Hugging Face."""
    pass

class HFModelUnavailableError(HFClientError):
    """Configured model is unavailable, not supported by provider, or requires subscription."""
    pass

class HFProviderError(HFClientError):
    """General provider or gateway error from Hugging Face."""
    pass

class HuggingFaceInferenceService:
    def __init__(
        self,
        token: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        timeout: int = 20,
        max_retries: int = 2,
        max_tokens: int = 512
    ):
        self.token = token or os.environ.get("HF_TOKEN")
        self.model = model or os.environ.get("HF_MODEL", "meta-llama/Llama-3.2-3B-Instruct")
        self.provider = provider or os.environ.get("HF_PROVIDER") or None
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_tokens = max_tokens
        self._mock_handler = None  # Hook for synthetic testing

    def set_mock_handler(self, handler):
        """Allows injecting mock generation for unit tests."""
        self._mock_handler = handler

    def _get_client(self):
        if not self.token:
            raise HFAuthError("Hugging Face API token is missing or not configured (HF_TOKEN).")
        
        from huggingface_hub import InferenceClient
        kwargs = {
            "token": self.token,
            "timeout": self.timeout
        }
        if self.provider:
            kwargs["provider"] = self.provider
        return InferenceClient(**kwargs)

    def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Executes chat completion via official Hugging Face Inference Providers.
        Guarantees bounded retries, timeouts, and safe error handling.
        """
        if self._mock_handler is not None:
            return self._mock_handler(messages=messages, model=self.model, temperature=temperature)

        if not self.token:
            raise HFAuthError("Hugging Face API token is not configured.")

        max_tokens = max_tokens or self.max_tokens
        client = self._get_client()

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Calling Hugging Face Inference API (model={self.model}, attempt={attempt + 1})")
                
                # Official chat completion request
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                if not response or not response.choices:
                    raise HFProviderError("Hugging Face returned an empty response or malformed payload.")

                content = response.choices[0].message.content
                if content is None:
                    raise HFProviderError("Hugging Face returned empty content in message choice.")
                
                return content.strip()

            except Exception as e:
                err_str = str(e)
                last_error = e
                logger.warning(f"Hugging Face call attempt {attempt + 1} failed: {type(e).__name__}")

                # Classify error
                if "401" in err_str or "unauthorized" in err_str.lower() or "invalid token" in err_str.lower():
                    raise HFAuthError(f"Authentication failed: Invalid or unauthorized token.") from e

                if "429" in err_str or "rate limit" in err_str.lower():
                    if attempt < self.max_retries:
                        sleep_time = (2 ** attempt) * 1.5
                        time.sleep(sleep_time)
                        continue
                    raise HFRateLimitError(f"Hugging Face rate limit exceeded after {self.max_retries + 1} attempts.") from e

                if "timed out" in err_str.lower() or "timeout" in err_str.lower():
                    if attempt < self.max_retries:
                        time.sleep(1.0)
                        continue
                    raise HFTimeoutError(f"Hugging Face inference request timed out after {self.timeout}s.") from e

                if "model_not_supported" in err_str or "not supported by any provider" in err_str.lower() or "402" in err_str or "404" in err_str:
                    raise HFModelUnavailableError(f"Model '{self.model}' is currently unavailable or unsupported by provider.") from e

                # For general network transient errors, retry up to limit
                if attempt < self.max_retries:
                    time.sleep(1.0)
                    continue

                raise HFProviderError(f"Hugging Face inference failed: {err_str[:200]}") from e

        raise HFProviderError(f"Exceeded max retries for Hugging Face: {last_error}")

hf_service = HuggingFaceInferenceService()
