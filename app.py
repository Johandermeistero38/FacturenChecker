import sys
import os
import streamlit as st
import pandas as pd

# ============================================================
#   PAD FIX — ZORG DAT /src IN PYTHON PATH STAAT
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# ============================================================
#   PROJECT IMPORTS
# ============================================================

from src.database.supplier_db import load_supplier_config
from src.matrix.matcher import evaluate_rows
from src.matrix.matrix_loader import load_price_matrices
from src.parser.pdf_parser import extract_rows_from_pdf

# ============================================================
#   STREAMLIT INTERFACE
# ============================================================

st.title("🔍 Facturen Checker – TOPPOINT")

# ------------------------------
# 1. Leverancier selecteren
# ------------------------------
st.subheader("1. Kies leverancier")

supplier_key = st.selectbox("Selecteer leverancier", ["toppoint"])

try:
    supplier_config = load_supplier_config(supplier_key)
except Exception as e:
    st.error(f"Fout bij laden van leverancier-configuratie: {e}")
    st.stop()

st.caption(f"Momenteel is één leverancier geconfigureerd: {supplier_key.upper()}.")

# ------------------------------
# 2. Upload factuur PDF
# ------------------------------
st.subheader("2. Upload verkoopfactuur (PDF)")

uploaded_pdf = st.file_uploader("Upload factuur", type=["pdf"])

if not uploaded_pdf:
    st.stop()

st.success(f"📄 {uploaded_pdf.name} is geüpload.")

# ------------------------------
# 3. Factuur uitlezen
# ------------------------------
st.subheader("3. Factuur uitlezen en regels herkennen")

try:
    rows = extract_rows_from_pdf(uploaded_pdf)
    st.success(f"✔️ {len(rows)} regels gevonden.")
except Exception as e:
    st.error(f"Fout bij uitlezen van PDF: {e}")
    st.stop()

# ------------------------------
# 4. Prijzen vergelijken met matrix
# ------------------------------
st.subheader("4. Prijzen vergelijken met prijsmatrix(en)")

progress = st.progress(0)

try:
    matrices = load_price_matrices(supplier_key)
except Exception as e:
    st.error(f"Fout bij laden van prijsmatrices: {e}")
    st.stop()

try:
    results = evaluate_rows(
        rows=rows,
        matrices=matrices,
        progress_callback=lambda p: progress.progress(int(p))
    )
except Exception as e:
    st.error(f"Fout bij vergelijken met prijsmatrix: {e}")
    st.stop()

st.success("✔️ Vergelijking voltooid!")

# ------------------------------
# 5. Resultaten tonen en exporteren
# ------------------------------
st.subheader("5. Resultaten")

df_results = pd.DataFrame(results)
st.dataframe(df_results)

export_name = st.text_input("Bestandsnaam voor export (zonder extensie):", "resultaten")

col1, col2 = st.columns(2)

with col1:
    if st.button("⬇️ Download als Excel"):
        df_results.to_excel(f"{export_name}.xlsx", index=False)
        with open(f"{export_name}.xlsx", "rb") as f:
            st.download_button("Download Excel", f, file_name=f"{export_name}.xlsx")

with col2:
    if st.button("⬇️ Download als CSV"):
        csv_data = df_results.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv_data, file_name=f"{export_name}.csv")
