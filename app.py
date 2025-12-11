import io

from src.parser.pdf_parser import parse_invoice_pdf
from src.matrix.matrix_loader import load_price_matrices_from_excel
from src.matrix.matcher import evaluate_rows
from src.database.supplier_db import load_suppliers, get_supplier_matrix_path
from src.database.supplier_db import load_suppliers


# ----------------------------------------------------------------------
# APP HEADER
# ----------------------------------------------------------------------

st.set_page_config(page_title="Facturen Checker – Toppoint", layout="wide")
# ---------------------------------------
# Streamlit pagina instellingen
# ---------------------------------------
st.set_page_config(page_title="Facturen Checker – TOPPOINT", layout="wide")

st.title("🔍 Facturen Checker – TOPPOINT")
st.write(
    "Upload een verkoopfactuur (PDF), kies een leverancier, "
    "en de tool vergelijkt automatisch alle gordijnprijzen met de bijbehorende prijsmatrixen."
    "Upload een verkoopfactuur (PDF). De tool herkent per regel automatisch de stof, "
    "zoekt de juiste prijsmatrix op en vergelijkt de prijzen per plooi."
)


# ----------------------------------------------------------------------
# 1. FACTUUR UPLOADEN
# ----------------------------------------------------------------------

st.subheader("📄 1. Upload verkoopfactuur (PDF)")
invoice_file = st.file_uploader("Upload factuur", type=["pdf"])


# ----------------------------------------------------------------------
# 2. LEVERANCIER KIEZEN
# ----------------------------------------------------------------------

st.subheader("🏢 2. Kies leverancier")

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

st.caption("Op dit moment is alleen stof **Corsa/Cosa** geconfigureerd voor Toppoint.")


# Stop als er nog geen factuur is
if not invoice_file:
    st.info("➡️ Upload eerst een factuur om door te gaan.")
    st.stop()


# ----------------------------------------------------------------------
# 3. PRIJSMATRIX LADEN
# ----------------------------------------------------------------------
st.caption("Momenteel is één leverancier geconfigureerd: TOPPOINT.")

st.subheader("📊 3. Prijsmatrix laden voor gekozen leverancier")

try:
    # Voor nu: één stof 'corsa' (waar 'cosa' ook onder valt)
    matrix_path = get_supplier_matrix_path(suppliers, selected_supplier, fabric_key="corsa")

    st.success(f"Prijsmatrix gevonden voor Toppoint: `{matrix_path}`")

    matrices = load_price_matrices_from_excel(matrix_path)

    st.info(f"Matrixen geladen: **{', '.join(matrices.keys())}**")
# ---------------------------------------
# Factuur uploaden
# ---------------------------------------
st.subheader("📄 2. Upload verkoopfactuur (PDF)")
invoice_file = st.file_uploader("Upload factuur", type=["pdf"])

except Exception as e:
    st.error(f"❌ Fout bij laden van prijsmatrix: {e}")
if not invoice_file:
    st.info("➡️ Upload eerst een factuur om verder te gaan.")
    st.stop()


# ----------------------------------------------------------------------
# 4. FACTUUR UITLEZEN
# ----------------------------------------------------------------------

st.subheader("📑 4. Factuur analyseren...")
# ---------------------------------------
# Factuur analyseren
# ---------------------------------------
st.subheader("📑 3. Factuur uitlezen en regels herkennen")

try:
    rows = parse_invoice_pdf(invoice_file.read())
@@ -93,24 +64,26 @@
st.success(f"✔️ {len(rows)} gordijnregels gevonden.")


# ----------------------------------------------------------------------
# 5. VERGELIJKEN MET MATRIX
# ----------------------------------------------------------------------
# ---------------------------------------
# Prijzen vergelijken per regel / per stof
# ---------------------------------------
st.subheader("🧮 4. Prijzen vergelijken met prijsmatrix(en)")

st.subheader("🧮 5. Prijzen vergelijken met prijsmatrix...")
try:
    results = evaluate_rows(rows, supplier_key=selected_supplier)
except Exception as e:
    st.error(f"❌ Fout bij vergelijken met prijsmatrix(en): {e}")
    st.stop()

results = evaluate_rows(rows, matrices)
df = pd.DataFrame(results)

# Optioneel: kolombreedte verbeteren
st.dataframe(df, use_container_width=True, height=600)


# ----------------------------------------------------------------------
# 6. EXPORTEREN
# ----------------------------------------------------------------------

st.subheader("📥 6. Resultaten downloaden")
# ---------------------------------------
# Resultaten exporteren
# ---------------------------------------
st.subheader("📥 5. Resultaten downloaden")

output = io.BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
