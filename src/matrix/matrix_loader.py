import pandas as pd
import os

def load_supplier_matrices(supplier):
    base_path = "data/matrices/toppoint"

    matrices = {}

    for filename in os.listdir(base_path):
        if filename.endswith(".xlsx"):
            stofnaam = filename.replace(" price matrix.xlsx", "").strip().lower()

            df = pd.read_excel(os.path.join(base_path, filename), header=0)

            df = df.rename(columns={df.columns[0]: "hoogte"})
            df = df.set_index("hoogte")

            df.columns = df.columns.astype(int)
            df.index = df.index.astype(int)

            matrices[stofnaam] = df

    return matrices
