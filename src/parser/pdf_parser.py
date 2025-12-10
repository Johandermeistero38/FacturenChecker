import re
import io
from PyPDF2 import PdfReader

def parse_invoice_pdf(pdf_bytes):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text += page_text + "\n"

    lines = text.splitlines()
    parsed_rows = []

    # REGEX:
    # - match breedte & hoogte in mm (3–5 cijfers)
    # - 'x' met willekeurige spaties
    # - mm direct erachter of met spatie
    # - stofnaam = woord + nummer
    # - prijs komt later (we halen alleen maten + stof nu al goed eruit)
    pattern = re.compile(
        r"""
        Curtain\s+
        (?P<width>\d{3,5})      # breedte in mm
        \s*x\s*
        (?P<height>\d{3,5})     # hoogte in mm
        \s*mm[, ]*
        (?P<fabric>[A-Za-z]+)   # stofnaam (Cosa, Corsa, Isola, etc.)
        \s*
        (?P<fabric_code>\d+)?   # optioneel stofnummer
        """,
        re.VERBOSE,
    )

    # Regex voor EUR prijzen: 360,06 / 1.250,50 etc
    price_pattern = re.compile(r"(\d{1,3}(?:\.\d{3})*,\d{2})")

    for line in lines:
        match = pattern.search(line)
        if not match:
            continue

        width_mm = int(match.group("width"))
        height_mm = int(match.group("height"))
        fabric = match.group("fabric")
        fabric_code = match.group("fabric_code") or ""

        # Zoek prijs in dezelfde regel OF toekomstige regels
        price = None
        price_match_line = price_pattern.search(line)
        if price_match_line:
            price = price_match_line.group(1)
        else:
            # zoek in volgende regels
            for lookahead in lines:
                m2 = price_pattern.search(lookahead)
                if m2:
                    price = m2.group(1)
                    break

        if price:
            invoice_price = float(price.replace(".", "").replace(",", "."))
        else:
            invoice_price = 0.0

        parsed_rows.append({
            "raw_line": line.strip(),
            "width_mm": width_mm,
            "height_mm": height_mm,
            "fabric": fabric,
            "fabric_code": fabric_code,
            "invoice_price": invoice_price
        })

    return parsed_rows
