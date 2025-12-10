import re
import io
from PyPDF2 import PdfReader


def parse_invoice_pdf(pdf_bytes):
    """
    Leest de PDF en haalt per GORDIJN Curtain-regel:
    - breedte_mm
    - hoogte_mm
    - stofnaam
    - stofcode (optioneel)
    - factuurprijs

    Voorbeeldregel:
    '001    1   GORDIJN Curtain 5050 x 2450 mm, Dos Lados 2 almond      14      360,06'
    """

    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text += page_text + "\n"

    lines = text.splitlines()
    parsed_rows = []

    # Maat + stof:
    # Curtain 5050 x 2450 mm, Cosa 7 almond
    pattern = re.compile(
        r"""
        Curtain\s+
        (?P<width>\d{3,5})      # breedte in mm (3-5 cijfers)
        \s*x\s*
        (?P<height>\d{3,5})     # hoogte in mm
        \s*mm[, ]*
        (?P<fabric>[A-Za-z]+)   # stofnaam (Cosa, Corsa, Isola, etc.)
        \s*
        (?P<fabric_code>\d+)?   # optioneel stofnummer
        """,
        re.VERBOSE,
    )

    # Prijs: 360,06 of 1.250,50 etc.
    price_pattern = re.compile(r"(\d{1,3}(?:\.\d{3})*,\d{2})")

    for idx, line in enumerate(lines):
        m = pattern.search(line)
        if not m:
            continue

        width_mm = int(m.group("width"))
        height_mm = int(m.group("height"))
        fabric = m.group("fabric")
        fabric_code = m.group("fabric_code") or ""

        # Prijs zoeken: eerst in dezelfde regel, anders in de volgende paar regels
        price_str = None
        pm = price_pattern.search(line)
        if pm:
            price_str = pm.group(1)
        else:
            # kijk maximaal 3 regels vooruit
            for lookahead in lines[idx:idx+4]:
                pm2 = price_pattern.search(lookahead)
                if pm2:
                    price_str = pm2.group(1)
                    break

        if price_str:
            invoice_price = float(price_str.replace(".", "").replace(",", "."))
        else:
            invoice_price = 0.0  # fallback

        parsed_rows.append(
            {
                "raw_line": line.strip(),
                "width_mm": width_mm,
                "height_mm": height_mm,
                "fabric": fabric,
                "fabric_code": fabric_code,
                "invoice_price": invoice_price,
            }
        )

    return parsed_rows
