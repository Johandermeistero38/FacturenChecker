import re
from src.database.supplier_db import load_suppliers


# -------------------------------
# 1. Laad leveranciers + stoffen
# -------------------------------
suppliers = load_suppliers()
toppoint_data = suppliers["toppoint"]
toppoint_fabrics = toppoint_data["fabrics"]


# -------------------------------
# 2. Stof herkennen in tekst
# -------------------------------
def detect_fabric(text: str):
    """
    Zoekt in de tekst naar een geldige stofnaam of alias uit suppliers.json.
    Returnt de OFFICIËLE stofnaam (de key in suppliers.json).
    """
    text_lower = text.lower()

    for fabric_name, config in toppoint_fabrics.items():
        # exacte naam in de tekst?
        if fabric_name.lower() in text_lower:
            return fabric_name

        # alias match?
        for alias in config["aliases"]:
            alias_lower = alias.lower()
            if alias_lower and alias_lower in text_lower:
                return fabric_name

    return None  # niets gevonden


# -------------------------------
# 3. Breedte & hoogte detecteren
# -------------------------------
SIZE_PATTERN = re.compile(r"(\d+)\s*[xX]\s*(\d+)")


# -------------------------------
# 4. Prijs detecteren
# -------------------------------
PRICE_PATTERN = re.compile(r"(\d+[\.,]\d{2})")


# -------------------------------
# 5. Parser functie
# -------------------------------
def parse_invoice_pdf(content: bytes):
    """
    Extract text from PDF and parse:
    - fabric
    - width/height
    - price
    - raw line for debugging
    """

    try:
        import pdfplumber
    except ImportError:
        raise RuntimeError("pdfplumber is niet geïnstalleerd.")

    rows = []

    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            if not text:
                continue

            for line in text.split("\n"):
                line_stripped = line.strip()
                line_lower = line_stripped.lower()

                # -------------------------
                # STAP 1: Stof herkennen
                # -------------------------
                fabric = detect_fabric(line_lower)
                if not fabric:
                    continue  # geen stof → irrelevant

                # -------------------------
                # STAP 2: Afmetingen zoeken
                # -------------------------
                size_match = SIZE_PATTERN.search(line_stripped)
                if not size_match:
                    continue

                width_mm = int(size_match.group(1))
                height_mm = int(size_match.group(2))

                # -------------------------
                # STAP 3: Prijs zoeken
                # -------------------------
                price_match = PRICE_PATTERN.search(line_stripped)
                if not price_match:
                    continue

                price_str = price_match.group(1).replace(",", ".")
                price_value = float(price_str)

                # -------------------------
                # STAP 4: Stofcode (kleur)
                # voorbeeld: "Cosa (7)"
                # -------------------------
                color_code_match = re.search(r"\((\d+)\)", line_stripped)
                fabric_color = color_code_match.group(1) if color_code_match else ""

                # -------------------------
                # STAP 5: Record opslaan
                # -------------------------
                rows.append({
                    "fabric": fabric,
                    "fabric_code": fabric_color,
                    "width_mm": width_mm,
                    "height_mm": height_mm,
                    "invoice_price": price_value,
                    "raw_line": line_stripped,
                })

    return rows
