from src.utils.rounding import round_up_to_matrix

TARGET_FABRIC = "corsa"   # intern, we normaliseren 'cosa' -> 'corsa'

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
    if abs(diff) < 0.005:
        sign = ""
        abs_val = 0.0
    else:
        sign = "+" if diff > 0 else "-"
        abs_val = abs(diff)

    s = f"{abs_val:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{sign}€{s}"


def _collect_plooi_prices(matrices, height_cm, width_cm):
    prices = {}
    key = (float(height_cm), float(width_cm))

    for plooi in PLOOI_ORDER:
        info = matrices.get(plooi)
        if info is None:
            prices[plooi] = None
        else:
            prices[plooi] = info["prices"].get(key)

    return prices


def evaluate_rows(rows, matrices):
    results = []

    # staffels (van Enkele plooi; de andere tabs gebruiken dezelfde maten)
    staffels_breedte = matrices["Enkele plooi"]["widths"]
    staffels_hoogte = matrices["Enkele plooi"]["heights"]

    for row in rows:
        fabric_raw = row["fabric"]
        fabric_norm = fabric_raw.lower()
        fabric_code = row.get("fabric_code", "")

        # 'Cosa' normaliseren naar 'Corsa'
        if "cosa" in fabric_norm:
            fabric_norm = "corsa"

        width_mm = row["width_mm"]
        height_mm = row["height_mm"]
        invoice_price = row["invoice_price"]

        # mm -> cm
        width_cm_orig = width_mm / 10.0
        height_cm_orig = height_mm / 10.0

        # Afronden op staffels (altijd naar boven)
        width_cm = round_up_to_matrix(width_cm_orig, staffels_breedte)
        height_cm = round_up_to_matrix(height_cm_orig, staffels_hoogte)

        stof_display = f"{fabric_raw} ({fabric_code})" if fabric_code else fabric_raw

        record = {
            "Regel": row["raw_line"],
            "Stof": stof_display,
            "Afgerond": f"{int(width_cm)} x {int(height_cm)}",
            "Factuurprijs": _format_euro(invoice_price),
        }

        # Niet-Corsa: nog geen matrix → alles N/A
        if fabric_norm != TARGET_FABRIC:
            for plooi in PLOOI_ORDER:
                record[plooi] = "N/A"
            record["Beste plooi"] = ""
            record["Verschil"] = ""
            results.append(record)
            continue

        # Wel Corsa/Cosa → alle plooi-prijzen ophalen
        plooi_prices = _collect_plooi_prices(matrices, height_cm, width_cm)

        for plooi in PLOOI_ORDER:
            record[plooi] = _format_euro(plooi_prices.get(plooi))

        # Beste plooi bepalen (kleinste absolute verschil)
        best_plooi = None
        best_diff = None

        for plooi, price in plooi_prices.items():
            if price is None:
                continue
            diff = invoice_price - price
            if best_diff is None or abs(diff) < abs(best_diff):
                best_diff = diff
                best_plooi = plooi

        if best_plooi is None:
            record["Beste plooi"] = ""
            record["Verschil"] = ""
        else:
            record["Beste plooi"] = best_plooi
            record["Verschil"] = _format_diff(best_diff)

        results.append(record)

    return results
