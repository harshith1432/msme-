# Production Storage Architecture

## 1. Storage Abstraction

All file interactions go through `backend.services.storage.storage_service.StorageProvider`:
- `upload_file(file_obj, object_key, content_type)`
- `download_file(object_key)`
- `get_temporary_download_url(object_key, expires_in)`
- `delete_file(object_key)`
- `file_exists(object_key)`
- `calculate_checksum(object_key)`

## 2. Storage Tiers

1. **Public Static Files**: `frontend/static/` served directly by Nginx or CDN. Never contains sensitive records.
2. **Private Tenant Vault Documents**: Uploaded certificates, registrations, and balance sheets stored in S3 bucket `msme-private-documents` under key pattern:
   `private/organizations/{company_id}/documents/{document_id}/{filename}`
3. **Generated Documents**: Checklists, cover letters, and application summaries stored under:
   `private/organizations/{company_id}/generated/{workspace_id}/{filename}`
4. **Knowledge Base Documents**: Official government gazettes and guidelines stored in `msme-knowledge-sources`:
   `knowledge/sources/{document_id}/{filename}`

## 3. Security & Access Control

- No customer files or generated documents are stored in web roots.
- All download access is authorized per session and organization before returning presigned short-lived URLs or proxying file streams.
