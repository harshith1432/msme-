"""
Enterprise Document Generator Service.
Generates genuine, professional, downloadable PDF and DOCX artifacts for:
  - Application checklists and verification worksheets
  - Formal Government Authority Application Cover Letters
  - Statutory declarations and compliance readiness sheets
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

class DocumentGenerator:
    def __init__(self, output_dir=None):
        if not output_dir:
            if os.environ.get('VERCEL'):
                output_dir = '/tmp/generated_docs'
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                output_dir = os.environ.get('GENERATED_DOCS_DIR') or os.path.join(base_dir, 'uploads', 'generated_docs')
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError:
            pass
        self.output_dir = output_dir

    def generate_checklist_pdf(self, company_name, udyam_reg, workspace_title, checklist_items, filename=None):
        """Generates a high-fidelity PDF checklist artifact using ReportLab."""
        if not filename:
            filename = f"checklist_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            leftMargin=40,
            rightMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=16,
            leading=20,
            textColor=colors.HexColor('#0F172A'),
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#475569'),
            spaceAfter=15
        )
        body_style = ParagraphStyle(
            'DocBody',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#1E293B')
        )
        header_cell_style = ParagraphStyle(
            'HeaderCell',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            fontName='Helvetica-Bold',
            textColor=colors.white
        )

        elements = []

        # Top Header Banner
        elements.append(Paragraph("MSME NAVIGATOR INDIA — OFFICIAL APPLICATION PACKAGE", title_style))
        elements.append(Paragraph(f"Workspace / Scheme: <b>{workspace_title}</b>", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=12))

        # Company Metadata Table
        meta_data = [
            [
                Paragraph("<b>Applicant Enterprise:</b>", body_style),
                Paragraph(company_name, body_style),
                Paragraph("<b>Generated On:</b>", body_style),
                Paragraph(datetime.utcnow().strftime('%d %b %Y, %H:%M UTC'), body_style)
            ],
            [
                Paragraph("<b>Udyam Registration:</b>", body_style),
                Paragraph(udyam_reg or "Pending / Under Filing", body_style),
                Paragraph("<b>Compliance Status:</b>", body_style),
                Paragraph("Verified Package", body_style)
            ]
        ]
        meta_table = Table(meta_data, colWidths=[130, 160, 100, 120])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('PADDING', (0,0), (-1,-1), 6),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 15))

        # Checklist Items Table
        table_rows = [
            [
                Paragraph("No.", header_cell_style),
                Paragraph("Document / Requirement", header_cell_style),
                Paragraph("Verification Status", header_cell_style),
                Paragraph("Issuing Authority / Notes", header_cell_style)
            ]
        ]

        for idx, item in enumerate(checklist_items, 1):
            doc_name = item.get('name') or item.get('document_name') or item.get('title') or str(item)
            status = item.get('status', 'Required')
            notes = item.get('notes') or item.get('authority') or 'Official filing copy'
            
            status_color = '#15803D' if status.lower() in ['verified', 'attached', 'ready'] else '#D97706'
            status_p = Paragraph(f"<font color='{status_color}'><b>{status.upper()}</b></font>", body_style)

            table_rows.append([
                Paragraph(str(idx), body_style),
                Paragraph(doc_name, body_style),
                status_p,
                Paragraph(notes, body_style)
            ])

        chk_table = Table(table_rows, colWidths=[30, 230, 100, 150])
        chk_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
        ]))
        elements.append(chk_table)
        elements.append(Spacer(1, 25))

        # Sign-off Declaration
        decl_text = (
            "<b>Applicant Declaration:</b> We hereby certify that the documents listed above have been prepared "
            "in accordance with applicable statutory guidelines and Government of India notifications. "
            "All assertions are subject to verification against official portal records."
        )
        elements.append(Paragraph(decl_text, body_style))
        elements.append(Spacer(1, 30))

        # Signature Blocks
        sig_data = [
            [
                Paragraph("<b>Authorized Signatory</b><br/><br/>_______________________<br/>(Name & Stamp)", body_style),
                Paragraph("<b>Chartered Accountant / Legal Reviewer</b><br/><br/>_______________________<br/>(Membership No. / Stamp)", body_style)
            ]
        ]
        sig_table = Table(sig_data, colWidths=[250, 250])
        sig_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 0)
        ]))
        elements.append(sig_table)

        doc.build(elements)
        return filename, file_path

    def generate_cover_letter_docx(self, company_dict, scheme_title, authority_name, checklist_items, filename=None):
        """Generates a professional DOCX cover letter for official submissions."""
        if not filename:
            filename = f"cover_letter_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.docx"
        file_path = os.path.join(self.output_dir, filename)

        doc = docx.Document()

        # Set standard margins
        for section in doc.sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

        company_name = company_dict.get('name', 'Applicant Enterprise')
        udyam = company_dict.get('udyam_registration_number') or company_dict.get('udyam_number', 'Under Registration')
        state = company_dict.get('state', 'India')
        sector = company_dict.get('sector', 'Manufacturing / Services')
        turnover = company_dict.get('annual_turnover') or company_dict.get('turnover', 0)

        # Header Block
        h = doc.add_paragraph()
        h_run = h.add_run(company_name.upper())
        h_run.bold = True
        h_run.font.size = Pt(14)
        h_run.font.color.rgb = RGBColor(15, 23, 42)

        meta_p = doc.add_paragraph()
        meta_p.paragraph_format.space_after = Pt(14)
        meta_p.add_run(f"Registered Office: {state}, India | Udyam: {udyam} | Sector: {sector}\nDate: {datetime.utcnow().strftime('%d %B, %Y')}")

        doc.add_paragraph(f"To,\nThe Competent Authority / General Manager,\n{authority_name or 'District Industries Centre (DIC) / MSME Directorate'},\nGovernment of India / {state}")

        # Subject Line
        subj = doc.add_paragraph()
        subj.paragraph_format.space_before = Pt(12)
        subj.paragraph_format.space_after = Pt(12)
        s_run = subj.add_run(f"Subject: Formal Application & Submission of Documentation for {scheme_title}")
        s_run.bold = True
        s_run.underline = True

        doc.add_paragraph("Respected Sir/Madam,")

        body1 = doc.add_paragraph(
            f"We, {company_name}, are a recognized Indian Micro/Small enterprise holding Udyam Registration No. {udyam}. "
            f"Our registered operations in {state} are engaged in {sector} with an annual turnover of ₹{turnover:,.2f}."
        )
        body1.paragraph_format.space_after = Pt(10)

        body2 = doc.add_paragraph(
            f"In reference to the published guidelines for '{scheme_title}', we respectfully submit our formal claim and application package. "
            f"We confirm that our unit satisfies all statutory eligibility conditions, employer threshold criteria, and operational standards mandated under the scheme."
        )
        body2.paragraph_format.space_after = Pt(10)

        doc.add_paragraph("Please find enclosed herewith the following verified supporting documentation:")

        # Bullet List of Documents
        for idx, item in enumerate(checklist_items, 1):
            doc_name = item.get('name') or item.get('document_name') or item.get('title') or str(item)
            p = doc.add_paragraph(f"{idx}. {doc_name}", style='List Number')
            p.paragraph_format.space_after = Pt(4)

        closing = doc.add_paragraph(
            "\nWe request your esteemed office to verify the submitted particulars, accord formal approval, and release the admissible benefits/clearances at your earliest convenience. "
            "We undertake to provide any further clarifications or original records as and when requested."
        )
        closing.paragraph_format.space_before = Pt(10)
        closing.paragraph_format.space_after = Pt(24)

        doc.add_paragraph("Yours faithfully,\nFor " + company_name + "\n\n\n\n___________________________\nAuthorized Signatory\nName:\nDesignation:\nContact:\nEmail:")

        doc.save(file_path)
        return filename, file_path

document_generator = DocumentGenerator()
