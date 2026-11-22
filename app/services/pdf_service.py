import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas
from app.core.config import settings

class NumberedCanvas(canvas.Canvas):
    """Canvas personnalisé pour ajouter les numéros de page et pied de page sobre."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#71717a")) # Gris zinc sobre
        
        # En-tête (sauf page 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "AI Research Agent — Rapport d'Analyse Autonome")
            self.setStrokeColor(colors.HexColor("#27272a"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
        # Pied de page
        page_str = f"Page {self._pageNumber} sur {page_count}"
        self.drawRightString(558, 40, page_str)
        self.drawString(54, 40, f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} — Document Confidentiel")
        self.setStrokeColor(colors.HexColor("#27272a"))
        self.setLineWidth(0.5)
        self.line(54, 50, 558, 50)
        self.restoreState()


class PDFService:
    """Générateur de rapport PDF au style sombre, moderne et sans aucun émoji."""

    def __init__(self):
        settings.ensure_directories()
        self.reports_dir = settings.REPORTS_DIR

    def generate_report(self, report_data: Dict[str, Any], session_id: str) -> str:
        """Produit un rapport PDF hautement professionnel et structuré."""
        filename = f"rapport_recherche_{session_id}.pdf"
        output_path = self.reports_dir / filename
        
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=60
        )

        styles = getSampleStyleSheet()
        
        # Styles corporate sombres & sobres
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#09090b"),
            spaceAfter=12
        )
        
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#52525b"),
            spaceAfter=20
        )
        
        h1_style = ParagraphStyle(
            'ReportH1',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#09090b"),
            spaceBefore=16,
            spaceAfter=8,
            keepWithNext=True
        )
        
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#27272a"),
            spaceAfter=10
        )
        
        bullet_style = ParagraphStyle(
            'ReportBullet',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#27272a"),
            leftIndent=15,
            firstLineIndent=-10,
            spaceAfter=5
        )

        meta_label_style = ParagraphStyle(
            'MetaLabel',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#09090b")
        )

        meta_val_style = ParagraphStyle(
            'MetaValue',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#52525b")
        )

        elements = []

        # En-tête / Page de couverture légère intégrée
        elements.append(Paragraph("RAPPORT DE RECHERCHE TECHNIQUE ET STRATÉGIQUE", subtitle_style))
        title = report_data.get("title", "Rapport d'Analyse Autonome")
        elements.append(Paragraph(title, title_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#18181b"), spaceAfter=14))

        # Tableau des métadonnées
        meta_table_data = [
            [Paragraph("Date d'exécution :", meta_label_style), Paragraph(datetime.now().strftime('%d/%m/%Y %H:%M'), meta_val_style),
             Paragraph("Identifiant Session :", meta_label_style), Paragraph(session_id[:12], meta_val_style)],
            [Paragraph("Niveau de recherche :", meta_label_style), Paragraph(report_data.get("depth", "Standard").upper(), meta_val_style),
             Paragraph("Sources auditées :", meta_label_style), Paragraph(str(len(report_data.get("references", []))), meta_val_style)]
        ]
        t = Table(meta_table_data, colWidths=[110, 140, 110, 140])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f4f4f5")),
            ('PADDING', (0,0), (-1,-1), 6),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#e4e4e7")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        elements.append(t)
        elements.append(Spacer(1, 16))

        # 10 Sections obligatoires
        sections = [
            ("1. Synthèse Exécutive", report_data.get("executive_summary", "")),
            ("2. Introduction et Contexte", report_data.get("introduction", "")),
            ("3. Méthodologie de Recherche", report_data.get("research_methodology", "")),
            ("4. Résultats Détaillés", report_data.get("detailed_findings", "")),
            ("5. Analyse Comparative", report_data.get("comparative_analysis", "")),
            ("6. Avantages et Limites", report_data.get("advantages_and_limitations", "")),
            ("7. Recommandations Stratégiques", report_data.get("recommendations", "")),
            ("8. Conclusion", report_data.get("conclusion", ""))
        ]

        for sec_title, sec_content in sections:
            elements.append(Paragraph(sec_title, h1_style))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#d4d4d8"), spaceAfter=8))
            
            # Formatage du texte par paragraphes
            paragraphs = sec_content.split("\n\n")
            for p in paragraphs:
                p_clean = p.strip()
                if not p_clean:
                    continue
                if p_clean.startswith("- ") or p_clean.startswith("* "):
                    for line in p_clean.split("\n"):
                        l_clean = line.strip().lstrip("-* ").strip()
                        if l_clean:
                            elements.append(Paragraph(f"•  {l_clean}", bullet_style))
                else:
                    elements.append(Paragraph(p_clean.replace("\n", "<br/>"), body_style))
            elements.append(Spacer(1, 8))

        # 9. Références et Sources (Vérifiables et cliquables)
        elements.append(Paragraph("9. Références et Sources Documentaires", h1_style))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#d4d4d8"), spaceAfter=8))
        
        refs = report_data.get("references", [])
        if refs:
            for idx, ref in enumerate(refs, 1):
                ref_title = ref.get("title", "Source sans titre")
                ref_url = ref.get("url", "")
                link_text = f"<b>[{idx}] {ref_title}</b><br/><font color='#111111'><u><link href='{ref_url}'>{ref_url}</link></u></font>"
                elements.append(Paragraph(link_text, bullet_style))
                elements.append(Spacer(1, 3))
        else:
            elements.append(Paragraph("Aucune référence externe collectée.", body_style))

        # Construction du PDF
        doc.build(elements, canvasmaker=NumberedCanvas)
        return str(output_path)

pdf_service = PDFService()
