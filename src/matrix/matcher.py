import re
import math

# Herken stof uit regel
def detect_stof(row_text, available_matrices):
    row_text = row_text.lower()

    for stof in available_matrices:
        if stof in row_text:
            return stof
    return None


def round_to_matrix(value):
    value = int(value)
    remainder = value % 10
    if remainder == 0:
        return value
    return value + (10 - remainder)


def extract_sizes(text):
    match = re.search(r"(\d+)\s*[xX]\s*(\d+)", text)
    if not match:
        return None, None

    b = int(match.group(1)) / 10  # mm → cm
    h = int(match.group(2)) / 10

    return round_to_matrix(b), round_to_matrix(h)


def evaluate_rows(rows, matrices):
    results = []

    for row in rows:
        regel = row["text"]
        prijs = row["price"]

        stof = detect_stof(regel, matrices.keys())
        if not stof:
            results.append({
                "Stof": "Onbekend",
                "Regel": regel,
                "Factuurprijs": prijs,
                "Opmerking": "Stof niet gevonden"
            })
            continue

        breedte, hoogte = extract_sizes(regel)
        if not breedte or not hoogte:
            results.append({
                "Stof": stof,
                "Regel": regel,
                "Factuurprijs": prijs,
                "Opmerking": "Maten niet gevonden"
            })
            continue

        matrix = matrices[stof]

        try:
            matrix_prijs = matrix.loc[hoogte, breedte]
        except:
            matrix_prijs = None

        results.append({
            "Stof": stof,
            "Regel": regel,
            "Breedte": breedte,
            "Hoogte": hoogte,
            "Matrixprijs": matrix_prijs,
            "Factuurprijs": prijs,
            "Verschil": round(prijs - matrix_prijs, 2) if matrix_prijs else "N/A"
        })

    return results
