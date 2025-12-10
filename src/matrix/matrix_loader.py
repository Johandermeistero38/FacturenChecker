import pandas as pd

def load_price_matrices_from_excel(excel_file):
    """
    Leest JOUW matrix exact zoals de structuur is:
    - Rij 2 bevat breedtes (Excel index 1)
    - Kolom A bevat hoogtes (Excel index 0)
    - Prijzen starten op rij 3, kolom B (index 2:, 1:)
    """
    matrices = {}
    xls = pd.ExcelFile(excel_file)

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet, header=None)

        # Breedtes (rij 1 in pandas = Excel rij 2)
        widths = df.iloc[1, 1:].tolist()
        widths = sorted([float(x) for x in widths])

        # Hoogtes (rij 2 in pandas = Excel rij 3)
        heights = df.iloc[2:, 0].tolist()
        heights = sorted([float(x) for x in heights])

        # Prijs tabel
        price_df = df.iloc[2:, 1:]
        price_df.columns = widths
        price_df.index = heights

        lookup = {}
        for h in heights:
            for w in widths:
                v = price_df.at[h, w]
                if not pd.isna(v):
                    lookup[(h, w)] = float(v)

        matrices[sheet] = {
            "widths": widths,
            "heights": heights,
            "prices": lookup
        }

    return matrices
