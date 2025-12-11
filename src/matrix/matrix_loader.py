import os
import pandas as pd

DATA_DIR = "data/matrices"

def load_supplier_matrices(supplier: str):
    """
    Laadt ALLE prijsmatrixen binnen data/matrices/<supplier>/ automatisch.
    Geeft dict terug: {stofnaam: dataframe}
    """

    supplier_path = os.path.join(DATA_DIR, supplier)
    if not os.path.isdir(supplier_path):
        raise FileNotFoundError(
            f"Map voor leverancier '{supplier}' bestaat niet: {supplier_path}"
        )

    matrices = {}

    for file in os.listdir(supplier_path):
        if not file.lower().endswith(".xlsx"):
            continue

        stofnaam = file.replace(" price matrix.xlsx", "").strip().lower()

        full_path = os.path.join(supplier_path, file)
        df = pd.read_excel(full_path, index_col=0)

        df.index = df.index.astype(int)
        df.columns = df.columns.astype(int)

        matrices[stofnaam] = df

    return matrices
