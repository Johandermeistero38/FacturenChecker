import pandas as pd


def load_price_matrices_from_excel(path):
    """
    Leest een Excel bestand met meerdere tabbladen (Enkele plooi, Dubbele plooi, Wave plooi, Ring)
    en zet elke matrix om naar een gestandaardiseerd formaat:

    {
        "Enkele plooi": {
            "widths": [...],
            "heights": [...],
            "grid": [[...], [...], ...]
        },
        "Dubbele plooi": {...},
        ...
    }
    """

    xls = pd.ExcelFile(path)
    matrices = {}

    for sheet_name in xls.sheet_names:

        df = pd.read_excel(path, sheet_name=sheet_name, header=None)

        # -----------------------------
        # Controle: is de sheet leeg?
        # -----------------------------
        if df.empty:
            continue

        # -----------------------------
        # 1. Breedtes staan in rij 0, vanaf kolom 1
        # -----------------------------
        widths = df.iloc[0, 1:].tolist()

        # -----------------------------
        # 2. Hoogtes staan in kolom 0, vanaf rij 1
        # -----------------------------
        heights = df.iloc[1:, 0].tolist()

        # -----------------------------
        # 3. De daadwerkelijke prijs-matrix
        # -----------------------------
        grid = df.iloc[1:, 1:].values.tolist()

        # -----------------------------
        # Alles converteren naar floats
        # -----------------------------
        def to_float(v):
            try:
                return float(str(v).replace(",", "."))
            except:
                return None

        widths = [to_float(v) for v in widths]
        heights = [to_float(v) for v in heights]

        clean_grid = []
        for row in grid:
            clean_grid.append([to_float(v) for v in row])

        matrices[sheet_name] = {
            "widths": widths,
            "heights": heights,
            "grid": clean_grid
        }

    return matrices
