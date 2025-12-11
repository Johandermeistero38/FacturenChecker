import sys
import os
import streamlit as st
import pandas as pd

# ====== FIX: Zorg dat Streamlit de /src map kan vinden ======
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# ====== IMPORTS (GEEN src. MEER!) ======
from database.supplier_db import load_supplier_config
from matrix.matcher import evaluate_rows
from matrix.matrix_loader import load_price_matrices
from parser.pdf_parser import extract_rows_from_pdf


# ---------------------------------------------------------
# Pagina-instellingen
# ---------------------------------------------------------
st.set_page_config(page_title="Facturen Checker – TOPPOINT", layout="wide")

st.title("🔍 Facturen Checker – TOPPOINT")

# ---------------------------------------------------------
# 1. Kies leverancier
# ---------------------------------------------------------
st.header("1. Kies leverancier")

suppliers = load_supplier_config()
supplier_names = [s["name"] for s in suppliers]

supplier_choice = st.selectbox("Selecteer leverancier", supplier_names)

supplier_key = None
for s in suppliers:
    if s["name"] == supplier_choice:
        supplier_key = s["key"]
        break

if not supplier_key:
    st.error("Kon leverancier niet vinden in database!")
    st.stop()

# ---------------------------------------------------------
# 2. Upload factuur
# ---------------------------------------------------------
st.header("💾 2. Upload verkoopfactuur (PDF)")

uploaded_pdf = st.file_uploader("Upload factuur", type=["pdf"])

if not uploaded_pdf:
    st.info("⬆️ Upload eerst een factuur om verder te gaan.")
    st.stop()

# ---------------------------------------------------------
# 3. Factuur uitlezen
# ---------------------------------------------------------
st.header("📄 3. Factuur uitlezen en regels herkennen")

try:
    invoice_rows = extract_rows_from_pdf(uploaded_pdf)
    st.success(f"✔️ {len(invoice_rows)} gordijnregels gevonden.")
except Exception as e:
    st.error(f"Fout bij uitlezen van factuur: {e}")
    st.stop()

# ---------------------------------------------------------
# 4. Matrix laden
# ---------------------------------------------------------
st.header("📊 4. Prijzen vergelijken met prijsmatrix(en)")

try:
    matrices = load_price_matrix(supplier_key)
except Exception as e:
    st.error(f"❌ Fout bij laden van matrix: {e}")
    st.stop()

# ---------------------------------------------------------
# 5. Vergelijking uitvoeren
# ---------------------------------------------------------
st.write("Bezig met berekenen...")

try:
    result_df = evaluate_rows(invoice_rows, matrices)
except Exception as e:
    st.error(f"❌ Fout bij vergelijken met prijsmatrix(en): {e}")
    st.stop()

st.success("✔️ Vergelijking voltooid!")

st.dataframe(result_df)

# ---------------------------------------------------------
# 6. Exportfunctie
# ---------------------------------------------------------
st.header("📤 5. Resultaten exporteren")

export_name = st.text_input("Bestandsnaam (zonder extensie):", "factuurcontrole")

export_format = st.selectbox("Exportformaat:", ["Excel (.xlsx)", "CSV (.csv)"])

if st.button("Download"):
    if export_format == "Excel (.xlsx)":
        file = result_df.to_excel(index=False, engine="openpyxl")
        st.success("✔️ Excel-bestand gedownload.")
    else:
        file = result_df.to_csv(index=False).encode("utf-8")
        st.success("✔️ CSV-bestand gedownload.")

    st.download_button(
        label="📥 Download bestand",
        data=file,
        file_name=f"{export_name}{'.xlsx' if export_format.startswith('Excel') else '.csv'}"
    )
