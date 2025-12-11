import streamlit as st
import tempfile
import pandas as pd

from src.pdf_parser.pdf_parser import extract_rows_from_pdf
from src.matrix_loader import load_supplier_matrices
from src.matcher import evaluate_rows


# ------------------------------
# PAGINA TITEL
# ------------------------------
st.set_page_config(page_title="Facturen Checker – TOPPOINT", layout="wide")
st.title("🔍 Facturen Checker – TOPPOINT")


# ------------------------------
# 1. LEVERANCIER SELECTIE
# ------------------------------
st.header("1. Kies leverancier")

supplier = st.selectbox(
    "Selecteer leverancier",
    ["toppoint"],  # Voor nu alleen TOPPOINT.
)

st.caption("Momenteel is één leverancier geconfigureerd: TOPPOINT.")


# ------------------------------
# 2. PDF UPLOAD
# ------------------------------
st.header("2. Upload verkoopfactuur (PDF)")

pdf_file = st.file_uploader(
    "Upload factuur",
    type=["pdf"],
    help="Upload een PDF factuur van Toppoint."
)


# ------------------------------
# 3. FACTUUR PARSEN
# ------------------------------
if pdf_file:
    st.header("3. Factuur uitlezen en regels herkennen")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_file.getvalue())
        pdf_path = tmp.name

    try:
        rows = extract_rows_from_pdf(pdf_path)
        st.success(f"✓ {len(rows)} gordijnregels gevonden.")
    except Exception as e:
        st.error(f"❌ Fout bij uitlezen van factuur: {e}")
        st.stop()


# ------------------------------
# 4. PRIJZEN VERGELIJKEN MET MATRIX(EN)
# ------------------------------
if pdf_file:
    st.header("4. Prijzen vergelijken met prijsmatrix(en)")

    try:
        matrices = load_supplier_matrices(supplier)

        # 👉 BELANGRIJK: GEEN supplier_key MEER
        results = evaluate_rows(rows, matrices)

        df_results = pd.DataFrame(results)

        st.success("Vergelijken afgerond!")
        st.dataframe(df_results, use_container_width=True)

        # ------------------------------
        # EXPORT KNOP
        # ------------------------------
        st.download_button(
            label="📥 Download resultaten als Excel",
            data=df_results.to_excel(index=False, engine="openpyxl"),
            file_name="factuur_check_resultaten.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Fout bij vergelijken met prijsmatrix(en): {e}")
