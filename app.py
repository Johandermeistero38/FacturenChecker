import streamlit as st
import pandas as pd
import io

from src.parser.pdf_parser import parse_invoice_pdf
from src.matrix.matcher import evaluate_rows
from src.database.supplier_db import load_suppliers


# ---------------------------------------
# Streamlit pagina instellingen
# ---------------------------------------
st.set_page_config(page_title="Facturen Checker – TOPPOINT", layout="wide")

st.title("🔍 Facturen Checker – TOPPOINT")
st.write(
    "Upload een verkoopfactuur (PDF). De tool herkent per regel automatisch de stof, "
    "zoekt de juiste prijsmatrix op en vergelijkt de prijzen per plooi."
)


# ---------------------------------------
# Leveranciers laden
# ---------------------------------------
suppliers = load_suppliers()
supplier_keys = list(suppliers.keys())

st.subheader("🏢 1. Kies leverancier")
selected_supplier = st.selectbox(
    "Selecteer leverancier",
    options=supplier_keys,
    format_func=lambda key: suppliers[key]["display_name"],
)

st.caption("Momenteel is één leverancier geconfigureerd: TOPPOINT.")


# ---------------------------------------
# Factuur uploaden
# ---------------------------------------
st.subheader("📄 2. Upload verkoopfactuur (PDF)")
invoice_file = st.file_uploader("Upload factuur", type=["pdf"])

if not invoice_file:
    st.info("➡️ Upload eerst een factuur om verder te gaan.")
    st.stop()


# ---------------------------------------
# Factuur analyseren
# ---------------------------------------
st.subheader("📑 3. Factuur uitlezen en regels herkennen")

try:
    rows = parse_invoice_pdf(invoice_file.read())
except Exception as e:
    st.error(f"❌ Fout bij uitlezen van factuur: {e}")
    st.stop()

if not rows:
    st.warning("⚠️ Er zijn geen gordijnregels gevonden in de factuur.")
    st.stop()

st.success(f"✔️ {len(rows)} gordijnregels gevonden.")


# ---------------------------------------
# Prijzen vergelijken per regel / per stof
# ---------------------------------------
st.subheader("🧮 4. Prijzen vergelijken met prijsmatrix(en)")

try:
    results = evaluate_rows(rows, supplier_key=selected_supplier)
except Exception as e:
    st.error(f"❌ Fout bij vergelijken met prijsmatrix(en): {e}")
    st.stop()

df = pd.DataFrame(results)

st.dataframe(df, use_container_width=True, height=600)


# ---------------------------------------
# Resultaten exporteren
# ---------------------------------------
st.subheader("📥 5. Resultaten downloaden")

output = io.BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Resultaten")
output.seek(0)

st.download_button(
    label="📥 Download resultaten als Excel",
    data=output,
    file_name="facturencheck_resultaten.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.success("✔️ Vergelijking voltooid! Je kunt de resultaten downloaden.")
