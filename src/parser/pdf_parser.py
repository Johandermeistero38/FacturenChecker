import re
import io

import pdfplumber
from src.database.supplier_db import load_suppliers


# ---------------------------------
# 1. Leveranciers + stoffen laden
# ---------------------------------
suppliers = load_suppliers()
toppoint_data = suppliers["toppoint"]
toppoint_fabrics = toppoint_data["fabrics"]


# ---------------------------------
# 2. Stof herkennen in tekst
#    - match alleen hele woorden
#    - kies de langste match
# ---------------------------------
def detect_fabric(text: str):
    """
    Zoekt in de tekst naar een geldige stofnaam of alias uit suppliers.json.
    - gebruikt woordgrenzen (\b) zodat 'between' niet matcht in 'inbetween'
    - kiest de langste match als er meerdere mogelijkheden zijn
    Returnt de OFFICIËLE stofnaam (de key in suppliers.json), of None.
    """
    text_lower = text.lower()
    best_match = None
    best_length = 0

    for fabric_name, config in toppoint_fabrics.items():
        # 1) officiële naam checken
        name_pattern = r"\b" + re.escape(fabric_name.lower()) + r"\b"
        if re.search(name_pattern, text_lower):
            if len(fabric_name) > best_length:
                best_match = fabric_name
                best_length = len(fabric_name)

        # 2) aliassen checken
        for alias in config.get("aliases", []):
            alias = alias.strip().lower()
            if not alias:
                continue

            alias_pattern = r"\b" + re.escape(alias) + r"\b"
            if re.search(alias_pattern, text_lower):
                if len(alias) > best_length:
                    best_match = fabric_name
                    best_length = len(alias)

    return best_match


# ---------------------------------
# 3. Breedte & hoogte detecteren
# ---------------------------------
SIZE_PATTERN = re.compile(r"(\d+)\s*[xX]\s*(\d+)")


# ---------------------------------
# 4. Prijs detecteren
# ---------------------------------
PRICE_PATTERN = re.compile(r"(\d+[\.,]\d{2})")


# ---------------------------------
# 5. Parser functie
# ---------------------------------
def parse_invoice_pdf(content: bytes):
    """
    Leest de PDF in met pdfplumber en probeert per regel te bepalen:
    - stof (fabric)
    - optionele stofkleur (fabric_code, bijv. (7))
    - breedte & hoogte in mm
    - factuurprijs
    - raw_line (originele tekst)
    """
    rows = []

    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            for line in text.split("\n"):
                line_stripped = line.strip()
                if not line_stripped:
                    continue

                # --- Stof ---
                fabric = detect_fabric(line_stripped)
                if not fabric:
                    # geen bekende stof gevonden → sla deze regel over
                    continue

                # --- Afmetingen ---
                size_match = SIZE_PATTERN.search(line_stripped)
                if not size_match:
                    continue

                width_mm = int(size_match.group(1))
                height_mm = int(size_match.group(2))

                # --- Prijs ---
                price_match = PRICE_PATTERN.search(line_stripped)
                if not price_match:
                    continue

                price_str = price_match.group(1).replace(",", ".")
                invoice_price = float(price_str)

                # --- Stofkleur (optioneel, bijv. "(7)") ---
                color_code_match = re.search(r"\((\d+)\)", line_stripped)
                fabric_code = color_code_match.group(1) if color_code_match else ""

                # --- Record toevoegen ---
                rows.append(
                    {
                        "fabric": fabric,           # officiële naam uit suppliers.json
                        "fabric_code": fabric_code,
                        "width_mm": width_mm,
                        "height_mm": height_mm,
                        "invoice_price": invoice_price,
                        "raw_line": line_stripped,
                    }
                )

    return rows
