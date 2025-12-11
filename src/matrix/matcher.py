from src.database.supplier_db import load_suppliers, get_matrix_path_for_fabric
from src.matrix.matrix_loader import load_price_matrices_from_excel
from src.utils.rounding import round_up_to_matrix

PLOOI_TYPES = ["Enkele plooi", "Dubbele plooi", "Wave plooi", "Ring"]


def _format_euro(value):
    if value is None:
        return "N/A"
    return f"€{value:.2f}".replace(".", ",")


def _format_diff(diff):
    if diff is None:
        return ""
    sign = "+" if diff > 0 else ""
    return f"{sign}€{diff:.2f}".replace(".", ",")


def evaluate_rows(rows, supplier_key="toppoint", progress_callback=None):
    """
    Voor ELKE regel:
    - juiste stof bepalen
    - juiste matrix voor die stof laden
    - staffelmaten zoeken
    - plooiprijzen ophalen
    - match bepalen

    progress_callback(optional): functie die wordt aangeroepen als
    progress_callback(done, total)
    """

    suppliers = load_suppliers()
    supplier = suppliers[supplier_key]

    results = []
    total = len(rows)

    for idx, row in enumerate(rows):
        fabric = row["fabric"]
        width_mm = row["width_mm"]
        height_mm = row["height_mm"]
        factuurprijs = row["invoice_price"]

        # -------------------------
        # 1. Probeer matrix te vinden voor deze stof
        # -------------------------
        try:
            matrix_path = get_matrix_path_for_fabric(supplier, fabric)
            matrices = load_price_matrices_from_excel(matrix_path)
            matrix_ok = True
        except Exception:
            matrices = None
            matrix_ok = False

        # -------------------------
        # 2. cm afronden op staffels (alleen als matrix bestaat)
        # -------------------------
        width_cm = width_mm / 10
        height_cm = height_mm / 10

        if matrix_ok:
            bw = matrices["Enkele plooi"]["widths"]
            bh = matrices["Enkele plooi"]["heights"]

            w_round = round_up_to_matrix(width_cm, bw)
            h_round = round_up_to_matrix(height_cm, bh)
        else:
            w_round = None
            h_round = None

        # -------------------------
        # 3. Record basis
        # -------------------------
        rec = {
            "Regel": row["raw_line"],
            "Stof": fabric,
            "Breedte/Hoogte (cm)": f"{int(width_cm)} x {int(height_cm)}",
            "Staffel breedte": int(w_round) if w_round else "N/A",
            "Staffel hoogte": int(h_round) if h_round else "N/A",
            "Factuurprijs": _format_euro(factuurprijs),
        }

        # -------------------------
        # 4. Geen matrix beschikbaar?
        # -------------------------
        if not matrix_ok:
            for plooi in PLOOI_TYPES:
                rec[plooi] = "N/A"
            rec["Plooi match"] = "Geen matrix"
            rec["Verschil"] = ""
            results.append(rec)

            if progress_callback:
                progress_callback(idx + 1, total)
            continue

        # -------------------------
        # 5. Plooiprijzen ophalen
        # -------------------------
        plooi_prices = {}

        for plooi in PLOOI_TYPES:
            mat = matrices.get(plooi)
            if mat is None:
                plooi_prices[plooi] = None
                rec[plooi] = "N/A"
                continue

            if w_round in mat["widths"] and h_round in mat["heights"]:
                row_idx = mat["heights"].index(h_round)
                col_idx = mat["widths"].index(w_round)
                price = mat["grid"][row_idx][col_idx]
                plooi_prices[plooi] = price
                rec[plooi] = _format_euro(price)
            else:
                plooi_prices[plooi] = None
                rec[plooi] = "N/A"

        # -------------------------
        # 6. Beste plooi of "Niet zeker"
        # -------------------------
        direct_match = None
        closest_match_plooi = None
        closest_diff = None

        for plooi, price in plooi_prices.items():
            if price is None:
                continue

            diff = factuurprijs - price

            # directe match
            if abs(diff) < 0.01:
                direct_match = (plooi, diff)
                break

            # dichtstbijzijnde match
            if closest_diff is None or abs(diff) < abs(closest_diff):
                closest_diff = diff
                closest_match_plooi = plooi

        if direct_match:
            rec["Plooi match"] = direct_match[0]
            rec["Verschil"] = _format_diff(direct_match[1])
        else:
            rec["Plooi match"] = "Niet zeker" if closest_match_plooi else "N/A"
            rec["Verschil"] = _format_diff(closest_diff) if closest_diff else ""

        results.append(rec)

        # -------------------------
        # 7. Progressie bijwerken
        # -------------------------
        if progress_callback:
            progress_callback(idx + 1, total)

    return results
