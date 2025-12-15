# gpt_agent/pdf_generator.py

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from pathlib import Path

from .gpt_assistant import GPTAssistant
from .prompts import build_dashboard_analysis_prompt, build_single_chart_analysis_prompt


# Enregistrer une police Unicode-complète
try:
    # Tester différents chemins selon l'OS
    font_paths = [
        # Linux
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        # Mac
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
        '/Library/Fonts/Arial Unicode.ttf',
        # Windows
        'C:/Windows/Fonts/arial.ttf',
    ]
    
    for font_path in font_paths:
        if Path(font_path).exists():
            font_name = 'DejaVuSans' if 'DejaVu' in font_path else 'ArialUnicode'
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            DEFAULT_FONT = font_name
            DEFAULT_FONT_BOLD = font_name
            break
    else:
        # Aucune police trouvée, utiliser Helvetica
        raise FileNotFoundError
except:
    # Fallback sur Helvetica (police par défaut de reportlab, support Unicode limité)
    DEFAULT_FONT = 'Helvetica'
    DEFAULT_FONT_BOLD = 'Helvetica-Bold'


def format_text_for_pdf(text: str) -> str:
    """
    Formate le texte pour reportlab en ajoutant des balises HTML.
    Convertit les sauts de ligne en <br/> et nettoie les caractères spéciaux.
    """
    # Remplacer les doubles retours à la ligne par des paragraphes
    text = text.strip()
    
    # Nettoyer les "\n" littéraux échappés (backslash-n comme string)
    text = text.replace('\\n\\n', '\n\n')
    text = text.replace('\\n', ' ')
    
    # Nettoyer les caractères spéciaux qui ne s'affichent pas bien dans reportlab
    replacements = {
        '»': '>',
        '«': '<',
        ''': "'",
        ''': "'",
        '"': '"',
        '"': '"',
        '—': '-',
        '–': '-',
        '…': '...',
        '°': ' deg',
        '€': 'EUR',
        '≈': '~',
        '≥': '>=',
        '≤': '<=',
        '\u2022': '*',  # bullet point
        '\u2013': '-',  # en dash
        '\u2014': '-',  # em dash
        '\u2018': "'",  # left single quote
        '\u2019': "'",  # right single quote
        '\u201c': '"',  # left double quote
        '\u201d': '"',  # right double quote
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    # D'abord identifier les vrais paragraphes (double \n)
    paragraphs = text.split('\n\n')
    
    # Pour chaque paragraphe, remplacer les \n simples par des espaces
    # (ce sont juste des word wrapping, pas de vrais retours à la ligne)
    cleaned_paragraphs = []
    for para in paragraphs:
        # Remplacer les \n simples par des espaces pour éviter les coupures de mots
        para = para.replace('\n', ' ')
        # Nettoyer les espaces multiples
        para = ' '.join(para.split())
        cleaned_paragraphs.append(para)
    
    # Rejoindre les paragraphes avec <br/><br/>
    text = '<br/><br/>'.join(cleaned_paragraphs)
    
    return text


class PDFReportGenerator:
    """
    Générateur de rapports PDF avec analyses IA.
    """
    
    def __init__(self, assistant: GPTAssistant = None):
        self.assistant = assistant or GPTAssistant()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configure les styles personnalisés avec support Unicode."""
        # Style titre
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontName=DEFAULT_FONT_BOLD,
            fontSize=24,
            textColor="#0f489d",
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Style sous-titre
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontName=DEFAULT_FONT_BOLD,
            fontSize=16,
            textColor="#32597f",
            spaceBefore=20,
            spaceAfter=12
        ))
        
        # Style texte justifié
        self.styles.add(ParagraphStyle(
            name='Justified',
            parent=self.styles['BodyText'],
            fontName=DEFAULT_FONT,
            alignment=TA_JUSTIFY,
            fontSize=11,
            leading=16
        ))
        
        # Modifier le style Normal aussi
        self.styles['Normal'].fontName = DEFAULT_FONT
    
    def _generate_introduction(self, city1, city2):
        """Génère l'introduction du rapport."""
        prompt = f"""
        Rédige une introduction professionnelle pour un rapport d'analyse immobilière 
        comparant {city1} et {city2}.
        
        2-3 phrases maximum qui présentent :
        - Le contexte (analyse comparative de marché locatif)
        - Les deux villes comparées
        - L'objectif du rapport
        
        Texte fluide, pas de titre, pas de formule générique.
        """
        return self.assistant.ask(prompt)
    
    def _generate_global_analysis(self, city1, city2, stats1, stats2, weekly1, weekly2, question, dashboard_image_path):
        """Génère l'analyse globale avec l'image complète du dashboard."""
        prompt = build_dashboard_analysis_prompt(
            city1, city2, stats1, stats2, weekly1, weekly2, question
        )
        # Utiliser l'image complète du dashboard pour l'analyse globale
        return self.assistant.ask_with_image(prompt, dashboard_image_path)
    
    def _generate_chart_analysis(self, chart_name, chart_type, city1, city2, image_path, context):
        """Génère l'analyse d'un graphique spécifique."""
        prompt = build_single_chart_analysis_prompt(chart_type, city1, city2, context)
        return self.assistant.ask_with_image(prompt, image_path)
    
    def _generate_conclusion(self, city1, city2, all_analyses):
        """Génère la conclusion du rapport."""
        prompt = f"""
        Rédige une conclusion synthétique pour un rapport d'analyse immobilière 
        comparant {city1} et {city2}.
        
        Synthèse basée sur :
        {all_analyses[:2000]}...
        
        En 2 paragraphes courts :
        - Synthèse des enseignements clés
        - Recommandation finale pratique
        
        Texte fluide, pas de titre, pas de formule type "En conclusion".
        """
        return self.assistant.ask(prompt)
    
    def save_to_pdf(
        self,
        output_path: str,
        city1: str,
        city2: str,
        stats1: dict,
        stats2: dict,
        weekly1: list,
        weekly2: list,
        question: str,
        charts_data: list[dict],
        dashboard_image_path: str = None,
        progress_callback = None
    ):
        """
        Génère un rapport PDF complet avec analyses IA.
        
        Args:
            output_path: Chemin du fichier PDF à générer
            city1, city2: Noms des villes comparées
            stats1, stats2: Statistiques des villes
            weekly1, weekly2: Données hebdomadaires
            question: Question utilisateur
            charts_data: Liste de dicts avec structure:
                {
                    'name': 'Nom du graphique',
                    'type': 'scatter|temporal|map|pie|density',
                    'image_path': 'chemin/vers/image.png',
                    'context': {...}  # Contexte additionnel
                }
            dashboard_image_path: Chemin de l'image complète du dashboard (optionnel)
            progress_callback: Fonction callback(progress: int, message: str) pour le suivi
        """
        def update_progress(progress: int, message: str):
            if progress_callback:
                progress_callback(progress, message)
        
        # Créer le document
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)
        
        # Conteneur pour les éléments du PDF
        story = []
        
        # ========== PAGE DE TITRE ==========
        story.append(Spacer(1, 2*inch))
        title = Paragraph(
            f"Analyse Comparative du Marché Immobilier<br/>{city1.capitalize()} vs {city2.capitalize()}",
            self.styles['CustomTitle']
        )
        story.append(title)
        story.append(Spacer(1, 0.5*inch))
        
        date_text = Paragraph(
            f"Rapport généré le {datetime.now().strftime('%d/%m/%Y')}",
            self.styles['Normal']
        )
        story.append(date_text)
        story.append(PageBreak())
        
        # ========== INTRODUCTION ==========
        update_progress(25, "📝 Rédaction de l'introduction...")
        story.append(Paragraph("Introduction", self.styles['CustomHeading']))
        intro_text = self._generate_introduction(city1, city2)
        story.append(Paragraph(format_text_for_pdf(intro_text), self.styles['Justified']))
        story.append(Spacer(1, 0.3*inch))
        
        # ========== ANALYSE GLOBALE ==========
        update_progress(35, "🔍 Analyse globale du dashboard...")
        story.append(Paragraph("Vue d'ensemble", self.styles['CustomHeading']))
        if dashboard_image_path:
            global_analysis = self._generate_global_analysis(
                city1, city2, stats1, stats2, weekly1, weekly2, question, dashboard_image_path
            )
        else:
            # Fallback sans image si non fournie
            prompt = build_dashboard_analysis_prompt(
                city1, city2, stats1, stats2, weekly1, weekly2, question
            )
            global_analysis = self.assistant.ask(prompt)
        story.append(Paragraph(format_text_for_pdf(global_analysis), self.styles['Justified']))
        story.append(PageBreak())
        
        # ========== ANALYSES GRAPHIQUE PAR GRAPHIQUE ==========
        all_analyses = [global_analysis]
        
        for i, chart in enumerate(charts_data):
            # Progression pour chaque graphique
            progress = 45 + int((i / len(charts_data)) * 45)
            update_progress(progress, f"📊 Analyse: {chart['name']}... ({i+1}/{len(charts_data)})")
            
            # Titre du graphique
            story.append(Paragraph(
                f"{i+1}. {chart['name']}", 
                self.styles['CustomHeading']
            ))
            story.append(Spacer(1, 0.2*inch))
            
            # Image du graphique (garder le ratio d'aspect)
            if Path(chart['image_path']).exists():
                # Charger l'image pour obtenir ses dimensions réelles
                from PIL import Image as PILImage
                pil_img = PILImage.open(chart['image_path'])
                img_width, img_height = pil_img.size
                
                # Calculer le ratio d'aspect
                aspect_ratio = img_height / img_width
                
                # Définir la largeur max et calculer la hauteur en conséquence
                max_width = 5.5 * inch
                calculated_height = max_width * aspect_ratio
                
                # Limiter la hauteur max pour éviter les images trop grandes
                max_height = 4 * inch
                if calculated_height > max_height:
                    calculated_height = max_height
                    max_width = calculated_height / aspect_ratio
                
                img = Image(chart['image_path'], width=max_width, height=calculated_height)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
            
            # Analyse du graphique
            chart_analysis = self._generate_chart_analysis(
                chart['name'],
                chart['type'],
                city1,
                city2,
                chart['image_path'],
                chart.get('context', {})
            )
            story.append(Paragraph(format_text_for_pdf(chart_analysis), self.styles['Justified']))
            all_analyses.append(chart_analysis)
            
            # Saut de page sauf pour le dernier
            if i < len(charts_data) - 1:
                story.append(PageBreak())
            else:
                story.append(Spacer(1, 0.5*inch))
        
        # ========== CONCLUSION ==========
        update_progress(92, "✍️ Rédaction de la conclusion...")
        story.append(PageBreak())
        story.append(Paragraph("Conclusion", self.styles['CustomHeading']))
        conclusion_text = self._generate_conclusion(
            city1, city2, 
            "\n\n".join(all_analyses)
        )
        story.append(Paragraph(format_text_for_pdf(conclusion_text), self.styles['Justified']))
        
        # ========== GÉNÉRATION DU PDF ==========
        update_progress(97, "📄 Finalisation du PDF...")
        # ========== GÉNÉRATION DU PDF ==========
        doc.build(story)
        print(f"✅ Rapport PDF généré : {output_path}")


def generate_comparison_report(
    city1: str,
    city2: str,
    df1,
    df2,
    stats1: dict,
    stats2: dict,
    weekly1: list,
    weekly2: list,
    question: str,
    output_path: str = "imgs/rapport_comparatif.pdf",
    progress_callback = None
):
    """
    Fonction helper pour générer un rapport complet.
    
    Usage:
        generate_comparison_report(
            city1="Lyon",
            city2="Paris",
            df1=df_lyon,
            df2=df_paris,
            stats1=stats_lyon,
            stats2=stats_paris,
            weekly1=weekly_lyon,
            weekly2=weekly_paris,
            question="Quelle ville est la plus attractive?",
            output_path="rapport.pdf"
        )
    """
    # Préparer les données des graphiques
    charts_data = [
        {
            'name': 'Distribution des annonces',
            'type': 'pie',
            'image_path': 'imgs/plotly_screenshot_0.png',
            'context': {
                'count_city1': len(df1),
                'count_city2': len(df2)
            }
        },
        {
            'name': 'Prix au m² vs Surface',
            'type': 'scatter',
            'image_path': 'imgs/plotly_screenshot_1.png',
            'context': {
                'median_price_city1': stats1['median'],
                'median_price_city2': stats2['median']
            }
        },
        {
            'name': 'Évolution temporelle des prix',
            'type': 'temporal',
            'image_path': 'imgs/plotly_screenshot_2.png',
            'context': {
                'trend_city1': 'stable' if len(weekly1) > 0 else 'unknown',
                'trend_city2': 'stable' if len(weekly2) > 0 else 'unknown'
            }
        },
        {
            'name': f'Distribution géographique - {city1}',
            'type': 'map',
            'image_path': 'imgs/pydeck_screenshot_0.png',
            'context': {'city': city1}
        },
        {
            'name': f'Distribution géographique - {city2}',
            'type': 'map',
            'image_path': 'imgs/pydeck_screenshot_1.png',
            'context': {'city': city2}
        }
    ]
    
    # Générer le PDF
    generator = PDFReportGenerator()
    generator.save_to_pdf(
        output_path=output_path,
        city1=city1,
        city2=city2,
        stats1=stats1,
        stats2=stats2,
        weekly1=weekly1,
        weekly2=weekly2,
        question=question,
        charts_data=charts_data,
        dashboard_image_path="imgs/dashboard_image.png",
        progress_callback=progress_callback
    )
    
    return output_path
