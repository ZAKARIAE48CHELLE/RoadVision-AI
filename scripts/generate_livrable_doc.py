"""
Generate a professional Word document (.docx) and PDF for the Data Audit deliverable.
Embeds metadata tables, statistical analysis, and figures from results/figures.
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_audit_document(output_docx="Livrable/RDD2022_Data_Audit_Report.docx"):
    doc = Document()
    
    # Page setup - Margins (1 inch)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        
    # Styles
    styles = doc.styles
    normal_style = styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(44, 62, 80)
    
    # -----------------------------
    # Title Block
    # -----------------------------
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(4)
    title_run = title_p.add_run("RoadVision AI — Rapport d'Audit des Données")
    title_run.font.size = Pt(22)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(26, 82, 118) # Deep navy/blue
    
    subtitle_p = doc.add_paragraph()
    subtitle_p.paragraph_format.space_after = Pt(16)
    sub_run = subtitle_p.add_run("Analyse Exploratoire, Intégrité et Caractérisation Géométrique du Corpus RDD2022 (United States)")
    sub_run.font.size = Pt(12)
    sub_run.font.italic = True
    sub_run.font.color.rgb = RGBColor(127, 140, 141)
    
    # Meta Info Table
    info_table = doc.add_table(rows=4, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Projet :", "RoadVision AI — Intelligent Road Damage Detection & Mapping"),
        ("Module :", "Vision par Ordinateur & Deep Learning (EMSI 5ème année)"),
        ("Corpus analysé :", "RDD2022 (Crowdsensing-based Road Damage Detection Challenge) — United States subset"),
        ("Date d'audit :", "Octobre 2026 — Phase 1 & 2 (Audit et Préparation)")
    ]
    for idx, (label, val) in enumerate(meta_data):
        row = info_table.rows[idx]
        cell_lbl, cell_val = row.cells[0], row.cells[1]
        
        p0 = cell_lbl.paragraphs[0]
        r0 = p0.add_run(label)
        r0.bold = True
        r0.font.size = Pt(10)
        r0.font.color.rgb = RGBColor(41, 128, 185)
        
        p1 = cell_val.paragraphs[0]
        r1 = p1.add_run(val)
        r1.font.size = Pt(10)
        
        cell_lbl.width = Inches(1.8)
        cell_val.width = Inches(5.0)
        set_cell_background(cell_lbl, "F8F9FA")
        set_cell_background(cell_val, "FFFFFF")
        set_cell_margins(cell_lbl, top=60, bottom=60, left=100, right=100)
        set_cell_margins(cell_val, top=60, bottom=60, left=100, right=100)
        
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # -----------------------------
    # 1. Synthèse globale
    # -----------------------------
    h1 = doc.add_heading("1. Synthèse Globale et Intégrité du Corpus", level=1)
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(6)
    
    p = doc.add_paragraph(
        "Dans le cadre du pipeline expérimental de RoadVision AI, le sous-ensemble RDD2022_United_States a été intégralement extrait "
        "et vérifié. Ce corpus standardisé permet d'entraîner et d'évaluer les architectures de détection d'objets (YOLO et RT-DETR) "
        "sur des images réelles de dégradations de chaussées capturées par caméras embarquées."
    )
    p.paragraph_format.space_after = Pt(8)
    
    # Table 1: Synthèse des volumes
    summary_table = doc.add_table(rows=5, cols=3)
    summary_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Composante", "Volume / Valeur", "Commentaire & Vérification"]
    for c_idx, h_text in enumerate(headers):
        cell = summary_table.rows[0].cells[c_idx]
        p = cell.paragraphs[0]
        r = p.add_run(h_text)
        r.bold = True
        r.font.size = Pt(10.5)
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "2C3E50")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        
    rows_data = [
        ("Images d'entraînement annotées", "4 805 images", "100% exploitables, zéro fichier corrompu"),
        ("Annotations XML (PASCAL VOC)", "4 805 fichiers", "Appariement bijectif parfait (zéro orphelin)"),
        ("Images de test (Challenge)", "1 200 images", "Images brutes sans vérité terrain transmise"),
        ("Résolution d'image standard", "640 × 640 × 3 (RGB)", "Homogénéité dimensionnelle absolue (100%)")
    ]
    for r_idx, row_values in enumerate(rows_data):
        row = summary_table.rows[r_idx + 1]
        bg = "F8F9FA" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_values):
            cell = row.cells[c_idx]
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(10)
            if c_idx == 0:
                r.bold = True
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=70, bottom=70, left=100, right=100)
            
    summary_table.columns[0].width = Inches(2.6)
    summary_table.columns[1].width = Inches(1.8)
    summary_table.columns[2].width = Inches(2.4)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # -----------------------------
    # 2. Distribution des Classes
    # -----------------------------
    h2 = doc.add_heading("2. Distribution et Analyse du Déséquilibre des Classes", level=1)
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    
    p2 = doc.add_paragraph(
        "L'analyse exhaustive des 4 805 fichiers XML a permis d'isoler un total de 11 014 boîtes englobantes "
        "réparties sur les 4 catégories officielles retenues pour la compétition CRDDC'2022 :"
    )
    p2.paragraph_format.space_after = Pt(8)
    
    # Table 2: Classes
    class_table = doc.add_table(rows=6, cols=5)
    class_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_headers = ["Code", "Classe Sémantique", "Instances", "Proportion", "Impact / Criticité"]
    for c_idx, h_text in enumerate(c_headers):
        cell = class_table.rows[0].cells[c_idx]
        p = cell.paragraphs[0]
        r = p.add_run(h_text)
        r.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "16A085") # Teal / Emerald
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
        
    class_rows = [
        ("D00", "Fissure longitudinale (Longitudinal Crack)", "6 750", "61.29%", "Classe dominante, orientation verticale"),
        ("D10", "Fissure transversale (Transverse Crack)", "3 295", "29.92%", "Orientation perpendiculaire au roulage"),
        ("D20", "Fissuration en réseau (Alligator Crack)", "834", "7.57%", "Zone polygonale complexe (faïençage)"),
        ("D40", "Nid-de-poule (Pothole)", "135", "1.23%", "Rare mais danger immédiat pour les usagers"),
        ("TOTAL", "Ensemble des dégradations", "11 014", "100.0%", "Moyenne de 2.29 dégradations par image")
    ]
    for r_idx, row_values in enumerate(class_rows):
        row = class_table.rows[r_idx + 1]
        is_total = (r_idx == len(class_rows) - 1)
        bg = "EAFAF1" if is_total else ("F8F9FA" if r_idx % 2 == 1 else "FFFFFF")
        for c_idx, val in enumerate(row_values):
            cell = row.cells[c_idx]
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(9.5)
            if is_total or c_idx in (0, 2):
                r.bold = True
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=65, bottom=65, left=70, right=70)
            
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    
    # Embed Figure 1: Class Distribution
    fig1_path = "results/figures/classes_distribution.png"
    if os.path.exists(fig1_path):
        p_img1 = doc.add_paragraph()
        p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img1.paragraph_format.space_after = Pt(4)
        run_img1 = p_img1.add_run()
        run_img1.add_picture(fig1_path, width=Inches(5.5))
        
        cap1 = doc.add_paragraph()
        cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap1.paragraph_format.space_after = Pt(14)
        r_cap1 = cap1.add_run("Figure 1 : Distribution des instances de dégradations annotées dans RDD2022 (USA Train).")
        r_cap1.font.size = Pt(9.5)
        r_cap1.font.italic = True
        r_cap1.font.color.rgb = RGBColor(127, 140, 141)

    # -----------------------------
    # 3. Analyse Géométrique & Échelles
    # -----------------------------
    h3 = doc.add_heading("3. Analyse Géométrique et Échelles des Boîtes (Norme COCO)", level=1)
    h3.paragraph_format.space_before = Pt(14)
    h3.paragraph_format.space_after = Pt(6)
    
    p3 = doc.add_paragraph(
        "Selon les critères standards du benchmark COCO basés sur l'aire de la boîte englobante :\n"
        "• Small (surface < 32² = 1024 px²) : 515 boîtes (4.68%)\n"
        "• Medium (1024 px² ≤ surface ≤ 9216 px²) : 5 967 boîtes (54.18%)\n"
        "• Large (surface > 9216 px²) : 4 532 boîtes (41.15%)\n\n"
        "Contrairement aux objets usuels (piétons, panneaux), les fissures routières couvrent de larges portions de la chaussée. "
        "Les fissures longitudinales (D00) s'étirent le long de l'axe vertical, tandis que les fissures transversales (D10) "
        "s'étirent horizontalement. Ce constat géométrique impose de restreindre les rotations de 90° dans les augmentations afin "
        "de ne pas brouiller la frontière sémantique entre D00 et D10."
    )
    p3.paragraph_format.space_after = Pt(10)
    
    # Embed Figure 2: Box Geometry Distribution
    fig2_path = "results/figures/box_geometry_distribution.png"
    if os.path.exists(fig2_path):
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.paragraph_format.space_after = Pt(4)
        run_img2 = p_img2.add_run()
        run_img2.add_picture(fig2_path, width=Inches(6.0))
        
        cap2 = doc.add_paragraph()
        cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap2.paragraph_format.space_after = Pt(14)
        r_cap2 = cap2.add_run("Figure 2 : Répartition des tailles de boîtes selon la norme COCO et surface relative par classe.")
        r_cap2.font.size = Pt(9.5)
        r_cap2.font.italic = True
        r_cap2.font.color.rgb = RGBColor(127, 140, 141)

    # -----------------------------
    # 4. Exemples Annotés de Vérité Terrain
    # -----------------------------
    h4 = doc.add_heading("4. Visualisation d'Échantillons Annotés (Vérité Terrain)", level=1)
    h4.paragraph_format.space_before = Pt(14)
    h4.paragraph_format.space_after = Pt(6)
    
    p4 = doc.add_paragraph(
        "Afin d'auditer la cohérence visuelle des annotations, des cas représentatifs de chaque catégorie ont été extraits "
        "et projetés avec leur boîte et identifiant de classe officiel (D00 en bleu, D10 en vert, D20 en jaune, D40 en rouge) :"
    )
    p4.paragraph_format.space_after = Pt(8)
    
    # Embed Figure 3: Annotated samples
    fig3_path = "results/figures/annotated_samples.png"
    if os.path.exists(fig3_path):
        p_img3 = doc.add_paragraph()
        p_img3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img3.paragraph_format.space_after = Pt(4)
        run_img3 = p_img3.add_run()
        run_img3.add_picture(fig3_path, width=Inches(6.2))
        
        cap3 = doc.add_paragraph()
        cap3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap3.paragraph_format.space_after = Pt(14)
        r_cap3 = cap3.add_run("Figure 3 : Échantillons réels de vérité terrain (RDD2022) démontrant la variété des dégradations et des fonds routiers.")
        r_cap3.font.size = Pt(9.5)
        r_cap3.font.italic = True
        r_cap3.font.color.rgb = RGBColor(127, 140, 141)

    # -----------------------------
    # 5. Recommandations Méthodologiques
    # -----------------------------
    h5 = doc.add_heading("5. Recommandations pour le Pipeline d'Apprentissage", level=1)
    h5.paragraph_format.space_before = Pt(14)
    h5.paragraph_format.space_after = Pt(6)
    
    recoms = [
        ("Stratification sans fuite (Zero Data Leakage) :", "Effectuer un partitionnement Train (70%), Validation (15%), Test (15%) en isolant strictement le jeu de test de tout réglage d'hyperparamètres."),
        ("Gestion du déséquilibre de classe :", "Accorder un bonus métrique ou une pondération de perte spécifique à la classe D40 (nids-de-poule, 1.23%), critique pour la sécurité routière."),
        ("Politique d'augmentation ciblée :", "Privilégier la mosaïque, les variations de luminosité et de contraste (HSV), tout en évitant les rotations à 90° qui inverseraient sémantiquement les fissures longitudinales (D00) et transversales (D10).")
    ]
    for r_title, r_desc in recoms:
        p_rec = doc.add_paragraph()
        p_rec.paragraph_format.space_after = Pt(4)
        p_rec.paragraph_format.left_indent = Inches(0.2)
        r_t = p_rec.add_run(f"• {r_title} ")
        r_t.bold = True
        r_t.font.color.rgb = RGBColor(41, 128, 185)
        r_d = p_rec.add_run(r_desc)
        
    doc.save(output_docx)
    print(f"Document saved successfully: {output_docx}")

if __name__ == "__main__":
    create_audit_document()
