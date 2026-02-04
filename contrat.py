import streamlit as st
import pandas as pd
from fpdf import FPDF
from PIL import Image
import io

st.set_page_config(page_title="Contrat de Phase ENIM", layout="wide")

st.title("🚀 Générateur de Contrats de Phase par Positionnement")

# --- INTERFACE DE SAISIE (ENTÊTE) ---
with st.sidebar:
    st.header("📦 Configuration du Poste")
    nom_piece = st.text_input("Nom de la pièce", "AXE_01")
    designation_cao = st.text_input("Désignation CAO", "ENSEMBLE_MOTEUR")
    
    # AJOUT DU POSITIONNEMENT DANS L'ENTÊTE
    num_pos = st.number_input("N° de Positionnement", min_value=1, value=1, step=1)
    
    matiere = st.text_input("Matière", "35NiCrMo16")
    liste_machines = ["Haas Mini Mill", "Haas VF2", "Huron", "Somab"]
    machine = st.selectbox("Machine-Outil", liste_machines)

# --- SECTION CROQUIS ---
st.subheader(f"🖼️ Croquis du Positionnement n°{num_pos}")
st.caption("Le croquis doit montrer la mise en position (Isostatisme) et les cotes fabriquées.")
image_file = st.file_uploader("Importer le croquis de phase", type=['png', 'jpg', 'jpeg'])

# --- SECTION TABLEAU TECHNIQUE (Modifié) ---
st.subheader(f"📋 Phases d'usinage pour le Positionnement {num_pos}")

data = {
    "N° Op": [10, 20, 30],
    "Désignation Opération": ["Dressage", "Chariotage", "Finition"],
    "Outils": ["T1 : CNMG", "T1 : CNMG", "T2 : VNMG"],
    "ap (mm)": [2.0, 3.0, 0.5],
    "Surépaisseur (mm)": [0.5, 0.5, 0.0], # <-- Nouvelle colonne
    "Vc (m/min)": [180, 160, 220],
    "f (mm/tr)": [0.25, 0.35, 0.12]
}

df = pd.DataFrame(data)
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# --- FONCTION PDF (Ajustée pour 7 colonnes) ---
def generer_pdf(nom, cao, pos, mat, mach, table, img):
    pdf = PDF()
    pdf.add_page()
    
    # ... (garder le même début pour l'entête et le croquis) ...
    # [Code d'entête identique au précédent]

    # Tableau des opérations (Nouveaux calculs de largeurs)
    pdf.set_font("Arial", "B", 8)
    # Total doit faire 190mm : 
    # N°(12) + Désig(55) + Outils(38) + ap(15) + Surépaiss(25) + Vc(22) + f(23) = 190
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
if st.button("💾 Générer le PDF du Positionnement"):
    pdf_output = generer_pdf(nom_piece, designation_cao, num_pos, matiere, machine, edited_df, image_file)
    st.download_button(
        label=f"📥 Télécharger la fiche POS {num_pos}",
        data=bytes(pdf_output),
        file_name=f"CP_{nom_piece}_POS{num_pos}.pdf",
        mime="application/pdf"
)
