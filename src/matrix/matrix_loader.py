import pandas as pd

def load_price_matrices_from_excel(path):
    """
    Laadt één Excel-bestand met 4 tabbladen (Enkele, Dubbele, Wave, Ring)
    en zorgt dat rijen en kolommen altijd integers zijn.
    """

    sheets = ["Enkele plooi", "Dubbele plooi", "Wave plooi", "Ring"]
    matrices = {}

    try:
        excel = pd.ExcelFile(path)
    except Exception as e:
        raise ValueError(f"Kan Excel niet openen: {e}")

    for sheet in sheets:
        if sheet not in excel.sheet_names:
            matrices[sheet] = None
            continue

        df = excel.parse(sheet, header=0)

        # Eerste kolom moet de hoogte index worden
        df = df.rename(columns={df.columns[0]: "height"})
        df = df.set_index("height")

        # Convert ALL row + column labels to integers
        try:
            df.index = df.index.astype(int)
        except:
            df.index = df.index.astype(str).str.extract(r"(\d+)").astype(int)

        try:
            df.columns = df.columns.astype(int)
        except:
            df.columns = df.columns.astype(str).str.extract(r"(\d+)").astype(int)

        # Convert values to floats
        df = df.apply(pd.to_numeric, errors="coerce")

        matrices[sheet] = df

    # Verzamel alle unieke breedtes en hoogtes
    all_widths = matrices["Enkele plooi"].columns.tolist()
    all_heights = matrices["Enkele plooi"].index.tolist()

    return matrices, all_widths, all_heights
