import streamlit as st
import pandas as pd
import io

from src.parser.pdf_parser import parse_invoice_pdf
from src.matrix.matcher import evaluate_rows
from src.database.supplier_db import load_suppliers


st.set_page_config(page_title="Facturen Checker – TOPPOINT", layout="wide")

st.title("🔍 Facturen Checker – TOPPOINT")
st.write(
    "Upload een verkoopfactuur (PDF). De tool herkent per regel automatisch de stof, "
    "zoekt de juiste prijsmatrix op en vergelijkt de prijzen per plooi."
)

# ---------------------------------------
# 1. Leverancier kiezen
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
# 2. Factuur uploaden
# ---------------------------------------
st.subheader("📄 2. Upload verkoopfactuur (PDF)")
invoice_file = st.file_uploader("Upload factuur", type=["pdf"])

if not invoice_file:
    st.info("➡️ Upload eerst een factuur om verder te gaan.")
    st.stop()


# ---------------------------------------
# 3. Factuur uitlezen
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
# 4. Prijzen vergelijken met prijsmatrix(en)
# ---------------------------------------
st.subheader("🧮 4. Prijzen vergelijken met prijsmatrix(en)")

progress_bar = st.progress(0)
progress_text = st.empty()

def progress_callback(done, total):
    pct = int(done / total * 100)
    progress_bar.progress(pct)
    progress_text.text(f"Bezig met vergelijken... {done}/{total} regels ({pct}%)")

with st.spinner("Prijzen worden vergeleken..."):
    try:
        results = evaluate_rows(rows, supplier_key=selected_supplier, progress_callback=progress_callback)
    except Exception as e:
        st.error(f"❌ Fout bij vergelijken met prijsmatrix(en): {e}")
        st.stop()

progress_text.text("Vergelijken voltooid.")
progress_bar.progress(100)

df = pd.DataFrame(results)

# Resultaten pas tonen als gebruiker dat wil
show_table = st.checkbox("Laat resultaten in browser zien", value=False)

if show_table:
    st.dataframe(df, use_container_width=True, height=600)


# ---------------------------------------
# 5. Resultaten exporteren
# ---------------------------------------
st.subheader("📥 5. Resultaten downloaden")

default_name = "facturencheck_resultaten"
export_name = st.text_input("Bestandsnaam (zonder extensie)", value=default_name)

export_format = st.radio(
    "Kies exportformaat",
    options=["Excel (.xlsx)", "CSV (.csv)"],
    index=0,
    horizontal=True,
)

if export_format.startswith("Excel"):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultaten")
    buffer.seek(0)
    filename = (export_name or default_name) + ".xlsx"
    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
else:
    csv_data = df.to_csv(index=False).encode("utf-8-sig")
    buffer = io.BytesIO(csv_data)
    filename = (export_name or default_name) + ".csv"
    mime = "text/csv"

st.download_button(
    label="📥 Download resultaten",
    data=buffer,
    file_name=filename,
    mime=mime,
)

st.success("✔️ Vergelijking voltooid! Je kunt de resultaten downloaden.")
