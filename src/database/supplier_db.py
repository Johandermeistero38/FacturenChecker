import json
import os


# ----------------------------------------
# 1. Load suppliers.json
# ----------------------------------------
def load_suppliers():
    """
    Leest de JSON in met alle leveranciers, stoffen en matrixpaden.
    """
    path = "data/suppliers.json"
    if not os.path.exists(path):
        raise FileNotFoundError(f"suppliers.json niet gevonden op: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ----------------------------------------
# 2. Haal alle stofnamen van een leverancier op
# ----------------------------------------
def get_fabric_list(supplier_data):
    """
    Returnt een lijst met officiële stofnamen voor een leverancier.
    """
    return list(supplier_data["fabrics"].keys())


# ----------------------------------------
# 3. Geef matrix-pad voor specifieke stof
# ----------------------------------------
def get_matrix_path_for_fabric(supplier_data, fabric_name):
    """
    Zoekt de juiste matrix-file voor een stof.
    Als deze niet bestaat → foutmelding.
    """
    fabrics = supplier_data["fabrics"]

    if fabric_name in fabrics:
        return fabrics[fabric_name]["matrix_path"]
    
    raise ValueError(
        f"Geen matrix gevonden voor stof '{fabric_name}'. "
        f"Beschikbare stoffen: {', '.join(fabrics.keys())}"
    )


# ----------------------------------------
# 4. Controle of matrixpacket bestaat
# ----------------------------------------
def verify_matrix_file(matrix_path):
    """
    Controleert of het matrixbestand werkelijk bestaat.
    Returnt True/False.
    """
    return os.path.exists(matrix_path)
