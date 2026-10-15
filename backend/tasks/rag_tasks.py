"""
Asynchronous background tasks for RAG ingestion and chunk indexing.
"""
from backend.tasks.celery_app import celery_app
from backend.services.rag_service import rag_service

@celery_app.task(name='tasks.process_rag_ingestion', bind=True, max_retries=2)
def process_rag_ingestion(self, document_id):
    """Executes file hashing, text extraction, and chunk generation in background worker."""
    try:
        success, msg = rag_service.ingest_document(document_id)
        return {'document_id': document_id, 'success': success, 'message': msg}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=15)
