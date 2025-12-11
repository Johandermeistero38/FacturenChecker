import sys
import os
import streamlit as st
import pandas as pd

# ============================================================
#   PAD FIX — ZORG DAT /src GEVONDEN WORDT
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# ============================================================
#   IMPORTS VANUIT JOUW PROJECTSTRUCTUUR
# ============================================================
from database.supplier_db import load_supplier_config
from matrix.matcher import evaluate_rows
from matrix.matrix_loader import load_price_matrices
from parser.pdf_parser import extract_rows_from_pdf


# ============================================================
#   STREAMLIT UI
# ============================================================

st.title("🔍 Facturen Checker – TOPPOINT")

# ------------------------------
# 1. Leverancier kiezen
# ------------------------------
st.subheader("1. Kies leverancier")

supplier_key = st.selectbox("Selecteer leverancier", ["toppoint"])

# Laad leverancier-config
try:
    supplier_config = load_supplier_config(supplier_key)
except Exception as e:
    st.error(f"Fout bij laden van supplier config: {e}")
    st.stop()

st.caption(f"Momenteel is één leverancier geconfigureerd: {supplier_key.upper()}.")

# ------------------------------
# 2. Upload factuur PDF
# ------------------------------
st.subheader("2. Upload verkoopfactuur (PDF)")

uploaded_pdf = st.file_uploader("Upload factuur", type=["pdf"])

if not uploaded_pdf:
    st.stop()

st.success(f"📄 {uploaded_pdf.name} geüpload.")

# ------------------------------
# 3. Factuur uitlezen
# ------------------------------
st.subheader("3. Factuur uitlezen en regels herkennen")

try:
    rows = extract_rows_from_pdf(uploaded_pdf)
    st.success(f"✔️ {len(rows)} gordijnregels gevonden.")
except Exception as e:
    st.error(f"Fout bij uitlezen van factuur: {e}")
    st.stop()

# ------------------------------
# 4. Prijzen vergelijken
# ------------------------------
st.subheader("4. Prijzen vergelijken met prijsmatrix(en)")

progress_bar = st.progress(0)

try:
    matrices = load_price_matrices(supplier_key)
except Exception as e:
    st.error(f"Fout bij laden van prijsmatrices: {e}")
    st.stop()

try:
    results = evaluate_rows(
        rows=rows,
        matrices=matrices,
        progress_callback=lambda p: progress_bar.progress(int(p))
    )
except Exception as e:
    st.error(f"Fout bij vergelijken met prijsmatrix(en): {e}")
    st.stop()

st.success("✔️ Vergelijking voltooid")

# ------------------------------
# 5. Resultaten tonen + export
# ------------------------------
st.subheader("5. Resultaten")

df_results = pd.DataFrame(results)
st.dataframe(df_results)

export_name = st.text_input("Bestandsnaam voor export (zonder extensie):", "resultaten")

col1, col2 = st.columns(2)

with col1:
    if st.button("⬇️ Download als Excel"):
        file = df_results.to_excel(f"{export_name}.xlsx", index=False)
        st.download_button(
            "Download Excel",
            data=open(f"{export_name}.xlsx", "rb").read(),
            file_name=f"{export_name}.xlsx"
        )

with col2:
    if st.button("⬇️ Download als CSV"):
        csv_data = df_results.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv_data,
            file_name=f"{export_name}.csv",
            mime="text/csv"
        )
