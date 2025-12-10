from src.utils.rounding import round_to_10_up

TARGET_FABRIC = "corsa"

def find_matrix_price(matrices, height_cm, width_cm):
    for plooi_name, lookup in matrices.items():
        key = (height_cm, width_cm)
        if key in lookup:
            return plooi_name, lookup[key]
    return None, None


def evaluate_rows(rows, matrices):
    results = []

    for row in rows:
        fabric = row["fabric"].lower()
        width_cm = round_to_10_up(row["width_mm"])
        height_cm = round_to_10_up(row["height_mm"])
        invoice_price = row["invoice_price"]

        if fabric != TARGET_FABRIC:
            results.append({
                "Regel": row["raw_line"],
                "Stof": row["fabric"],
                "Afgerond": f"{int(width_cm)} x {int(height_cm)}",
                "Factuurprijs": invoice_price,
                "Matrixprijs": None,
                "Plooi": None,
                "Status": "Geen match (andere stof)",
                "Verschil": None
            })
            continue

        plooi, matrix_price = find_matrix_price(matrices, height_cm, width_cm)

        if matrix_price is None:
            results.append({
                "Regel": row["raw_line"],
                "Stof": row["fabric"],
                "Afgerond": f"{int(width_cm)} x {int(height_cm)}",
                "Factuurprijs": invoice_price,
                "Matrixprijs": None,
                "Plooi": None,
                "Status": "Geen match (Corsa – geen prijs gevonden)",
                "Verschil": None
            })
            continue

        diff = round(invoice_price - matrix_price, 2)
        status = "OK" if abs(diff) < 0.01 else "Prijsverschil"

        results.append({
            "Regel": row["raw_line"],
            "Stof": row["fabric"],
            "Afgerond": f"{int(width_cm)} x {int(height_cm)}",
            "Factuurprijs": invoice_price,
            "Matrixprijs": matrix_price,
            "Plooi": plooi,
            "Status": status,
            "Verschil": diff
        })

    return results
