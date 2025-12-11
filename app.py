import streamlit as st
import pandas as pd

from src.parser.pdf_parser import parse_invoice_pdf
from src.matrix.matcher import evaluate_rows
from src.database.supplier_db import load_suppliers
from io import BytesIO

st.set_page_config(page_title="Facturen Checker – TOPPOINT", layout="wide")
suppliers = load_suppliers()

# ----------------------------------------------
# Header
# ----------------------------------------------
st.title("🔎 Facturen Checker – TOPPOINT")

# ----------------------------------------------
# 1. Leverancier kiezen
# ----------------------------------------------
st.header("1. Kies leverancier")
supplier_key = st.selectbox("Selecteer leverancier", options=list(suppliers.keys()))
st.caption(f"Momenteel is één leverancier geconfigureerd: {supplier_key.upper()}.")

# ----------------------------------------------
# 2. Upload factuur
# ----------------------------------------------
st.header("2. Upload verkoopfactuur (PDF)")
uploaded_pdf = st.file_uploader("Upload factuur", type=["pdf"])

if not uploaded_pdf:
    st.stop()

# ----------------------------------------------
# 3. Factuur uitlezen
# ----------------------------------------------
st.header("3. Factuur uitlezen en regels herkennen")

try:
    rows = parse_invoice_pdf(uploaded_pdf.read())
    st.success(f"✔ {len(rows)} gordijnregels gevonden.")
except Exception as e:
    st.error(f"❌ Fout bij uitlezen factuur: {e}")
    st.stop()

# ----------------------------------------------
# 4. Prijzen vergelijken
# ----------------------------------------------
st.header("4. Prijzen vergelijken met prijsmatrix(en)")

progress_bar = st.progress(0.0)

def update_progress(value):
    progress_bar.progress(value)

try:
    results = evaluate_rows(
        rows,
        supplier_key=supplier_key,
        progress_callback=update_progress
    )
except Exception as e:
    st.error(f"❌ Fout bij vergelijken met prijsmatrix(en): {e}")
    st.stop()

df = pd.DataFrame(results)

# Verberg matrix optioneel
with st.expander("Toon matrix-resultaten"):
    st.dataframe(df, use_container_width=True)

# ----------------------------------------------
# 5. Exporteren
# ----------------------------------------------
st.header("5. Exporteer resultaten")

export_name = st.text_input("Bestandsnaam", value="factuurcontrole")
export_format = st.selectbox("Bestandsformaat", ["Excel (.xlsx)", "CSV (.csv)"])

if export_format == "Excel (.xlsx)":
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    st.download_button(
        "Download als Excel",
        data=buffer.getvalue(),
        file_name=f"{export_name}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download als CSV",
        data=csv,
        file_name=f"{export_name}.csv",
        mime="text/csv"
    )
