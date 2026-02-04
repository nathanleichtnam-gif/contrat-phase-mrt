import streamlit as st
import pandas as pd
from fpdf import FPDF
from PIL import Image
import io

st.set_page_config(page_title="Contrat Multi-Positions ENIM", layout="wide")

class PDF(FPDF):
    def header(self):
        self.rect(10, 10, 190, 277)
        self.set_font("Arial", "B", 15)
        self.set_y(15)
        self.cell(0, 12, "CONTRAT DE PHASE D'USINAGE", 1, 1, "C")

# --- INTERFACE ---
with st.sidebar:
    st.header("📦 Informations Générales")
    nom_piece = st.text_input("Nom de la pièce", "PIÈCE_ABC")
    designation_cao = st.text_input("Désignation CAO", "ENSEMBLE_01")
    matiere = st.text_input("Matière", "S300")
    machine = st.selectbox("Machine-Outil", ["Haas Mini Mill", "Haas VF2", "Huron", "Somab", "Tour CN"])
    nb_pos = st.number_input("Nombre de positions", min_value=1, max_value=5, value=2)

positions_data = []

for i in range(int(nb_pos)):
    st.header(f"📍 Positionnement n°{i+1}")
    col_img, col_tab = st.columns([1, 2])
    with col_img:
        img = st.file_uploader(f"Croquis Pos {i+1}", type=['png', 'jpg', 'jpeg'], key=f"img_{i}")
    with col_tab:
        data = {"N° Op": [10, 20], "Désignation": ["Opération 1", "Opération 2"], "Outils": ["T1", "T2"], "ap": [2.0, 0.5], "S": [0.5, 0.0], "Vc": [180, 200], "f": [0.2, 0.1]}
        df = st.data_editor(pd.DataFrame(data), num_rows="dynamic", key=f"df_{i}", use_container_width=True)
    positions_data.append({"img": img, "df": df, "num": i+1})
    st.divider()

# --- FONCTION DE GÉNÉRATION ---
def generer_pdf_complet(nom, cao, mat, mach, positions):
    pdf = PDF()
    
    for pos in positions:
        pdf.add_page()
        pdf.set_font("Arial", "B", 9)
        pdf.set_y(30) 
        pdf.cell(95, 8, f" Piece : {nom}", 1, 0)
        pdf.cell(95, 8, f" CAO : {cao}", 1, 1)
        
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(40, 8, f" POS N : {pos['num']}", 1, 0, "L", fill=True)
        pdf.cell(75, 8, f" Matiere : {mat}", 1, 0)
        pdf.cell(75, 8, f" Machine : {mach}", 1, 1)
        
        # --- LOGIQUE DE CADRAGE IMAGE AMÉLIORÉE ---
        y_zone_image = 55
        h_zone_image = 85 # Hauteur max allouée à l'image
        
        if pos['img']:
            img_pil = Image.open(pos['img'])
            
            # On calcule le ratio pour ne pas déformer
            w_img, h_img = img_pil.size
            ratio = w_img / h_img
            
            # On fixe une largeur de 120mm par défaut
            render_w = 120
            render_h = render_w / ratio
            
            # Si la hauteur calculée dépasse la zone allouée (85mm), on réduit
            if render_h > h_zone_image:
                render_h = h_zone_image
                render_w = render_h * ratio
            
            # On centre horizontalement (Page = 210mm, donc (210 - render_w) / 2)
            x_centered = (210 - render_w) / 2
            
            img_path = f"temp_img_{pos['num']}.png"
            img_pil.save(img_path)
            pdf.image(img_path, x=x_centered, y=y_zone_image, w=render_w, h=render_h)
            
            # On place le tableau systématiquement sous la zone d'image
            pdf.set_y(y_zone_image + h_zone_image + 5)
        else:
            pdf.set_y(y_zone_image)
            pdf.cell(190, h_zone_image, f"SANS CROQUIS POS {pos['num']}", 1, 1, "C")
            pdf.ln(5)

        # --- TABLEAU ---
        pdf.set_font("Arial", "B", 7)
        widths = [10, 50, 45, 15, 25, 23, 22] 
        headers = pos['df'].columns
        pdf.set_fill_color(220, 220, 220)
        for i in range(len(headers)):
            pdf.cell(widths[i], 8, headers[i], 1, 0, "C", fill=True)
        pdf.ln()
        
        pdf.set_font("Arial", "", 7)
        for index, row in pos['df'].iterrows():
            line_height = 7
            start_y = pdf.get_y()
            for i in range(len(row)):
                valeur = str(row[i]).replace("⌀", "D.").replace("ø", "d")
                valeur_propre = valeur.encode('latin-1', 'replace').decode('latin-1')
                curr_x = pdf.get_x()
                pdf.multi_cell(widths[i], line_height, valeur_propre, border=1, align="C")
                pdf.set_xy(curr_x + widths[i], start_y)
            pdf.ln(line_height)
            
    return pdf.output()

if st.button("💾 Générer le Dossier Complet"):
    try:
        pdf_bytes = generer_pdf_complet(nom_piece, designation_cao, matiere, machine, positions_data)
        st.download_button(label="📥 Télécharger le PDF", data=bytes(pdf_bytes), file_name=f"Dossier_{nom_piece}.pdf", mime="application/pdf")
    except Exception as e:
        st.error(f"Erreur : {e}")
