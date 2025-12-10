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
