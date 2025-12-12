diff --git a/src/matrix/matrix_loader.py b/src/matrix/matrix_loader.py
index 86005247faccb73267afd8d8783ddfce2fea5ce1..e4b88e78c5aa45f266491098df016e9f712c8d84 100644
--- a/src/matrix/matrix_loader.py
+++ b/src/matrix/matrix_loader.py
@@ -1,150 +1,64 @@
 import pandas as pd
 
-def load_price_matrices_from_excel(excel_file):
-    matrices = {}
-    xls = pd.ExcelFile(excel_file)
-
-    for sheet in xls.sheet_names:
-        df = pd.read_excel(xls, sheet_name=sheet, header=None)
-
-        # verwijder lege rijen / kolommen
-        df = df.dropna(axis=0, how="all")
-        df = df.dropna(axis=1, how="all")
-
-        # eerste rij = breedtes, maar kolom A is leeg → breedtes beginnen bij kolom B
-        widths = []
-        for val in df.iloc[0, 1:].tolist():
-            if isinstance(val, (int, float)):
-                widths.append(float(val))
-
-        # eerste kolom vanaf rij 2 = hoogtes
-        heights = []
-        for val in df.iloc[1:, 0].tolist():
-            if isinstance(val, (int, float)):
-                heights.append(float(val))
-
-        # prijsgebied = B2 t/m einde
-        price_df = df.iloc[1:1+len(heights), 1:1+len(widths)]
-        price_df.columns = widths
-        price_df.index = heights
-
-        lookup = {}
-        for h in heights:
-            for w in widths:
-                v = price_df.at[h, w]
-                if not pd.isna(v):
-                    lookup[(h, w)] = float(v)
-
-        matrices[sheet] = {
-            "widths": sorted(widths),
-            "heights": sorted(heights),
-            "prices": lookup
-        }
+from src.database.supplier_db import load_supplier_config
+
+
+PLOOI_TYPES = ["Enkele plooi", "Dubbele plooi", "Wave plooi", "Ring"]
+
+
+def _to_float(value):
+    try:
+        return float(str(value).replace(",", "."))
+    except Exception:
+        return None
 
-    return matrices
-import pandas as pd
 
-def load_price_matrices_from_excel(excel_file):
 def load_price_matrices_from_excel(path):
     """
-    Leest een Excel bestand met meerdere tabbladen (Enkele plooi, Dubbele plooi, Wave plooi, Ring)
-    en zet elke matrix om naar een gestandaardiseerd formaat:
-
-    {
-        "Enkele plooi": {
-            "widths": [...],
-            "heights": [...],
-            "grid": [[...], [...], ...]
-        },
-        "Dubbele plooi": {...},
-        ...
-    }
+    Laadt de prijsmatrices uit één Excelbestand.
+    Elke sheet vertegenwoordigt een plooitype.
     """
-
     xls = pd.ExcelFile(path)
     matrices = {}
-    xls = pd.ExcelFile(excel_file)
-
-    for sheet in xls.sheet_names:
-        df = pd.read_excel(xls, sheet_name=sheet, header=None)
-
-        # verwijder lege rijen / kolommen
-        df = df.dropna(axis=0, how="all")
-        df = df.dropna(axis=1, how="all")
-
-        # eerste rij = breedtes, maar kolom A is leeg → breedtes beginnen bij kolom B
-        widths = []
-        for val in df.iloc[0, 1:].tolist():
-            if isinstance(val, (int, float)):
-                widths.append(float(val))
-
-        # eerste kolom vanaf rij 2 = hoogtes
-        heights = []
-        for val in df.iloc[1:, 0].tolist():
-            if isinstance(val, (int, float)):
-                heights.append(float(val))
-
-        # prijsgebied = B2 t/m einde
-        price_df = df.iloc[1:1+len(heights), 1:1+len(widths)]
-        price_df.columns = widths
-        price_df.index = heights
-
-        lookup = {}
-        for h in heights:
-            for w in widths:
-                v = price_df.at[h, w]
-                if not pd.isna(v):
-                    lookup[(h, w)] = float(v)
-
-        matrices[sheet] = {
-            "widths": sorted(widths),
-            "heights": sorted(heights),
-            "prices": lookup
-    for sheet_name in xls.sheet_names:
 
-        df = pd.read_excel(path, sheet_name=sheet_name, header=None)
+    for sheet_name in xls.sheet_names:
+        df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
 
-        # -----------------------------
-        # Controle: is de sheet leeg?
-        # -----------------------------
         if df.empty:
             continue
 
-        # -----------------------------
-        # 1. Breedtes staan in rij 0, vanaf kolom 1
-        # -----------------------------
-        widths = df.iloc[0, 1:].tolist()
-
-        # -----------------------------
-        # 2. Hoogtes staan in kolom 0, vanaf rij 1
-        # -----------------------------
-        heights = df.iloc[1:, 0].tolist()
-
-        # -----------------------------
-        # 3. De daadwerkelijke prijs-matrix
-        # -----------------------------
-        grid = df.iloc[1:, 1:].values.tolist()
-
-        # -----------------------------
-        # Alles converteren naar floats
-        # -----------------------------
-        def to_float(v):
-            try:
-                return float(str(v).replace(",", "."))
-            except:
-                return None
-
-        widths = [to_float(v) for v in widths]
-        heights = [to_float(v) for v in heights]
-
-        clean_grid = []
-        for row in grid:
-            clean_grid.append([to_float(v) for v in row])
+        widths = [_to_float(v) for v in df.iloc[0, 1:].tolist()]
+        heights = [_to_float(v) for v in df.iloc[1:, 0].tolist()]
+        grid_raw = df.iloc[1:, 1:].values.tolist()
+        grid = [[_to_float(v) for v in row] for row in grid_raw]
 
         matrices[sheet_name] = {
             "widths": widths,
             "heights": heights,
-            "grid": clean_grid
+            "grid": grid,
         }
 
     return matrices
+
+
+def load_price_matrices(supplier_key: str):
+    """
+    Laadt alle prijsmatrices voor een leverancier en groepeert ze per stof.
+    Resultaatvorm:
+    {
+        "Cosa": {<plooi-matrices>},
+        "Isola": {<plooi-matrices>},
+        ...
+    }
+    """
+    supplier_config = load_supplier_config(supplier_key)
+    matrices = {}
+
+    for fabric_name, config in supplier_config["fabrics"].items():
+        matrix_path = config.get("matrix_path")
+        if not matrix_path:
+            continue
+
+        matrices[fabric_name] = load_price_matrices_from_excel(matrix_path)
+
+    return matrices
