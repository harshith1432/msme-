"""
Asynchronous background tasks for OCR and document extraction.
"""
from backend.tasks.celery_app import celery_app
from backend.services.extraction_service import ExtractionService

@celery_app.task(name='tasks.process_document_extraction', bind=True, max_retries=3)
def process_document_extraction(self, document_id):
    """Executes OCR/heuristic text extraction in background worker."""
    service = ExtractionService()
    try:
        extraction = service.process_document(document_id)
        return {
            'document_id': document_id,
            'extraction_id': extraction.id if extraction else None,
            'status': extraction.status if extraction else 'failed'
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)
