import pandas as pd

def load_price_matrices_from_excel(path):
    """
    Laadt prijsmatrixen (4 plooi-type tabs) en maakt ALLE indexen + kolommen integers,
    zelfs als Excel strings, floats, spaties of 'Unnamed: 0' bevat.
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

        # Lees sheet + forceer eerste kolom als index
        df = excel.parse(sheet, header=0)

        # Eerste kolom is hoogte → hernoemen en set_index
        first_col = df.columns[0]
        df = df.rename(columns={first_col: "height"}).set_index("height")

        # --- ALTIJD integer index erzorgen ---
        df.index = (
            df.index.astype(str)          # alles naar string
                     .str.replace(r"[^\d]+", "", regex=True)  # strip niet-cijfers
                     .astype(int)         # terug naar int
        )

        # --- ALTIJD integer kolommen erzorgen ---
        df.columns = (
            df.columns.astype(str)
                      .str.replace(r"[^\d]+", "", regex=True)
                      .astype(int)
        )

        # Waarden numeric
        df = df.apply(pd.to_numeric, errors="coerce")

        matrices[sheet] = df

    # Verzamel breedtes en hoogtes uit eerste matrix
    main_df = matrices["Enkele plooi"]
    width_steps = list(main_df.columns)
    height_steps = list(main_df.index)

    return matrices, width_steps, height_steps
