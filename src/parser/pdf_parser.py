import re
import io
from PyPDF2 import PdfReader

def parse_invoice_pdf(pdf_bytes):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    lines = text.splitlines()
    parsed_rows = []

    pattern = re.compile(
        r"""
        GORDIJN\s+Curtain\s+
        (?P<width>\d+)\s*x\s*(?P<height>\d+)\s*mm,\s*
        (?P<fabric>[A-Za-z0-9]+)\s+
        (?P<fabric_code>\d+)\s+
        (?P<color>[A-Za-zÀ-ÿ0-9]+)\s+
        (?P<price>\d+,\d{2})
        """,
        re.VERBOSE
    )

    for line in lines:
        line_fixed = re.sub(r"(\d)(GORDIJN)", r"\1 GORDIJN", line)
        match = pattern.search(line_fixed)
        if match:
            width_mm = int(match.group("width"))
            height_mm = int(match.group("height"))
            fabric = match.group("fabric")
            fabric_code = match.group("fabric_code")
            color = match.group("color")
            invoice_price = float(match.group("price").replace(",", "."))

            parsed_rows.append(
                {
                    "raw_line": line.strip(),
                    "width_mm": width_mm,
                    "height_mm": height_mm,
                    "fabric": fabric,
                    "fabric_code": fabric_code,
                    "color": color,
                    "invoice_price": invoice_price,
                }
            )

    return parsed_rows
