import streamlit as st
import pandas as pd
import io

from src.parser.pdf_parser import parse_invoice_pdf
from src.matrix.matrix_loader import load_price_matrices_from_excel
from src.matrix.matcher import evaluate_rows
from src.database.supplier_db import load_suppliers, get_supplier_matrix_path


st.title("🔍 Facturen Checker – TOPPOINT")

st.write(
    "Upload een verkoopfactuur (PDF), kies een leverancier, "
    "en de tool vergelijkt automatisch de gordijnprijzen met de gekoppelde prijsmatrix(en)."
)

# 1. Factuur uploaden
invoice_file = st.file_uploader("Upload factuur (PDF)", type=["pdf"])

# 2. Leveranciers laden uit JSON
suppliers = load_suppliers()
supplier_keys = list(suppliers.keys())

# Dropdown voor leverancier (nu alleen TOPPOINT)
selected_supplier = st.selectbox(
    "Kies leverancier",
    options=supplier_keys,
    format_func=lambda key: suppliers[key]["display_name"]
)

st.caption("Voor nu is alleen stof Corsa/Cosa geconfigureerd voor TOPPOINT.")

if invoice_file and selected_supplier:
    st.subheader("1. Prijsmatrix ophalen voor gekozen leverancier...")

    try:
        # Voor nu gebruiken we altijd stof 'corsa' (waar 'cosa' ook onder valt)
        matrix_path = get_supplier_matrix_path(suppliers, selected_supplier, fabric_key="corsa")
        st.write(f"Gebruik matrixbestand: `{matrix_path}`")

        # Laad de matrix vanuit het pad in de repo
        matrices = load_price_matrices_from_excel(matrix_path)
        st.success(f"Matrixen geladen: {', '.join(matrices.keys())}")

        # Optioneel: staffels tonen ter controle
        enkel = matrices.get("Enkele plooi")
        if enkel:
            st.write("Breedte-staffels (cm):", enkel["widths"])
            st.write("Hoogte-staffels (cm):", enkel["heights"])

    except Exception as e:
        st.error(f"Fout bij laden van matrix voor leverancier '{selected_supplier}': {e}")
        st.stop()

    st.subheader("2. Factuur uitlezen...")
    try:
        rows = parse_invoice_pdf(invoice_file.read())
    except Exception as e:
        st.error(f"Fout bij lezen/analyseren factuur: {e}")
        st.stop()

    if not rows:
        st.warning("Geen gordijnregels gevonden in de factuur. "
                   "Mogelijk moet de parser nog verder worden uitgebreid.")
        st.stop()

    st.info(f"{len(rows)} gordijnregels gevonden.")

    st.subheader("3. Prijzen vergelijken met matrix...")
    results = evaluate_rows(rows, matrices)
    df = pd.DataFrame(results)

    st.dataframe(df, use_container_width=True)

    # Download als Excel
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
else:
    st.info("Upload eerst een factuur en kies een leverancier om de controle uit te voeren.")
