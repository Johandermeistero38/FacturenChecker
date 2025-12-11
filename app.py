import streamlit as st
import tempfile
import pandas as pd

from src.pdf_parser.pdf_parser import extract_rows_from_pdf
from src.matrix_loader import load_supplier_matrices
from src.matcher import evaluate_rows

st.set_page_config(page_title="Facturen Checker – TOPPOINT", layout="wide")
st.title("🔍 Facturen Checker – TOPPOINT")

st.header("1. Kies leverancier")
supplier = st.selectbox("Selecteer leverancier", ["toppoint"])

st.header("2. Upload verkoopfactuur (PDF)")
pdf_file = st.file_uploader("Upload factuur", type=["pdf"])

rows = None

if pdf_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_file.getvalue())
        pdf_path = tmp.name

    st.header("3. Factuur uitlezen…")

    try:
        rows = extract_rows_from_pdf(pdf_path)
        st.success(f"✓ {len(rows)} gordijnregels gevonden.")
    except Exception as e:
        st.error(f"❌ Fout bij inlezen factuur: {e}")
        st.stop()

if rows:
    st.header("4. Prijzen vergelijken…")

    try:
        matrices = load_supplier_matrices(supplier)
        results = evaluate_rows(rows, matrices)
        df = pd.DataFrame(results)

        st.dataframe(df, use_container_width=True)

        st.download_button(
            label="📥 Download resultaten als Excel",
            data=df.to_excel(index=False, engine="openpyxl"),
            file_name="factuurcheck_resultaten.xlsx"
        )
    except Exception as e:
        st.error(f"❌ Fout bij prijsvergelijking: {e}")
