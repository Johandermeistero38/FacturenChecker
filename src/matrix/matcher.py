from src.utils.rounding import round_up_to_matrix

TARGET_FABRIC = "cosa"

# Plooi-volgorde zoals kolommen moeten verschijnen
PLOOI_ORDER = ["Enkele plooi", "Dubbele plooi", "Wave plooi", "Ring"]


def _format_euro(value):
    """Zet een getal om naar €1.234,56 formaat. None -> 'N/A'."""
    if value is None:
        return "N/A"
    s = f"{value:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"€{s}"


def _format_diff(diff):
    """Verschil tonen als '+€1,23', '-€0,50', '€0,00' of ''."""
    if diff is None:
        return ""
    if abs(diff) < 0.005:
        # praktisch 0
        sign = ""
        abs_val = 0.0
    else:
        sign = "+" if diff > 0 else "-"
        abs_val = abs(diff)

    s = f"{abs_val:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{sign}€{s}"


def _collect_plooi_prices(matrices, height_cm, width_cm):
    """
    Haal voor alle plooitypes de matrixprijs op uit:
    matrices[plooi]["prices"]   (hoogte, breedte) -> prijs
    """
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
    """
    Bouwt de volledige output:
    - Regel
    - Stof
    - Afgerond
    - Factuurprijs
    - Enkele plooi
    - Dubbele plooi
    - Wave plooi
    - Ring
    - Beste plooi
    - Verschil
    """
    results = []

    # Haal matrixstaffels op (zelfde voor alle plooien)
    staffels_breedte = matrices["Enkele plooi"]["widths"]
    staffels_hoogte = matrices["Enkele plooi"]["heights"]

    for row in rows:
        fabric_raw = row["fabric"]
        fabric = fabric_raw.lower()
        fabric_code = row.get("fabric_code", "")
        width_mm = row["width_mm"]
        height_mm = row["height_mm"]
        invoice_price = row["invoice_price"]

        # Converteer mm naar cm
        width_cm_original = width_mm / 10
        height_cm_original = height_mm / 10

        # Afronden volgens staffels → altijd naar boven
        width_cm = round_up_to_matrix(width_cm_original, staffels_breedte)
        height_cm = round_up_to_matrix(height_cm_original, staffels_hoogte)

        # Stofnaam tonen als: "cosa (7)"
        stof_display = (
            f"{fabric_raw} ({fabric_code})" if fabric_code else fabric_raw
        )

        # Basiskolommen
        record = {
            "Regel": row["raw_line"],
            "Stof": stof_display,
            "Afgerond": f"{int(width_cm)} x {int(height_cm)}",
            "Factuurprijs": _format_euro(invoice_price),
        }

        # NIET cosa → alleen N/A vullen
        if fabric != TARGET_FABRIC:
            for plooi in PLOOI_ORDER:
                record[plooi] = "N/A"
            record["Beste plooi"] = ""
            record["Verschil"] = ""
            results.append(record)
            continue

        # cosa → haal alle plooiprijzen op
        plooi_prices = _collect_plooi_prices(matrices, height_cm, width_cm)

        # Kolommen toevoegen
        for plooi in PLOOI_ORDER:
            record[plooi] = _format_euro(plooi_prices[plooi])

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

        # Beste plooi + verschil invullen
        if best_plooi is None:
            record["Beste plooi"] = ""
            record["Verschil"] = ""
        else:
            record["Beste plooi"] = best_plooi
            record["Verschil"] = _format_diff(best_diff)

        results.append(record)

    return results
