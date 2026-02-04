import streamlit as st
import pandas as pd
from fpdf import FPDF
from PIL import Image
import io

st.set_page_config(page_title="Contrat Multi-Positions ENIM", layout="wide")

# --- CLASSE PDF ---
class PDF(FPDF):
    def header(self):
        # Cadre et Titre sur chaque page
        self.rect(10, 10, 190, 277)
        self.set_font("Arial", "B", 15)
        self.cell(0, 12, "CONTRAT DE PHASE D'USINAGE", 1, 1, "C")
        self.ln(5)

# --- INTERFACE ---
with st.sidebar:
    st.header("📦 Informations Générales")
    nom_piece = st.text_input("Nom de la pièce", "PIÈCE_ABC")
    designation_cao = st.text_input("Désignation CAO", "ENSEMBLE_01")
    matiere = st.text_input("Matière", "S300")
    machine = st.selectbox("Machine-Outil", ["Haas Mini Mill", "Haas VF2", "Huron", "Somab", "Tour CN"])
    
    st.divider()
    # Nombre de positions dynamique
    nb_pos = st.number_input("Nombre de positions à créer", min_value=1, max_value=5, value=2)

# Stockage des données de chaque position
positions_data = []

for i in range(int(nb_pos)):
    st.header(f"📍 Positionnement n°{i+1}")
    col_img, col_tab = st.columns([1, 2])
    
    with col_img:
        img = st.file_uploader(f"Croquis Pos {i+1}", type=['png', 'jpg', 'jpeg'], key=f"img_{i}")
    
    with col_tab:
        data = {
            "N° Op": [10, 20],
            "Désignation": ["Opération 1", "Opération 2"],
            "Outils": ["T1", "T2"],
            "ap": [2.0, 0.5],
            "S": [0.5, 0.0],
            "Vc": [180, 200],
            "f": [0.2, 0.1]
        }
        df = st.data_editor(pd.DataFrame(data), num_rows="dynamic", key=f"df_{i}", use_container_width=True)
    
    positions_data.append({"img": img, "df": df, "num": i+1})
    st.divider()

# --- GÉNÉRATION PDF MULTI-PAGES ---
def generer_pdf_complet(nom, cao, mat, mach, positions):
    pdf = PDF()
    
    for pos in positions:
        pdf.add_page()
        pdf.set_font("Arial", "B", 9)
        
        # Entête (Répété sur chaque page)
        pdf.cell(95, 8, f" Piece : {nom}", 1, 0)
        pdf.cell(95, 8, f" CAO : {cao}", 1, 1)
        
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(40, 8, f" POS N : {pos['num']}", 1, 0, "L", fill=True)
        pdf.cell(75, 8, f" Matiere : {mat}", 1, 0)
        pdf.cell(75, 8, f" Machine : {mach}", 1, 1)
        
        # Espace Croquis (Plus grand car une seule pos par page)
        pdf.ln(5)
        if pos['img']:
            img_pil = Image.open(pos['img'])
            img_path = f"temp_img_{pos['num']}.png"
            img_pil.save(img_path)
            pdf.image(img_path, x=45, y=55, w=120)
            pdf.ln(90)
        else:
            pdf.cell(190, 60, f"ZONE CROQUIS POS {pos['num']}", 1, 1, "C")
            pdf.ln(5)

        # Tableau
        pdf.set_font("Arial", "B", 8)
        widths = [12, 55, 40, 15, 23, 23, 22] 
        headers = pos['df'].columns
        for i in range(len(headers)):
            pdf.cell(widths[i], 10, headers[i], 1, 0, "C", fill=True)
        pdf.ln()
        
        pdf.set_font("Arial", "", 8)
        for index, row in pos['df'].iterrows():
            line_height = 8
            curr_y = pdf.get_y()
            for i in range(len(row)):
                valeur = str(row[i]).replace("⌀", "D.").replace("ø", "d")
                valeur_propre = valeur.encode('latin-1', 'replace').decode('latin-1')
                curr_x = pdf.get_x()
                pdf.multi_cell(widths[i], line_height, valeur_propre, border=1, align="C")
                pdf.set_xy(curr_x + widths[i], curr_y)
            pdf.ln(line_height)
            
    return pdf.output()

# --- BOUTON FINAL ---
if st.button("💾 Générer le PDF Complet (Toutes les positions)"):
    try:
        pdf_bytes = generer_pdf_complet(nom_piece, designation_cao, matiere, machine, positions_data)
        st.success(f"✅ PDF avec {len(positions_data)} page(s) généré !")
        st.download_button(
            label="📥 Télécharger le dossier de phase",
            data=bytes(pdf_bytes),
            file_name=f"Dossier_Phase_{nom_piece}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Erreur : {e}")
