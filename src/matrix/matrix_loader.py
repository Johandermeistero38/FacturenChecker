import pandas as pd


def load_price_matrices_from_excel(excel_file):
    """
    Leest jouw matrix exact zoals opgebouwd:

    - Rij 1 (index 0)   : breedtes in kolommen B.. (B1, C1, D1, ...)
    - Kolom A vanaf rij 2 (index 1..): hoogtes (A2, A3, ...)
    - Prijzen starten op B2 (index [1:, 1:])

    Returned per sheet:
    {
      "Enkele plooi": {
          "widths": [...],   # staffels breedte
          "heights": [...],  # staffels hoogte
          "prices": {(hoogte, breedte): prijs}
      },
      ...
    }
    """
    matrices = {}
    xls = pd.ExcelFile(excel_file)

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet, header=None)

        # Breedtes: rij 0, kolommen vanaf 1
        widths_raw = [x for x in df.iloc[0, 1:].tolist() if not pd.isna(x)]
        widths = [float(x) for x in widths_raw]

        # Hoogtes: kolom 0, rijen vanaf 1
        heights_raw = [x for x in df.iloc[1:, 0].tolist() if not pd.isna(x)]
        heights = [float(x) for x in heights_raw]

        # Prijzen: vanaf rij 1, kolom 1
        price_df = df.iloc[1 : 1 + len(heights), 1 : 1 + len(widths)]
        price_df.columns = widths
        price_df.index = heights

        lookup = {}
        for h in heights:
            for w in widths:
                v = price_df.at[h, w]
                if pd.isna(v):
                    continue
                lookup[(h, w)] = float(v)

        matrices[sheet] = {
            "widths": sorted(widths),
            "heights": sorted(heights),
            "prices": lookup,
        }

    return matrices
