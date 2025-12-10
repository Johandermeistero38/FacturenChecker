import pandas as pd

def load_price_matrices_from_excel(excel_file):
    matrices = {}
    xls = pd.ExcelFile(excel_file)

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet)

        heights = df.iloc[2:, 1].astype(float).tolist()
        widths = df.iloc[1, 2:].astype(float).tolist()

        price_df = df.iloc[2:, 2:]
        price_df.columns = widths
        price_df.index = heights

        lookup = {}
        for h in heights:
            for w in widths:
                price = price_df.at[h, w]
                if not pd.isna(price):
                    lookup[(h, w)] = float(price)

        matrices[sheet] = lookup

    return matrices
