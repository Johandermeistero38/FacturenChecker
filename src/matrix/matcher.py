from src.utils.rounding import round_up_to_matrix

TARGET_FABRIC = "corsa"
PLOOI_ORDER = ["Enkele plooi", "Dubbele plooi", "Wave plooi", "Ring"]

def _format_euro(value):
    if value is None:
        return "N/A"
    s = f"{value:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"€{s}"

def _format_diff(diff):
    if diff is None:
        return ""
    sign = "+" if diff > 0 else "-"
    s = f"{abs(diff):,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{sign}€{s}"

def _collect_plooi_prices(matrices, h, w):
    prices = {}
    key = (float(h), float(w))
    for plooi in PLOOI_ORDER:
        tab = matrices.get(plooi)
        prices[plooi] = tab["prices"].get(key) if tab else None
    return prices

def evaluate_rows(rows, matrices):
    results = []

    staffels_breedte = matrices["Enkele plooi"]["widths"]
    staffels_hoogte = matrices["Enkele plooi"]["heights"]

    for row in rows:
        fabric_raw = row["fabric"]
        fabric = fabric_raw.lower()
        fabric_code = row.get("fabric_code", "")

        # normaliseer cosa → corsa
        if "cosa" in fabric:
            fabric = "corsa"

        width_cm_orig = row["width_mm"] / 10
        height_cm_orig = row["height_mm"] / 10

        width_cm = round_up_to_matrix(width_cm_orig, staffels_breedte)
        height_cm = round_up_to_matrix(height_cm_orig, staffels_hoogte)

        display_stof = f"{fabric_raw} ({fabric_code})" if fabric_code else fabric_raw

        rec = {
            "Regel": row["raw_line"],
            "Stof": display_stof,
            "Afgerond": f"{int(width_cm_orig)} x {int(height_cm_orig)}",
            "Staffel breedte": int(width_cm),
            "Staffel hoogte": int(height_cm),
            "Factuurprijs": _format_euro(row["invoice_price"]),
        }

        if fabric != TARGET_FABRIC:
            for plooi in PLOOI_ORDER:
                rec[plooi] = "N/A"
            rec["Beste plooi"] = ""
            rec["Verschil"] = ""
            results.append(rec)
            continue

        plooi_prices = _collect_plooi_prices(matrices, height_cm, width_cm)

        for plooi in PLOOI_ORDER:
            rec[plooi] = _format_euro(plooi_prices[plooi])

        best_plooi = None
        best_diff = None

        for plooi, price in plooi_prices.items():
            if price is not None:
                diff = row["invoice_price"] - price
                if best_diff is None or abs(diff) < abs(best_diff):
                    best_diff = diff
                    best_plooi = plooi

        rec["Beste plooi"] = best_plooi or ""
        rec["Verschil"] = _format_diff(best_diff) if best_plooi else ""

        results.append(rec)

    return results
