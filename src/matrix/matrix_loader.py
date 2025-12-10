import pandas as pd


def load_price_matrices_from_excel(excel_file):
    """
    VEILIGE LOADER:
    - verwijdert lege kolommen
    - verwijdert lege rijen
    - detecteert automatisch eerste rij met breedtes
    - detecteert automatisch eerste kolom met hoogtes
    - bouwt een zuivere staffel-matrix
    """

    matrices = {}
    xls = pd.ExcelFile(excel_file)

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet, header=None)

        # Verwijder volledig lege kolommen en rijen
        df = df.dropna(axis=0, how="all")
        df = df.dropna(axis=1, how="all")

        # Breedtes staan ALTIJD in de eerste dataframe-rij → index 0
        widths = []
        for val in df.iloc[0, 1:].tolist():
            if pd.isna(val):
                continue
            if isinstance(val, (int, float)):
                widths.append(float(val))

        # Hoogtes staan ALTIJD in de eerste dataframe-kolom → index 0
        heights = []
        for val in df.iloc[1:, 0].tolist():
            if pd.isna(val):
                continue
            if isinstance(val, (int, float)):
                heights.append(float(val))

        # Snijd het prijsgebied exact uit
        price_area = df.iloc[1:1+len(heights), 1:1+len(widths)]

        # Bouw lookup-tabel
        lookup = {}
        for i, h in enumerate(heights):
            for j, w in enumerate(widths):
                val = price_area.iat[i, j]
                if not pd.isna(val):
                    lookup[(h, w)] = float(val)

        matrices[sheet] = {
            "widths": sorted(widths),
            "heights": sorted(heights),
            "prices": lookup
        }

    return matrices
