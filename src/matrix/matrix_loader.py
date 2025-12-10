import pandas as pd

def load_price_matrices_from_excel(excel_file):
    """
    Laadt de 4 matrix-tabbladen op basis van jouw Excel-indeling:
    - Rij 1 bevat de breedtes
    - Kolom A (kolom 0) bevat de hoogtes
    - Overige cellen zijn prijzen
    
    Returned dict:
    {
      "Enkele plooi": {
          "widths": [...],
          "heights": [...],
          "prices": {(height, width): price, ...}
      },
      ...
    }
    """
    matrices = {}
    xls = pd.ExcelFile(excel_file)

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet, header=None)

        # Breedtes staan in rij 1 vanaf kolom 1
        widths = df.iloc[1, 1:].tolist()

        # Hoogtes staan vanaf rij 2 in kolom 0
        heights = df.iloc[2:, 0].tolist()

        price_df = df.iloc[2:, 1:]
        price_df.columns = widths
        price_df.index = heights

        lookup = {}
        for h in heights:
            for w in widths:
                value = price_df.at[h, w]
                if pd.isna(value):
                    continue
                lookup[(float(h), float(w))] = float(value)

        matrices[sheet] = {
            "widths": [float(x) for x in widths],
            "heights": [float(x) for x in heights],
            "prices": lookup,
        }

    return matrices
