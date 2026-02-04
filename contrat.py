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

# --- SECTION TABLEAU TECHNIQUE ---
st.subheader(f"📋 Phases d'usinage pour le Positionnement {num_pos}")

# Le tableau ne contient plus le positionnement puisqu'il est en entête
data = {
    "N° Op": [10, 20, 30],
    "Désignation Opération": ["Dressage", "Chariotage", "Finition"],
    "Outils": ["T1 : CNMG", "T1 : CNMG", "T2 : VNMG"],
    "ap (mm)": [2.0, 3.0, 0.5],
    "Vc (m/min)": [180, 160, 220],
    "f (mm/tr)": [0.25, 0.35, 0.12]
}

df = pd.DataFrame(data)
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# --- CONFIGURATION DU PDF ---
class PDF(FPDF):
    def header(self):
        self.rect(5, 5, 200, 287)
        self.set_font("Arial", "B", 15)
        self.cell(0, 12, "CONTRAT DE PHASE D'USINAGE", 1, 1, "C")
        self.ln(2)

def generer_pdf(nom, cao, pos, mat, mach, table, img):
    pdf = PDF()
    pdf.add_page()
    
    # Bloc Entête (Largeur totale 190mm pour laisser 10mm de marge)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(95, 8, f" Piece : {nom}", 1)
    pdf.cell(95, 8, f" CAO : {cao}", 1, 1)
    
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(40, 8, f" POS N : {pos}", 1, 0, "L", fill=True)
    pdf.cell(75, 8, f" Matiere : {mat}", 1, 0)
    pdf.cell(75, 8, f" Machine : {mach}", 1, 1)
    
    # Espace Croquis
    pdf.ln(5)
    if img:
        img_pil = Image.open(img)
        img_path = "temp_img.png"
        img_pil.save(img_path)
        # On centre l'image (X=40 pour une largeur de 130mm sur une feuille de 210mm)
        pdf.image(img_path, x=40, y=50, w=130)
        pdf.ln(90) # On laisse de la place sous l'image
    else:
        pdf.cell(190, 50, f"CROQUIS DE MISE EN POSITION (POS {pos})", 1, 1, "C")
        pdf.ln(5)

    # Tableau des opérations (Largeurs ajustées pour un total de 190mm)
    pdf.set_font("Arial", "B", 8)
    # N°Op(15) + Désig(65) + Outils(45) + ap(15) + Vc(25) + f(25) = 190mm
    widths = [15, 65, 45, 15, 25, 25] 
    headers = table.columns
    
    # On dessine l'entête du tableau
    for i in range(len(headers)):
        pdf.cell(widths[i], 10, headers[i], 1, 0, "C")
    pdf.ln()
    
    # Contenu du tableau
    pdf.set_font("Arial", "", 8)
    for index, row in table.iterrows():
        # Pour éviter que le tableau ne sorte en bas de page, on pourrait ajouter une condition
        for i in range(len(row)):
            valeur = str(row[i])
            valeur_propre = valeur.replace("\u2300", "Diam.").replace("⌀", "Diam.").replace("ø", "o")
            valeur_propre = valeur_propre.encode('latin-1', 'replace').decode('latin-1')
            
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
