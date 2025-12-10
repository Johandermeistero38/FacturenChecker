import streamlit as st
import pandas as pd
import io

from src.parser.pdf_parser import parse_invoice_pdf
from src.matrix.matrix_loader import load_price_matrices_from_excel
from src.matrix.matcher import evaluate_rows

st.title("🔍 Facturen Checker – Corsa Prototype")

st.write(
    "Upload een factuur (PDF) en de Corsa-prijsmatrix (Excel). "
    "De tool controleert automatisch alle gordijnregels."
)

invoice_file = st.file_uploader("Upload factuur (PDF)", type=["pdf"])
matrix_file = st.file_uploader("Upload Corsa prijsmatrix (Excel)", type=["xlsx"])

if invoice_file and matrix_file:
    st.subheader("1. Prijsmatrix laden...")
    matrices = load_price_matrices_from_excel(matrix_file)
    st.success(f"Matrixen geladen: {', '.join(matrices.keys())}")

    st.subheader("2. Factuur uitlezen...")
    rows = parse_invoice_pdf(invoice_file.read())

    if not rows:
        st.error("Geen gordijnregels gevonden. Regex aanpassen?")
        st.stop()

    st.info(f"{len(rows)} gordijnregels gevonden.")

    st.subheader("3. Prijscontrole uitvoeren...")
    results = evaluate_rows(rows, matrices)
    df = pd.DataFrame(results)

    st.dataframe(df, use_container_width=True)

    # Download als Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    st.download_button(
        label="📥 Download resultaten als Excel",
        data=output,
        file_name="factuurcheck_resultaten.xlsx"
    )
