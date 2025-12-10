def round_up_to_matrix(value, staffels):
    staffels_sorted = sorted(float(s) for s in staffels)

    for s in staffels_sorted:
        if value <= s + 1e-9:
            return s

    return staffels_sorted[-1]  # grootste staffel
