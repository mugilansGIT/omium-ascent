"""
PDF generation utility using reportlab.
Install: pip install reportlab
"""
import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def generate_pdf_report(title: str, content: dict) -> bytes:
    """Generate a simple PDF report and return as bytes."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph(title, styles["Title"]))
        story.append(Spacer(1, 0.5 * cm))

        # Content sections
        for section, data in content.items():
            story.append(Paragraph(section.replace("_", " ").title(), styles["Heading2"]))
            story.append(Spacer(1, 0.2 * cm))

            if isinstance(data, list):
                for item in data:
                    story.append(Paragraph(f"• {item}", styles["Normal"]))
            elif isinstance(data, dict):
                for k, v in data.items():
                    story.append(Paragraph(f"<b>{k}:</b> {v}", styles["Normal"]))
            else:
                story.append(Paragraph(str(data), styles["Normal"]))

            story.append(Spacer(1, 0.3 * cm))

        doc.build(story)
        return buffer.getvalue()

    except ImportError:
        logger.error("reportlab not installed. Run: pip install reportlab")
        raise
