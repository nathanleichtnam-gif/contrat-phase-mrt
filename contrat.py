import streamlit as st
import pandas as pd
from fpdf import FPDF
from PIL import Image
import io

st.set_page_config(page_title="Générateur Pro ENIM", layout="wide")

# --- STYLE CSS POUR L'INTERFACE ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Générateur de Contrats de Phase ENIM")

# --- CLASSE PDF AVEC GESTION DU CADRE ---
class PDF(FPDF):
    def header(self):
        # Cadre extérieur (10mm de marge)
        self.rect(10, 10, 190, 277)
        self.set_font("Arial", "B", 15)
        self.cell(0, 12, "CONTRAT DE PHASE D'USINAGE", 1, 1, "C")
        self.ln(5)

# --- INTERFACE DE SAISIE (BARRE LATÉRALE) ---
with st.sidebar:
    st.header("📦 Configuration")
    nom_piece = st.text_input("Nom de la pièce", "PIÈCE_ABC")
    designation_cao = st.text_input("Désignation CAO", "ENSEMBLE_01")
    num_pos = st.number_input("N° de Positionnement", min_value=1, value=1, step=1)
    matiere = st.text_input("Matière", "S300 / 35NiCrMo16")
    machine = st.selectbox("Machine-Outil", ["Haas Mini Mill", "Haas VF2", "Huron", "Somab", "Tour CN"])

# --- SECTION CROQUIS ---
st.subheader(f"🖼️ Croquis du Positionnement n°{num_pos}")
image_file = st.file_uploader("Importer le croquis (Mise en position + Cotes)", type=['png', 'jpg', 'jpeg'])

# --- SECTION TABLEAU TECHNIQUE ---
st.subheader("📋 Opérations et Paramètres")
data = {
    "N° Op": [10, 20, 30],
    "Désignation Opération": ["Dressage face", "Ébauche profil", "Finition"],
    "Outils": ["T1 : Outil à dresser", "T1 : Outil à charioter", "T2 : Outil de finition"],
    "ap (mm)": [2.0, 1.5, 0.5],
    "Surépaisseur (mm)": [0.5, 0.5, 0.0],
    "Vc (m/min)": [180, 160, 20
