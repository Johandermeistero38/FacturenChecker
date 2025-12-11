def evaluate_rows(rows, matrices):
    """
    Vergelijkt elke factuurregel met de juiste prijsmatrix en berekent plooi-prijzen.
    """

    results = []

    for row in rows:

        stof = row["stof"]
        breedte = row["breedte"]
        hoogte = row["hoogte"]
        factuurprijs = row["prijs"]

        # Normalize stofnaam
        stof_norm = stof.lower().strip()

        # Matching stof op basis van beginsel
        chosen_matrix = None
        for key in matrices.keys():
            if stof_norm.startswith(key):
                chosen_matrix = matrices[key]
                break

        if chosen_matrix is None:
            results.append({
                "Stof": stof,
                "Afgerond": f"{breedte} x {hoogte}",
                "Factuurprijs": factuurprijs,
                "Enkele plooi": "N/A",
                "Dubbele plooi": "N/A",
                "Wave plooi": "N/A",
                "Ring": "N/A",
                "Beste plooi": "Geen matrix",
                "Verschil": "N/A"
            })
            continue

        df = chosen_matrix["df"]
        index_vals = chosen_matrix["index"]
        col_vals = chosen_matrix["columns"]

        # Stap 1: afronden volgens staffels
        def round_to_staffel(value, staffel_list):
            return min(staffel_list, key=lambda x: abs(x - value))

        rounded_w = round_to_staffel(breedte, col_vals)
        rounded_h = round_to_staffel(hoogte, index_vals)

        plooi_prices = {}

        # Elke plooi in matrix lezen:
        for plooi, df in chosen_matrix["matrices"].items():

            print("\n========== DEBUG ==========")
            print("Stof:", stof)
            print("Plooi:", plooi)
            print("Rounded W:", rounded_w, type(rounded_w))
            print("Rounded H:", rounded_h, type(rounded_h))
            print("DF index type:", type(df.index[0]))
            print("DF col type:", type(df.columns[0]))
            print("DF shape:", df.shape)

            try:
                price = df.loc[rounded_h, rounded_w]
                plooi_prices[plooi] = price
            except Exception as e:
                print("LOOKUP ERROR:", e)
                plooi_prices[plooi] = "N/A"

        # Bepaal beste plooi:
        beste_plooi = "Niet zeker"
        verschil = "N/A"

        # Filter alleen plooi-prijzen die echt bestaan:
        valid_prices = {p: v for p, v in plooi_prices.items() if isinstance(v, (int, float))}

        if valid_prices:
            # Zoek kleinste verschil
            diffs = {p: abs(factuurprijs - v) for p, v in valid_prices.items()}
            beste_plooi = min(diffs, key=diffs.get)
            verschil = f"{factuurprijs - valid_prices[beste_plooi]:+.2f}"

        results.append({
            "Stof": stof,
            "Afgerond": f"{rounded_w} x {rounded_h}",
            "Factuurprijs": factuurprijs,
            "Enkele plooi": plooi_prices.get("Enkele plooi", "N/A"),
            "Dubbele plooi": plooi_prices.get("Dubbele plooi", "N/A"),
            "Wave plooi": plooi_prices.get("Wave plooi", "N/A"),
            "Ring": plooi_prices.get("Ring", "N/A"),
            "Beste plooi": beste_plooi,
            "Verschil": verschil
        })

    return results
