import re
import io
from PyPDF2 import PdfReader

def parse_invoice_pdf(pdf_bytes):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        txt = page.extract_text() or ""
        text += txt + "\n"

    lines = text.splitlines()
    parsed_rows = []

    # Regex om GORDIJN Curtain regels te herkennen
    pattern = re.compile(
        r"""
        Curtain\s+
        (?P<width>\d{3,5})\s*x\s*(?P<height>\d{3,5})\s*mm  # maten in mm
        .*?                                              # alles ertussen
        (?P<fabric>[A-Za-z]+)\s*(?P<fabric_code>\d+)?    # stof + optionele code
        """,
        re.VERBOSE,
    )

    # Regex voor prijzen (EU formaat)
    price_pattern = re.compile(r"(\d{1,3}(?:\.\d{3})*,\d{2})")

    for idx, line in enumerate(lines):
        m = pattern.search(line)
        if not m:
            continue

        width_mm = int(m.group("width"))
        height_mm = int(m.group("height"))
        fabric = m.group("fabric")
        fabric_code = m.group("fabric_code") or ""

        price = None
        price_match = price_pattern.search(line)
        if price_match:
            price = price_match.group(1)
        else:
            # zoek maximaal drie regels verder
            for ahead in lines[idx:idx+4]:
                pm = price_pattern.search(ahead)
                if pm:
                    price = pm.group(1)
                    break

        invoice_price = float(price.replace(".", "").replace(",", ".")) if price else 0.0

        parsed_rows.append({
            "raw_line": line.strip(),
            "width_mm": width_mm,
            "height_mm": height_mm,
            "fabric": fabric,
            "fabric_code": fabric_code,
            "invoice_price": invoice_price
        })

    return parsed_rows
