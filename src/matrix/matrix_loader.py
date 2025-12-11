import pandas as pd

def load_price_matrices_from_excel(excel_file):
    matrices = {}
    xls = pd.ExcelFile(excel_file)

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet, header=None)

        # verwijder lege rijen / kolommen
        df = df.dropna(axis=0, how="all")
        df = df.dropna(axis=1, how="all")

        # eerste rij = breedtes, maar kolom A is leeg → breedtes beginnen bij kolom B
        widths = []
        for val in df.iloc[0, 1:].tolist():
            if isinstance(val, (int, float)):
                widths.append(float(val))

        # eerste kolom vanaf rij 2 = hoogtes
        heights = []
        for val in df.iloc[1:, 0].tolist():
            if isinstance(val, (int, float)):
                heights.append(float(val))

        # prijsgebied = B2 t/m einde
        price_df = df.iloc[1:1+len(heights), 1:1+len(widths)]
        price_df.columns = widths
        price_df.index = heights

        lookup = {}
        for h in heights:
            for w in widths:
                v = price_df.at[h, w]
                if not pd.isna(v):
                    lookup[(h, w)] = float(v)

        matrices[sheet] = {
            "widths": sorted(widths),
            "heights": sorted(heights),
            "prices": lookup
        }

    return matrices
import pandas as pd

def load_price_matrices_from_excel(excel_file):
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
    xls = pd.ExcelFile(excel_file)

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet, header=None)

        # verwijder lege rijen / kolommen
        df = df.dropna(axis=0, how="all")
        df = df.dropna(axis=1, how="all")

        # eerste rij = breedtes, maar kolom A is leeg → breedtes beginnen bij kolom B
        widths = []
        for val in df.iloc[0, 1:].tolist():
            if isinstance(val, (int, float)):
                widths.append(float(val))

        # eerste kolom vanaf rij 2 = hoogtes
        heights = []
        for val in df.iloc[1:, 0].tolist():
            if isinstance(val, (int, float)):
                heights.append(float(val))

        # prijsgebied = B2 t/m einde
        price_df = df.iloc[1:1+len(heights), 1:1+len(widths)]
        price_df.columns = widths
        price_df.index = heights

        lookup = {}
        for h in heights:
            for w in widths:
                v = price_df.at[h, w]
                if not pd.isna(v):
                    lookup[(h, w)] = float(v)

        matrices[sheet] = {
            "widths": sorted(widths),
            "heights": sorted(heights),
            "prices": lookup
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
