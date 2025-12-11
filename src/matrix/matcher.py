from src.utils.rounding import round_up_to_matrix

TARGET_FABRIC = "corsa"  # intern label; 'cosa' wordt hierna genormaliseerd
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

    staffels_breedte = matrices["Enkele plooi"]["widths"]
    staffels_hoogte = matrices["Enkele plooi"]["heights"]

    for row in rows:
        fabric_raw = row["fabric"]
        fabric_norm = fabric_raw.lower()
        fabric_code = row.get("fabric_code", "")

        # 'Cosa' -> 'Corsa'
        if "cosa" in fabric_norm:
            fabric_norm = "corsa"

        width_mm = row["width_mm"]
        height_mm = row["height_mm"]
        invoice_price = row["invoice_price"]

        # mm -> cm
        width_cm_orig = width_mm / 10.0
        height_cm_orig = height_mm / 10.0

        # afronden op staffels
        width_cm = round_up_to_matrix(width_cm_orig, staffels_breedte)
        height_cm = round_up_to_matrix(height_cm_orig, staffels_hoogte)

        stof_display = f"{fabric_raw} ({fabric_code})" if fabric_code else fabric_raw

        rec = {
            "Regel": row["raw_line"],
            "Stof": stof_display,
            "Afgerond": f"{int(width_cm_orig)} x {int(height_cm_orig)}",
            "Staffel breedte": int(width_cm),
            "Staffel hoogte": int(height_cm),
            "Factuurprijs": _format_euro(invoice_price),
        }

        # Nog geen matrix beschikbaar voor andere stoffen dan Corsa/Cosa
        if fabric_norm != TARGET_FABRIC:
            for plooi in PLOOI_ORDER:
                rec[plooi] = "N/A"
            rec["Plooi match"] = ""
            rec["Verschil"] = ""
            results.append(rec)
            continue

        # Prijzen uit matrix ophalen
        plooi_prices = _collect_plooi_prices(matrices, height_cm, width_cm)

        for plooi in PLOOI_ORDER:
            rec[plooi] = _format_euro(plooi_prices.get(plooi))

        # --------------------------
        # Nieuwe plooi-match logica
        # --------------------------
        direct_match_plooi = None
        direct_match_diff = None
        closest_plooi = None
        closest_diff = None

        for plooi, price in plooi_prices.items():
            if price is None:
                continue

            diff = invoice_price - price

            # dichtstbijzijnde plooi (voor "Niet zeker")
            if closest_diff is None or abs(diff) < abs(closest_diff):
                closest_diff = diff
                closest_plooi = plooi

            # directe match (bv. exact gelijk tot op 1 cent)
            if abs(diff) < 0.01:
                if direct_match_diff is None or abs(diff) < abs(direct_match_diff):
                    direct_match_diff = diff
                    direct_match_plooi = plooi

        if direct_match_plooi is not None:
            rec["Plooi match"] = direct_match_plooi
            rec["Verschil"] = _format_diff(direct_match_diff)
        elif closest_plooi is not None:
            rec["Plooi match"] = "Niet zeker"
            rec["Verschil"] = _format_diff(closest_diff)
        else:
            rec["Plooi match"] = ""
            rec["Verschil"] = ""

        results.append(rec)

    return results
