import streamlit as st
import pandas as pd
from io import BytesIO

from src.parser.pdf_parser import parse_invoice_pdf
from src.matrix.matcher import evaluate_rows
from src.database.supplier_db import load_suppliers

# -----------------------------
# Basis instellingen
# -----------------------------
st.set_page_config(page_title="Facturen Checker – TOPPOINT", layout="wide")

st.title("🔍 Facturen Checker – TOPPOINT")
st.write(
    "Upload een verkoopfactuur (PDF). De tool leest automatisch alle gordijnregels, "
    "zoekt de bijbehorende prijsmatrix en vergelijkt de prijzen."
)

# -----------------------------
# 1. Leverancier kiezen
# -----------------------------
st.subheader("1. Kies leverancier")

suppliers = load_suppliers()
supplier_keys = list(suppliers.keys())  # bv. ['toppoint']

selected_supplier = st.selectbox(
    "Selecteer leverancier",
    options=supplier_keys,
    format_func=lambda key: suppliers[key].get("display_name", key.upper()),
)

# -----------------------------
# 2. Upload factuur
# -----------------------------
st.subheader("2. Upload verkoopfactuur (PDF)")

uploaded_file = st.file_uploader("Kies een PDF-bestand", type=["pdf"])

if not uploaded_file:
    st.info("➡️ Upload eerst een factuur om verder te gaan.")
    st.stop()

# -----------------------------
# 3. Factuur uitlezen
# -----------------------------
st.subheader("3. Factuur uitlezen en regels herkennen")

try:
    content = uploaded_file.read()
    rows = parse_invoice_pdf(content)  # verwacht: lijst met dicts per regel
except Exception as e:
    st.error(f"❌ Fout bij uitlezen van factuur: {e}")
    st.stop()

if not rows:
    st.warning("⚠️ Er zijn geen gordijnregels gevonden in deze factuur.")
    st.stop()

st.success(f"✔ {len(rows)} gordijnregels gevonden.")

# -----------------------------
# 4. Prijzen vergelijken
# -----------------------------
st.subheader("4. Prijzen vergelijken met prijsmatrix(en)")

try:
    # evaluate_rows gebruikt intern de supplier-config (via supplier_db / matrix_loader)
    results = evaluate_rows(rows)
except Exception as e:
    st.error(f"❌ Fout bij vergelijken met prijsmatrix(en): {e}")
    st.stop()

df = pd.DataFrame(results)

toon_tabel = st.checkbox("Toon resultaten in de browser", value=True)
if toon_tabel:
    st.dataframe(df, use_container_width=True)

# -----------------------------
# 5. Resultaten downloaden
# -----------------------------
st.subheader("5. Resultaten downloaden")

bestandsnaam = st.text_input("Bestandsnaam (zonder extensie)", value="factuurcheck_resultaten")

export_formaat = st.radio(
    "Kies exportformaat",
    options=["Excel (.xlsx)", "CSV (.csv)"],
    index=0,
    horizontal=True,
)

if export_formaat.startswith("Excel"):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultaten")
    buffer.seek(0)
    data = buffer
    filename = f"{bestandsnaam}.xlsx"
    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
else:
    csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
    data = csv_bytes
    filename = f"{bestandsnaam}.csv"
    mime = "text/csv"

st.download_button(
    label="📥 Download resultaten",
    data=data,
    file_name=filename,
    mime=mime,
)
