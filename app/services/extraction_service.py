"""
Paperwork Agent - OCR & Text Extraction Service.
Extracts document text, identifies candidate business profile fields with source location,
and stages them in ExtractedField models for mandatory user confirmation before updating
authoritative Company records.
"""
import os
import re
from datetime import datetime, date
from app.extensions import db
from app.models import Document, DocumentExtraction, ExtractedField, Company, CompanyMetric, AuditEvent

class ExtractionService:
    def __init__(self):
        # Established Indian statutory regex patterns
        self.patterns = {
            'udyam_number': re.compile(r'UDYAM-[A-Z]{2}-\d{2}-\d{7}', re.IGNORECASE),
            'pan_number': re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'),
            'gstin': re.compile(r'\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}\b'),
            'turnover': re.compile(r'(?:turnover|gross revenue|sales|receipts)[:\s]+(?:₹|rs\.?|inr)?\s*([\d,]+(?:\.\d+)?)\s*(lakh|lac|crore|cr)?', re.IGNORECASE),
            'investment': re.compile(r'(?:investment in plant & machinery|plant & machinery|equipment investment|capital investment)[:\s]+(?:₹|rs\.?|inr)?\s*([\d,]+(?:\.\d+)?)\s*(lakh|lac|crore|cr)?', re.IGNORECASE),
            'employees': re.compile(r'(?:employees|headcount|workers|staff count|total persons employed)[:\s]+(\d+)', re.IGNORECASE),
            'date': re.compile(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b'),
            'entity_type': re.compile(r'\b(Private Limited|Pvt Ltd|Limited Liability Partnership|LLP|Partnership|Sole Proprietorship|Public Limited)\b', re.IGNORECASE)
        }

    def extract_text_from_file(self, file_path):
        """
        Extracts raw text and per-page content from supported file formats.
        """
        if not os.path.exists(file_path):
            return "File not found.", []

        ext = file_path.rsplit('.', 1)[-1].lower()
        pages = []
        full_text = ""

        try:
            if ext == 'pdf':
                try:
                    import pypdf
                    reader = pypdf.PdfReader(file_path)
                    for i, page in enumerate(reader.pages):
                        txt = page.extract_text() or ""
                        pages.append((f"Page {i+1}", txt))
                    full_text = "\n\n".join([f"--- {p[0]} ---\n{p[1]}" for p in pages])
                except Exception as e:
                    full_text = f"[PDF Extraction Note: {str(e)}]"
                    pages.append(("Page 1", full_text))

            elif ext == 'docx':
                try:
                    import docx
                    doc = docx.Document(file_path)
                    lines = [p.text for p in doc.paragraphs if p.text.strip()]
                    full_text = "\n".join(lines)
                    pages.append(("Document Body", full_text))
                except Exception as e:
                    full_text = f"[DOCX Extraction Note: {str(e)}]"
                    pages.append(("Document Body", full_text))

            elif ext == 'xlsx':
                try:
                    import openpyxl
                    wb = openpyxl.load_workbook(file_path, data_only=True)
                    rows_text = []
                    for sheet in wb.sheetnames:
                        ws = wb[sheet]
                        for row in ws.iter_rows(values_only=True):
                            row_vals = [str(c) for c in row if c is not None]
                            if row_vals:
                                rows_text.append(" | ".join(row_vals))
                    full_text = "\n".join(rows_text)
                    pages.append(("Workbook", full_text))
                except Exception as e:
                    full_text = f"[Excel Extraction Note: {str(e)}]"
                    pages.append(("Workbook", full_text))

            else:
                # Text or CSV
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        full_text = f.read()
                        pages.append(("File Content", full_text))
                except Exception as e:
                    full_text = f"[File Read Note: {str(e)}]"
                    pages.append(("File Content", full_text))

        except Exception as e:
            full_text = f"Extraction error: {str(e)}"
            pages.append(("Error", full_text))

        return full_text, pages

    def parse_candidate_fields(self, full_text, pages):
        """
        Parses text for key business profile fields with page location and confidence indicator.
        """
        candidates = []

        # 1. Udyam Registration
        udyam_match = self.patterns['udyam_number'].search(full_text)
        if udyam_match:
            loc = self._find_location(udyam_match.group(0), pages)
            candidates.append({
                'field_name': 'udyam_number',
                'proposed_value': udyam_match.group(0).upper(),
                'confidence': 'high',
                'source_location': loc
            })

        # 2. PAN Number
        pan_match = self.patterns['pan_number'].search(full_text)
        if pan_match:
            loc = self._find_location(pan_match.group(0), pages)
            candidates.append({
                'field_name': 'pan_number',
                'proposed_value': pan_match.group(0).upper(),
                'confidence': 'high',
                'source_location': loc
            })

        # 3. GSTIN
        gstin_match = self.patterns['gstin'].search(full_text)
        if gstin_match:
            loc = self._find_location(gstin_match.group(0), pages)
            candidates.append({
                'field_name': 'gstin',
                'proposed_value': gstin_match.group(0).upper(),
                'confidence': 'high',
                'source_location': loc
            })

        # 4. Turnover
        turnover_match = self.patterns['turnover'].search(full_text)
        if turnover_match:
            val_str = turnover_match.group(1).replace(',', '')
            multiplier = 1.0
            unit = (turnover_match.group(2) or '').lower()
            if 'crore' in unit or 'cr' in unit:
                multiplier = 10000000.0
            elif 'lakh' in unit or 'lac' in unit:
                multiplier = 100000.0

            try:
                turnover_val = float(val_str) * multiplier
                loc = self._find_location(turnover_match.group(0), pages)
                candidates.append({
                    'field_name': 'turnover',
                    'proposed_value': str(turnover_val),
                    'confidence': 'medium',
                    'source_location': loc
                })
            except ValueError:
                pass

        # 5. Investment
        invest_match = self.patterns['investment'].search(full_text)
        if invest_match:
            val_str = invest_match.group(1).replace(',', '')
            multiplier = 1.0
            unit = (invest_match.group(2) or '').lower()
            if 'crore' in unit or 'cr' in unit:
                multiplier = 10000000.0
            elif 'lakh' in unit or 'lac' in unit:
                multiplier = 100000.0

            try:
                invest_val = float(val_str) * multiplier
                loc = self._find_location(invest_match.group(0), pages)
                candidates.append({
                    'field_name': 'investment',
                    'proposed_value': str(invest_val),
                    'confidence': 'medium',
                    'source_location': loc
                })
            except ValueError:
                pass

        # 6. Employees
        emp_match = self.patterns['employees'].search(full_text)
        if emp_match:
            loc = self._find_location(emp_match.group(0), pages)
            candidates.append({
                'field_name': 'employees',
                'proposed_value': emp_match.group(1),
                'confidence': 'medium',
                'source_location': loc
            })

        # 7. Entity Type
        entity_match = self.patterns['entity_type'].search(full_text)
        if entity_match:
            loc = self._find_location(entity_match.group(0), pages)
            candidates.append({
                'field_name': 'entity_type',
                'proposed_value': entity_match.group(0),
                'confidence': 'medium',
                'source_location': loc
            })

        # 8. Date of Incorporation candidate
        date_match = self.patterns['date'].search(full_text)
        if date_match and ('incorporation' in full_text.lower() or 'registered on' in full_text.lower() or 'date:' in full_text.lower()):
            loc = self._find_location(date_match.group(0), pages)
            candidates.append({
                'field_name': 'incorporation_date',
                'proposed_value': date_match.group(0),
                'confidence': 'needs_review',
                'source_location': loc
            })

        return candidates

    def _find_location(self, needle, pages):
        for page_name, text in pages:
            if needle.lower() in text.lower():
                return page_name
        return "Document Body"

    def process_document(self, document_id):
        """
        Executes text extraction and candidate field staging for a given document.
        Does NOT update Company profile until user confirms.
        """
        doc = Document.query.get(document_id)
        if not doc:
            return None, "Document not found"

        doc.status = 'processing'
        db.session.commit()

        full_text, pages = self.extract_text_from_file(doc.file_path)
        candidates = self.parse_candidate_fields(full_text, pages)

        extraction = DocumentExtraction(
            document_id=doc.id,
            status='processed',
            raw_text=full_text[:10000],  # store first 10k chars to prevent database bloat
            extraction_method='ocr_heuristic_v1'
        )
        db.session.add(extraction)
        db.session.flush()

        for c in candidates:
            ef = ExtractedField(
                extraction_id=extraction.id,
                field_name=c['field_name'],
                proposed_value=c['proposed_value'],
                confidence=c['confidence'],
                source_location=c['source_location'],
                status='needs_review'
            )
            db.session.add(ef)

        doc.status = 'ready'
        db.session.commit()

        return extraction, None

    def confirm_extracted_fields(self, extraction_id, field_actions, user_id=None):
        """
        Explicit Human Confirmation Gate:
        Accepts dict { field_id: {'action': 'confirm'|'reject', 'corrected_value': '...'} }
        Updates the authoritative Company profile and metrics ONLY for confirmed fields.
        """
        extraction = DocumentExtraction.query.get(extraction_id)
        if not extraction:
            return False, "Extraction not found"

        doc = extraction.document
        company = doc.company
        confirmed_count = 0

        for field in extraction.fields:
            str_id = str(field.id)
            if str_id in field_actions:
                fa = field_actions[str_id]
                action = fa.get('action')
                corrected_val = fa.get('corrected_value')

                if action == 'confirm':
                    field.status = 'confirmed'
                    field.corrected_value = corrected_val or field.proposed_value
                    field.confirmed_at = datetime.utcnow()
                    effective_val = field.corrected_value

                    # Apply to company profile
                    if field.field_name == 'udyam_number':
                        company.udyam_number = effective_val
                    elif field.field_name == 'pan_number':
                        company.pan_number = effective_val
                    elif field.field_name == 'gstin':
                        company.gstin = effective_val
                    elif field.field_name == 'entity_type':
                        company.entity_type = effective_val
                    elif field.field_name == 'turnover':
                        try:
                            fval = float(effective_val)
                            db.session.add(CompanyMetric(company_id=company.id, metric_type='turnover', value=fval, provenance='extracted_confirmed'))
                        except ValueError:
                            pass
                    elif field.field_name == 'investment':
                        try:
                            fval = float(effective_val)
                            db.session.add(CompanyMetric(company_id=company.id, metric_type='investment', value=fval, provenance='extracted_confirmed'))
                        except ValueError:
                            pass
                    elif field.field_name == 'employees':
                        try:
                            ival = int(float(effective_val))
                            db.session.add(CompanyMetric(company_id=company.id, metric_type='employees', value=float(ival), provenance='extracted_confirmed'))
                        except ValueError:
                            pass
                    elif field.field_name == 'incorporation_date':
                        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
                            try:
                                company.incorporation_date = datetime.strptime(effective_val, fmt).date()
                                break
                            except ValueError:
                                pass

                    confirmed_count += 1

                elif action == 'reject':
                    field.status = 'rejected'
                    field.confirmed_at = datetime.utcnow()

        extraction.status = 'confirmed'
        doc.verification_status = 'verified'

        # Record audit event
        db.session.add(AuditEvent(
            tenant_id=company.tenant_id,
            user_id=user_id,
            action='fields_confirmed',
            entity_type='DocumentExtraction',
            entity_id=str(extraction.id),
            details=f"User confirmed {confirmed_count} fields from document '{doc.title}'"
        ))

        db.session.commit()
        return True, f"Successfully confirmed {confirmed_count} fields"
