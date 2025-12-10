def round_up_to_matrix(value, staffels):
    """
    Rond een waarde naar boven af op basis van de matrix-staffels.
    Bijvoorbeeld:
    value = 173, staffels = [160,170,180,...] -> 180
    """
    for s in staffels:
        if s >= value:
            return s
    # als waarde groter is dan alle staffels -> kies laatste staffel
    return staffels[-1]
