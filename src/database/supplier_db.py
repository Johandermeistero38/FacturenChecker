import json
import os


def load_suppliers():
    """
    Laadt de leveranciersconfiguratie uit data/suppliers.json
    """
    path = os.path.join("data", "suppliers.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_supplier_matrix_path(suppliers, supplier_key, fabric_key="corsa"):
    """
    Haalt het pad naar de matrix voor een bepaalde leverancier + stof.
    Voor nu standaard stof 'corsa' (waar 'cosa' ook onder valt).
    """
    supplier = suppliers.get(supplier_key)
    if not supplier:
        raise KeyError(f"Onbekende leverancier: {supplier_key}")

    fabrics = supplier.get("fabrics", {})
    fabric_info = fabrics.get(fabric_key)
    if not fabric_info:
        raise KeyError(f"Stof '{fabric_key}' niet gevonden voor leverancier '{supplier_key}'")

    return fabric_info["matrix_path"]
