import streamlit as st
import pandas as pd
from fpdf import FPDF
from PIL import Image
import io

st.set_page_config(page_title="Générateur Pro ENIM", layout="wide")

# --- STYLE ---
st.markdown("<style>.stButton>button { width: 100%; background-color: #007bff; color: white; }</style>", unsafe_allow_html=True)
st.title("🚀 Générateur de Contrats de Phase ENIM")

# --- CLASSE PDF ---
class PDF(FPDF):
    def header(self):
        self.rect(10, 10, 190, 277)
        self.set_font("Arial", "B", 15)
        self.cell(0, 12, "CONTRAT DE PHASE D'USINAGE", 1, 1, "C")
        self.ln(5)

# --- SIDEBAR ---
with st.sidebar:
    st.header("📦 Configuration")
    nom_piece = st.text_input("Nom de la pièce", "PIÈCE_ABC")
    designation_cao = st.text_input("Désignation CAO", "ENSEMBLE_01")
    num_pos = st.number_input("N° de Positionnement", min_value=1, value=1, step=1)
    matiere = st.text_input("Matière", "S300 / 35NiCrMo16")
    machine = st.selectbox("Machine-Outil", ["Haas Mini Mill", "Haas VF2", "Huron", "Somab", "Tour CN"])

# --- CROQUIS ---
st.subheader(f"🖼️ Croquis du Positionnement n°{num_pos}")
image_file = st.file_uploader("Importer le croquis", type=['png', 'jpg', 'jpeg'])

# --- TABLEAU ---
st.subheader("📋 Opérations et Paramètres")
data = {
    "N° Op": [10, 20, 30],
    "Désignation Opération": ["Dressage face", "Ébauche profil", "Finition"],
    "Outils": ["T1 : Outil à dresser", "T1 : Outil à charioter", "T2 : Outil de finition"],
    "ap (mm)": [2.0, 1.5, 0.5],
    "Surépaisseur (mm)": [0.5, 0.5, 0.0],
    "Vc (m/min)": [180, 160, 200],
    "f (mm/tr)": [0.2, 0.25, 0.1]
}
df = pd.DataFrame(data)
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# --- GÉNÉRATION PDF ---
def generer_pdf(nom, cao, pos, mat, mach, table, img):
    pdf = PDF()
    pdf.add_page()
    
    # Entête
    pdf.set_font("Arial", "B", 9)
    pdf.cell(95, 8, f" Piece : {nom}", 1, 0)
    pdf.cell(95, 8, f" CAO : {cao}", 1, 1)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(40, 8, f" POS N : {pos}", 1,
