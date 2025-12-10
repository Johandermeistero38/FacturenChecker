def round_up_to_matrix(value, staffels):
    """
    Rond een waarde (in cm) naar boven af op basis van staffels.

    Voorbeeld:
        value = 245, staffels = [240, 250, 260]
        -> 250

        value = 505, staffels = [500, 510, 520]
        -> 510
    """
    staffels_sorted = sorted(float(s) for s in staffels)

    for s in staffels_sorted:
        if value <= s + 1e-9:
            return s

    # groteren dan alle staffels -> hoogste staffel
    return staffels_sorted[-1]
