"""
Document Generation Service - Creates optimized resumes and cover letters
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

# PDF/DOCX generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from docxtpl import DocxTemplate
import io

from config import settings
from models.schemas import JobPosting, ResumeData

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for generating resumes and cover letters in various formats."""

    def __init__(self):
        self.output_dir = settings.generated_dir
        self.templates_dir = settings.base_dir / "data" / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    def generate_resume_pdf(
        self,
        resume_data: Dict[str, Any],
        job_posting: Optional[JobPosting] = None,
        optimizations: Optional[Dict[str, str]] = None
    ) -> bytes:
        """
        Generate an ATS-friendly resume PDF.

        Args:
            resume_data: Parsed resume data
            job_posting: Target job posting for optimization
            optimizations: Dict of section optimizations {section_name: optimized_text}

        Returns:
            PDF file as bytes
        """
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter,
                                   topMargin=0.5*inch, bottomMargin=0.5*inch,
                                   leftMargin=0.75*inch, rightMargin=0.75*inch)

            # Create story (content) list
            story = []
            styles = getSampleStyleSheet()

            # Custom styles
            name_style = ParagraphStyle(
                'CustomName',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.HexColor('#1f77b4'),
                spaceAfter=6,
                alignment=1  # Center
            )

            contact_style = ParagraphStyle(
                'ContactInfo',
                parent=styles['Normal'],
                fontSize=10,
                alignment=1,  # Center
                spaceAfter=12
            )

            heading_style = ParagraphStyle(
                'SectionHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#1f77b4'),
                spaceBefore=12,
                spaceAfter=6,
                borderWidth=0,
                borderPadding=0,
                borderColor=colors.HexColor('#1f77b4'),
                borderRadius=None
            )

            # Extract contact info
            contact = resume_data.get('contact', {})
            name = contact.get('name', 'Your Name')
            email = contact.get('email', '')
            phone = contact.get('phone', '')
            location = contact.get('location', '')
            linkedin = contact.get('linkedin', '')

            # Name
            story.append(Paragraph(name, name_style))

            # Contact info line
            contact_parts = []
            if email:
                contact_parts.append(email)
            if phone:
                contact_parts.append(phone)
            if location:
                contact_parts.append(location)
            if linkedin:
                contact_parts.append(f"LinkedIn: {linkedin}")

            if contact_parts:
                story.append(Paragraph(" | ".join(contact_parts), contact_style))

            # Professional Summary
            summary = optimizations.get('summary') if optimizations else None
            summary = summary or resume_data.get('summary', '')
            if summary:
                story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
                story.append(Paragraph(summary, styles['Normal']))
                story.append(Spacer(1, 0.2*inch))

            # Skills
            skills = resume_data.get('skills', [])
            if skills:
                story.append(Paragraph("SKILLS", heading_style))
                skills_text = " • ".join(skills[:15])  # Limit to 15 skills for ATS
                story.append(Paragraph(skills_text, styles['Normal']))
                story.append(Spacer(1, 0.2*inch))

            # Experience
            experience = resume_data.get('experience', [])
            if experience:
                story.append(Paragraph("PROFESSIONAL EXPERIENCE", heading_style))

                for exp in experience:
                    # Company and title
                    title_text = f"<b>{exp.get('title', '')}</b> | {exp.get('company', '')}"
                    story.append(Paragraph(title_text, styles['Normal']))

                    # Dates and location
                    dates = exp.get('dates', '')
                    location_exp = exp.get('location', '')
                    date_loc = f"{dates}" + (f" | {location_exp}" if location_exp else "")
                    story.append(Paragraph(date_loc, styles['Normal']))

                    # Bullets (use optimized if available)
                    bullets = exp.get('bullets', [])
                    for bullet in bullets:
                        bullet_text = f"• {bullet}"
                        story.append(Paragraph(bullet_text, styles['Normal']))

                    story.append(Spacer(1, 0.15*inch))

            # Education
            education = resume_data.get('education', [])
            if education:
                story.append(Paragraph("EDUCATION", heading_style))

                for edu in education:
                    degree = edu.get('degree', '')
                    institution = edu.get('institution', '')
                    dates = edu.get('dates', '')

                    edu_text = f"<b>{degree}</b> | {institution} | {dates}"
                    story.append(Paragraph(edu_text, styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))

            # Certifications
            certifications = resume_data.get('certifications', [])
            if certifications:
                story.append(Paragraph("CERTIFICATIONS", heading_style))

                for cert in certifications:
                    cert_name = cert.get('name', '')
                    issuer = cert.get('issuer', '')
                    date_cert = cert.get('date', '')

                    cert_text = f"• {cert_name} - {issuer}" + (f" ({date_cert})" if date_cert else "")
                    story.append(Paragraph(cert_text, styles['Normal']))

            # Build PDF
            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()

            logger.info("Resume PDF generated successfully")
            return pdf_bytes

        except Exception as e:
            logger.error(f"Error generating resume PDF: {str(e)}")
            raise

    def generate_cover_letter_pdf(
        self,
        resume_data: Dict[str, Any],
        job_posting: JobPosting,
        content: str
    ) -> bytes:
        """
        Generate a professional cover letter PDF.

        Args:
            resume_data: Parsed resume data
            job_posting: Target job posting
            content: Cover letter body content (generated by LLM)

        Returns:
            PDF file as bytes
        """
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter,
                                   topMargin=1*inch, bottomMargin=1*inch,
                                   leftMargin=1*inch, rightMargin=1*inch)

            story = []
            styles = getSampleStyleSheet()

            # Custom styles
            header_style = ParagraphStyle(
                'Header',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=12
            )

            body_style = ParagraphStyle(
                'Body',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=12,
                leading=14
            )

            # Extract contact info
            contact = resume_data.get('contact', {})
            name = contact.get('name', 'Your Name')
            email = contact.get('email', '')
            phone = contact.get('phone', '')
            location = contact.get('location', '')

            # Sender info (header)
            story.append(Paragraph(name, header_style))
            if email:
                story.append(Paragraph(email, header_style))
            if phone:
                story.append(Paragraph(phone, header_style))
            if location:
                story.append(Paragraph(location, header_style))

            story.append(Spacer(1, 0.3*inch))

            # Date
            today = datetime.now().strftime("%B %d, %Y")
            story.append(Paragraph(today, header_style))
            story.append(Spacer(1, 0.2*inch))

            # Recipient info
            story.append(Paragraph(f"Hiring Manager", header_style))
            story.append(Paragraph(job_posting.company, header_style))
            story.append(Spacer(1, 0.3*inch))

            # Subject line
            subject = f"Re: Application for {job_posting.title}"
            story.append(Paragraph(f"<b>{subject}</b>", header_style))
            story.append(Spacer(1, 0.2*inch))

            # Body paragraphs
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), body_style))

            # Closing
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("Sincerely,", body_style))
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph(name, body_style))

            # Build PDF
            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()

            logger.info("Cover letter PDF generated successfully")
            return pdf_bytes

        except Exception as e:
            logger.error(f"Error generating cover letter PDF: {str(e)}")
            raise

    def save_document(
        self,
        file_bytes: bytes,
        job_id: str,
        doc_type: str,  # 'resume' or 'cover_letter'
        file_format: str = 'pdf'
    ) -> str:
        """
        Save generated document to disk.

        Args:
            file_bytes: Document bytes
            job_id: Associated job ID
            doc_type: 'resume' or 'cover_letter'
            file_format: File extension ('pdf' or 'docx')

        Returns:
            Path to saved file
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{doc_type}_{job_id[:8]}_{timestamp}.{file_format}"
            file_path = self.output_dir / filename

            with open(file_path, 'wb') as f:
                f.write(file_bytes)

            logger.info(f"Document saved: {file_path}")
            return str(file_path)

        except Exception as e:
            logger.error(f"Error saving document: {str(e)}")
            raise

    def generate_resume_docx(
        self,
        resume_data: Dict[str, Any],
        job_posting: Optional[JobPosting] = None,
        optimizations: Optional[Dict[str, str]] = None
    ) -> bytes:
        """
        Generate resume as DOCX using template (if template exists).

        Args:
            resume_data: Parsed resume data
            job_posting: Target job posting
            optimizations: Section optimizations

        Returns:
            DOCX file as bytes
        """
        try:
            # Check if template exists
            template_path = self.templates_dir / "resume_template.docx"

            if not template_path.exists():
                logger.warning("Template not found, creating simple DOCX")
                # TODO: Create simple DOCX without template
                # For now, just convert PDF to note that template is missing
                raise FileNotFoundError("Resume template not found. Please create data/templates/resume_template.docx")

            # Load template
            doc = DocxTemplate(template_path)

            # Prepare context for template
            context = {
                'name': resume_data.get('contact', {}).get('name', ''),
                'email': resume_data.get('contact', {}).get('email', ''),
                'phone': resume_data.get('contact', {}).get('phone', ''),
                'location': resume_data.get('contact', {}).get('location', ''),
                'linkedin': resume_data.get('contact', {}).get('linkedin', ''),
                'summary': optimizations.get('summary') if optimizations else resume_data.get('summary', ''),
                'skills': resume_data.get('skills', []),
                'experience': resume_data.get('experience', []),
                'education': resume_data.get('education', []),
                'certifications': resume_data.get('certifications', [])
            }

            # Render template
            doc.render(context)

            # Save to bytes
            buffer = io.BytesIO()
            doc.save(buffer)
            docx_bytes = buffer.getvalue()
            buffer.close()

            logger.info("Resume DOCX generated successfully")
            return docx_bytes

        except FileNotFoundError:
            logger.warning("Template not found, falling back to PDF")
            # Return PDF instead
            return self.generate_resume_pdf(resume_data, job_posting, optimizations)
        except Exception as e:
            logger.error(f"Error generating resume DOCX: {str(e)}")
            raise


# Global service instance
document_service = DocumentService()
