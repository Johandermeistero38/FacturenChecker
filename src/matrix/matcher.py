from src.utils.rounding import round_to_10_up

TARGET_FABRIC = "corsa"

# In welke volgorde we de plooi-kolommen willen tonen
PLOOI_ORDER = ["Enkele plooi", "Dubbele plooi", "Wave plooi", "Ring"]


def _format_euro(value):
    """Getal -> '€1.234,56' ; None -> 'N/A'."""
    if value is None:
        return "N/A"
    # standaard Python gebruikt punt als decimaal, we draaien dat om
    s = f"{value:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"€{s}"


def _format_diff(diff):
    """Verschil -> '+€1,23' / '-€0,50' / '€0,00' ; None -> ''."""
    if diff is None:
        return ""
    if abs(diff) < 0.005:
        # praktisch nul
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
    Haal voor alle plooi-types de prijs op.
    Geeft een dict terug:
        { 'Enkele plooi': prijs of None, ... }
    """
    prices = {}
    key = (height_cm, width_cm)

    for plooi_name in PLOOI_ORDER:
        lookup = matrices.get(plooi_name)
        if lookup is None:
            prices[plooi_name] = None
            continue
        price = lookup.get(key)
        prices[plooi_name] = float(price) if price is not None else None

    return prices


def evaluate_rows(rows, matrices):
    """
    Bouwt de volledige output-structuur voor in de tabel:
    Kolommen:
      Regel, Stof, Afgerond, Factuurprijs,
      Enkele plooi, Dubbele plooi, Wave plooi, Ring,
      Beste plooi, Verschil
    """
    results = []

    for row in rows:
        fabric_name_raw = row["fabric"]
        fabric = fabric_name_raw.lower()
        fabric_code = row.get("fabric_code", "")
        width_mm = row["width_mm"]
        height_mm = row["height_mm"]
        invoice_price = row["invoice_price"]

        # afronden naar 10 cm
        width_cm = round_to_10_up(width_mm)
        height_cm = round_to_10_up(height_mm)

        # Stof-tekst (bijv. "Corsa (7)")
        stof_display = (
            f"{fabric_name_raw} ({fabric_code})" if fabric_code else fabric_name_raw
        )

        # Basisrecord
        record = {
            "Regel": row["raw_line"],
            "Stof": stof_display,
            "Afgerond": f"{int(width_cm)} x {int(height_cm)}",
            "Factuurprijs": _format_euro(invoice_price),
        }

        # ---- NIET-CORSA: alleen tonen, geen prijzen ----
        if fabric != TARGET_FABRIC:
            for plooi_name in PLOOI_ORDER:
                record[plooi_name] = "N/A"

            record["Beste plooi"] = ""
            record["Verschil"] = ""
            results.append(record)
            continue

        # ---- CORSA: alle 4 plooi-prijzen ophalen ----
        plooi_prices = _collect_plooi_prices(matrices, height_cm, width_cm)

        # Voeg alle plooi-prijzen als kolommen toe
        for plooi_name in PLOOI_ORDER:
            record[plooi_name] = _format_euro(plooi_prices.get(plooi_name))

        # Beste plooi bepalen (kleinste absolute verschil)
        best_plooi = None
        best_price = None
        best_diff = None

        for plooi_name, price in plooi_prices.items():
            if price is None:
                continue
            diff = invoice_price - price
            if best_diff is None or abs(diff) < abs(best_diff):
                best_diff = diff
                best_price = price
                best_plooi = plooi_name

        if best_plooi is None:
            # geen enkele plooi had een matrixprijs
            record["Beste plooi"] = ""
            record["Verschil"] = ""
        else:
            record["Beste plooi"] = best_plooi
            record["Verschil"] = _format_diff(best_diff)

        results.append(record)

    return results
