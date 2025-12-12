diff --git a/src/database/supplier_db.py b/src/database/supplier_db.py
index b93848db3f6ac1d72d19be4171e7840c718aa038..90c43ee310a6623eb1fabfc343b0f6adfb459fb2 100644
--- a/src/database/supplier_db.py
+++ b/src/database/supplier_db.py
@@ -1,57 +1,68 @@
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
 
 
+def load_supplier_config(supplier_key: str):
+    """
+    Haalt de configuratie op voor een specifieke leverancier.
+    """
+    suppliers = load_suppliers()
+    if supplier_key not in suppliers:
+        raise KeyError(f"Onbekende leverancier: {supplier_key}")
+
+    return suppliers[supplier_key]
+
+
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
-    
+
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
