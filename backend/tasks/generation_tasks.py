"""
Asynchronous background tasks for generating PDF and DOCX application packages.
"""
from backend.tasks.celery_app import celery_app
from backend.services.document_generator import document_generator

@celery_app.task(name='tasks.generate_application_checklist_pdf', bind=True)
def generate_application_checklist_pdf(self, company_name, udyam_reg, workspace_title, checklist_items):
    file_path, filename = document_generator.generate_checklist_pdf(
        company_name, udyam_reg, workspace_title, checklist_items
    )
    return {'filename': filename, 'file_path': file_path}

@celery_app.task(name='tasks.generate_authority_cover_letter_docx', bind=True)
def generate_authority_cover_letter_docx(self, company_name, udyam_reg, authority_name, scheme_name, state, sector):
    file_path, filename = document_generator.generate_cover_letter_docx(
        company_name, udyam_reg, authority_name, scheme_name, state, sector
    )
    return {'filename': filename, 'file_path': file_path}
