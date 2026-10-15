# Security & Threat Model

## 1. Authentication & Session Management

- Passwords hashed using Werkzeug PBKDF2 with SHA-256 and unique salts.
- Sessions protected with HTTPOnly cookies, SameSite=Lax, and optional TLS Secure flags.

## 2. Tenant Isolation & IDOR Protection

- Every document, obligation, metric, task, and workspace is strictly scoped to `company.id` and `tenant.id`.
- The AI Advisor Tool Dispatcher strictly denies cross-tenant queries with explicit `PermissionDenied` guardrails.

## 3. Server-Side Request Forgery (SSRF) Defense

- The Official Website Research Service verifies that URLs resolve exclusively to approved Indian Government top-level domains (`.gov.in`, `.nic.in`) and blocks internal private IP spaces (e.g. `127.0.0.1`, `10.0.0.0/8`, `192.168.0.0/16`, cloud metadata endpoints `169.254.169.254`).

## 4. Unsafe Document & Execution Guardrails

- Uploaded files are treated as untrusted data.
- User files and generated documents are kept out of `frontend/static/` and protected by authenticated routes or short-lived presigned URLs.
