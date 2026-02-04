import streamlit as st
import pandas as pd
from fpdf import FPDF
from PIL import Image
import io

st.set_page_config(page_title="Générateur Pro ENIM", layout="wide")

st.title("🚀 Générateur de Contrats de Phase ENIM")

# --- CLASSE PDF (NE PAS SUPPRIMER) ---
class PDF(FPDF):
    def header(self):
        # Dessine le cadre extérieur de 190mm de large
        self.rect(10, 10, 190, 277)
        self.set_font("Arial", "B", 15)
        self.cell(0, 12, "CONTRAT DE PHASE D'USINAGE", 1, 1, "C")
        self.ln(2)

# --- INTERFACE DE SAISIE ---
with st.sidebar:
    st.header("📦 Configuration")
    nom_piece = st.text_input("Nom de la pièce", "AXE_01")
    designation_cao = st.text_input("Désignation CAO", "ENSEMBLE_01")
    num_pos = st.number_input("N° de Positionnement", min_value=1, value=1, step=1)
    matiere = st.text_input("Matière", "35NiCrMo16")
    liste_machines = ["Haas Mini Mill", "Haas VF2", "Huron", "Somab"]
    machine = st.selectbox("Machine-Outil", liste_machines)

st.subheader(f"🖼️ Croquis du Positionnement n°{num_pos}")
image_file = st.file_uploader("Importer le croquis", type=['png', 'jpg', 'jpeg'])

st.subheader("📋 Opérations et Paramètres")
data = {
    "N° Op": [10, 20, 30],
    "Désignation Opération": ["Dressage", "Chariotage Ébauche", "Finition"],
    "Outils": ["T1 : CNMG", "T1 : CNMG", "T2 : VNMG"],
    "ap (mm)": [2.0, 3.0, 0.5],
    "Surépaisseur (mm)": [0.5, 0.5, 0.0],
    "Vc (m/min)": [180, 160, 220],
    "f (mm/tr)": [0.25, 0.35, 0.12]
}
df = pd.DataFrame(data)
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# --- FONCTION DE GÉNÉRATION ---
def generer_pdf(nom, cao, pos, mat, mach, table, img):
    pdf = PDF()
    pdf.add_page()
    
    # Entête
    pdf.set_font("Arial", "B", 9)
    pdf.set_xy(10, 22) # Positionnement après le titre du header
    pdf.cell(95, 8, f" Piece : {nom}", 1)
    pdf.cell(95, 8, f" CAO : {cao}", 1, 1)
    
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(40, 8, f" POS N : {pos}", 1, 0, "L", fill=True)
    pdf.cell(75, 8, f" Matiere : {mat}", 1, 0)
    pdf.cell(75, 8, f" Machine : {mach}", 1, 1)
    
    # Croquis
    pdf.ln(5)
    if img:
        img_pil = Image.open(img)
        img_path = "temp_img.png"
        img_pil.save(img_path)
        pdf.image(img_path, x=40, y=55, w=130)
        pdf.ln(95)
    else:
        pdf.cell(190, 55, "ZONE CROQUIS (ISO / COTES)", 1, 1, "C")
        pdf.ln(5)

    # Tableau
    pdf.set_font("Arial", "B", 8)
    # Largeurs cumulées = 190mm
    widths = [12, 55, 38, 15, 25, 22, 23] 
    headers = table.columns
    for i in range(len(headers)):
        pdf.cell(widths[i], 10, headers[i], 1, 0, "C")
    pdf.ln()
    
    pdf.set_font("Arial", "", 8)
    for index, row in table.iterrows():
        for i in range(len(row)):
            valeur = str(row[i]).replace("⌀", "Diam.").replace("ø", "o")
            valeur_propre = valeur.encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(widths[i], 8, valeur_propre, 1, 0, "C")
        pdf.ln()
    
    return pdf.output()

# --- VALIDATION ---
st.divider()
if st.button("💾 Valider et Générer le PDF"):
    try:
        pdf_val = generer_pdf(nom_piece, designation_cao, num_pos, matiere, machine, edited_df, image_file)
        st.download_button(
            label="📥 Télécharger le document final",
            data=bytes(pdf_val),
            file_name=f"CP_{nom_piece}_POS{num_pos}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Erreur lors de la génération : {e}")
