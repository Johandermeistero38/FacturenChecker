import pandas as pd
from src.database.supplier_db import get_matrix_path_for_fabric
from src.matrix.matrix_loader import load_price_matrices_from_excel
from src.utils.rounding import round_up_to_matrix

PLOOI_TYPES = ["Enkele plooi", "Dubbele plooi", "Wave plooi", "Ring"]


def evaluate_rows(rows, supplier_key="toppoint", progress_callback=None):
    """
    Vergelijkt elke gordijnregel met de juiste prijsmatrix.
    Returned een lijst records geschikt voor DataFrame.
    """
    results = []
    total = len(rows)

    for idx, row in enumerate(rows):
        if progress_callback:
            progress_callback((idx + 1) / total)

        fabric = row["fabric"]
        width_mm = row["width_mm"]
        height_mm = row["height_mm"]
        invoice_price = row["invoice_price"]

        matrix_path = get_matrix_path_for_fabric(supplier_key, fabric)
        if not matrix_path:
            results.append({
                "Stof": fabric,
                "Afgerond": "N/A",
                "Factuurprijs": invoice_price,
                "Enkele plooi": "N/A",
                "Dubbele plooi": "N/A",
                "Wave plooi": "N/A",
                "Ring": "N/A",
                "Match": "❌ Geen matrix gevonden",
                "Verschil": "N/A"
            })
            continue

        try:
            matrices, width_steps, height_steps = load_price_matrices_from_excel(matrix_path)
        except Exception as e:
            results.append({
                "Stof": fabric,
                "Afgerond": "N/A",
                "Factuurprijs": invoice_price,
                "Enkele plooi": "N/A",
                "Dubbele plooi": "N/A",
                "Wave plooi": "N/A",
                "Ring": "N/A",
                "Match": f"❌ Matrix fout: {e}",
                "Verschil": "N/A"
            })
            continue

        rounded_w = round_up_to_matrix(width_mm / 10, width_steps)
        rounded_h = round_up_to_matrix(height_mm / 10, height_steps)

        plooi_prices = {}
        best_match = None
        best_diff = None

        for plooi in PLOOI_TYPES:
            df = matrices.get(plooi)
            if df is None:
                plooi_prices[plooi] = "N/A"
                continue

           try:
    print("DEBUG df type:", type(df))
    print("DEBUG index type:", type(df.index[0]))
    print("DEBUG col type:", type(df.columns[0]))
    print("DEBUG rounded_w:", rounded_w, type(rounded_w))
    print("DEBUG rounded_h:", rounded_h, type(rounded_h))

    price = df.loc[rounded_h, rounded_w]
except Exception:
    plooi_prices[plooi] = "N/A"
    continue


            plooi_prices[plooi] = price

            diff = invoice_price - price
            if best_diff is None or abs(diff) < abs(best_diff):
                best_diff = diff
                best_match = plooi

        formatted_diff = f"€{best_diff:+.2f}" if best_diff is not None else "N/A"

        results.append({
            "Stof": fabric,
            "Afgerond": f"{rounded_w} x {rounded_h}",
            "Factuurprijs": f"€{invoice_price:.2f}",
            "Enkele plooi": f"€{plooi_prices['Enkele plooi']:.2f}" if plooi_prices["Enkele plooi"] != "N/A" else "N/A",
            "Dubbele plooi": f"€{plooi_prices['Dubbele plooi']:.2f}" if plooi_prices["Dubbele plooi"] != "N/A" else "N/A",
            "Wave plooi": f"€{plooi_prices['Wave plooi']:.2f}" if plooi_prices["Wave plooi"] != "N/A" else "N/A",
            "Ring": f"€{plooi_prices['Ring']:.2f}" if plooi_prices["Ring"] != "N/A" else "N/A",
            "Match": best_match if best_match else "Niet zeker",
            "Verschil": formatted_diff
        })

    return results
