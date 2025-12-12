diff --git a/src/matrix/matcher.py b/src/matrix/matcher.py
index 1f4a4e8e38072aeac7ce9599dcb97eb3c256285b..7de42576c0d9560d31209a416cda6b2d06f376f3 100644
--- a/src/matrix/matcher.py
+++ b/src/matrix/matcher.py
@@ -1,235 +1,134 @@
-import pandas as pd
-from src.database.supplier_db import load_suppliers, get_matrix_path_for_fabric
-from src.matrix.matrix_loader import load_price_matrices_from_excel
+from src.matrix.matrix_loader import PLOOI_TYPES
 from src.utils.rounding import round_up_to_matrix
 
-TARGET_FABRIC = "corsa"  # intern label; 'cosa' wordt hierna genormaliseerd
-PLOOI_ORDER = ["Enkele plooi", "Dubbele plooi", "Wave plooi", "Ring"]
-
-PLOOI_TYPES = ["Enkele plooi", "Dubbele plooi", "Wave plooi", "Ring"]
-
 
 def _format_euro(value):
     if value is None:
         return "N/A"
+
     s = f"{value:,.2f}"
     s = s.replace(",", "X").replace(".", ",").replace("X", ".")
     return f"€{s}"
-    return f"€{value:.2f}".replace(".", ",")
 
 
 def _format_diff(diff):
     if diff is None:
         return ""
+
     if abs(diff) < 0.005:
         sign = ""
         abs_val = 0.0
     else:
         sign = "+" if diff > 0 else "-"
         abs_val = abs(diff)
 
     s = f"{abs_val:,.2f}"
     s = s.replace(",", "X").replace(".", ",").replace("X", ".")
     return f"{sign}€{s}"
 
 
-def _collect_plooi_prices(matrices, height_cm, width_cm):
-    prices = {}
-    key = (float(height_cm), float(width_cm))
+def _lookup_price(matrix, width_cm, height_cm):
+    widths = matrix.get("widths", [])
+    heights = matrix.get("heights", [])
 
-    for plooi in PLOOI_ORDER:
-        info = matrices.get(plooi)
-        if info is None:
-            prices[plooi] = None
-        else:
-            prices[plooi] = info["prices"].get(key)
-    sign = "+" if diff > 0 else ""
-    return f"{sign}€{diff:.2f}".replace(".", ",")
+    if width_cm not in widths or height_cm not in heights:
+        return None
 
-    return prices
+    row_idx = heights.index(height_cm)
+    col_idx = widths.index(width_cm)
+    try:
+        return matrix.get("grid", [])[row_idx][col_idx]
+    except Exception:
+        return None
 
-def evaluate_rows(rows, supplier_key="toppoint"):
-    """
-    Voor ELKE regel:
-    - juiste stof bepalen
-    - juiste matrix voor die stof laden
-    - staffelmaten zoeken
-    - plooiprijzen ophalen
-    - match bepalen
-    """
 
 def evaluate_rows(rows, matrices):
-    results = []
-    suppliers = load_suppliers()
-    supplier = suppliers[supplier_key]
-
-    staffels_breedte = matrices["Enkele plooi"]["widths"]
-    staffels_hoogte = matrices["Enkele plooi"]["heights"]
+    """
+    Verwerkt alle regels uit de factuur met de aangeleverde prijsmatrices.
+    `matrices` is gegroepeerd per stofnaam.
+    """
     results = []
 
     for row in rows:
-        fabric_raw = row["fabric"]
-        fabric_norm = fabric_raw.lower()
-        fabric_code = row.get("fabric_code", "")
-
-        # 'Cosa' -> 'Corsa'
-        if "cosa" in fabric_norm:
-            fabric_norm = "corsa"
-
         fabric = row["fabric"]
+        fabric_code = row.get("fabric_code", "")
         width_mm = row["width_mm"]
         height_mm = row["height_mm"]
         invoice_price = row["invoice_price"]
+        raw_line = row.get("raw_line", "")
+
+        matrix_bundle = matrices.get(fabric)
 
         # mm -> cm
-        width_cm_orig = width_mm / 10.0
-        height_cm_orig = height_mm / 10.0
-
-        # afronden op staffels
-        width_cm = round_up_to_matrix(width_cm_orig, staffels_breedte)
-        height_cm = round_up_to_matrix(height_cm_orig, staffels_hoogte)
-
-        stof_display = f"{fabric_raw} ({fabric_code})" if fabric_code else fabric_raw
-        factuurprijs = row["invoice_price"]
-
-        # -------------------------
-        # 1. Probeer matrix te vinden voor deze stof
-        # -------------------------
-        try:
-            matrix_path = get_matrix_path_for_fabric(supplier, fabric)
-            matrices = load_price_matrices_from_excel(matrix_path)
-            matrix_ok = True
-        except Exception:
-            matrices = None
-            matrix_ok = False
-
-        # -------------------------
-        # 2. cm afronden op staffels (alleen als matrix bestaat)
-        # -------------------------
         width_cm = width_mm / 10
         height_cm = height_mm / 10
 
-        if matrix_ok:
-            bw = matrices["Enkele plooi"]["widths"]
-            bh = matrices["Enkele plooi"]["heights"]
-
-            w_round = round_up_to_matrix(width_cm, bw)
-            h_round = round_up_to_matrix(height_cm, bh)
-        else:
-            w_round = None
-            h_round = None
-
-        # -------------------------
-        # 3. Prepareer record
-        # -------------------------
         rec = {
-            "Regel": row["raw_line"],
-            "Stof": stof_display,
-            "Afgerond": f"{int(width_cm_orig)} x {int(height_cm_orig)}",
-            "Staffel breedte": int(width_cm),
-            "Staffel hoogte": int(height_cm),
-            "Factuurprijs": _format_euro(invoice_price),
-            "Stof": fabric,
+            "Regel": raw_line,
+            "Stof": f"{fabric} ({fabric_code})" if fabric_code else fabric,
             "Breedte/Hoogte (cm)": f"{int(width_cm)} x {int(height_cm)}",
-            "Staffel breedte": int(w_round) if w_round else "N/A",
-            "Staffel hoogte": int(h_round) if h_round else "N/A",
-            "Factuurprijs": _format_euro(factuurprijs),
+            "Factuurprijs": _format_euro(invoice_price),
         }
 
-        # Nog geen matrix beschikbaar voor andere stoffen dan Corsa/Cosa
-        if fabric_norm != TARGET_FABRIC:
-            for plooi in PLOOI_ORDER:
-        # -------------------------
-        # 4. Geen matrix beschikbaar?
-        # -------------------------
-        if not matrix_ok:
+        if not matrix_bundle:
+            rec["Staffel breedte"] = "N/A"
+            rec["Staffel hoogte"] = "N/A"
             for plooi in PLOOI_TYPES:
                 rec[plooi] = "N/A"
-            rec["Plooi match"] = ""
             rec["Plooi match"] = "Geen matrix"
             rec["Verschil"] = ""
             results.append(rec)
             continue
 
-        # Prijzen uit matrix ophalen
-        plooi_prices = _collect_plooi_prices(matrices, height_cm, width_cm)
-        # -------------------------
-        # 5. Plooiprijzen ophalen
-        # -------------------------
-        plooi_prices = {}
+        if "Enkele plooi" not in matrix_bundle:
+            rec["Staffel breedte"] = "N/A"
+            rec["Staffel hoogte"] = "N/A"
+            for plooi in PLOOI_TYPES:
+                rec[plooi] = "N/A"
+            rec["Plooi match"] = "Geen matrix"
+            rec["Verschil"] = ""
+            results.append(rec)
+            continue
 
-        for plooi in PLOOI_ORDER:
-            rec[plooi] = _format_euro(plooi_prices.get(plooi))
+        # afronden op staffels o.b.v. "Enkele plooi"
+        staffels_breedte = matrix_bundle["Enkele plooi"].get("widths", [])
+        staffels_hoogte = matrix_bundle["Enkele plooi"].get("heights", [])
+        w_round = round_up_to_matrix(width_cm, staffels_breedte)
+        h_round = round_up_to_matrix(height_cm, staffels_hoogte)
+
+        rec["Staffel breedte"] = int(w_round) if w_round is not None else "N/A"
+        rec["Staffel hoogte"] = int(h_round) if h_round is not None else "N/A"
+
+        plooi_prices = {}
         for plooi in PLOOI_TYPES:
-            mat = matrices.get(plooi)
-            if mat is None:
-                plooi_prices[plooi] = None
-                continue
+            mat = matrix_bundle.get(plooi)
+            price = _lookup_price(mat, w_round, h_round) if mat else None
+            plooi_prices[plooi] = price
+            rec[plooi] = _format_euro(price)
 
-        # --------------------------
-        # Nieuwe plooi-match logica
-        # --------------------------
-        direct_match_plooi = None
-        direct_match_diff = None
-        closest_plooi = None
-            if w_round in mat["widths"] and h_round in mat["heights"]:
-                row_idx = mat["heights"].index(h_round)
-                col_idx = mat["widths"].index(w_round)
-                plooi_prices[plooi] = mat["grid"][row_idx][col_idx]
-            else:
-                plooi_prices[plooi] = None
-
-            rec[plooi] = (
-                _format_euro(plooi_prices[plooi])
-                if plooi_prices[plooi] is not None
-                else "N/A"
-            )
-
-        # -------------------------
-        # 6. Beste plooi of "Niet zeker"
-        # -------------------------
         direct_match = None
-        closest_match_plooi = None
+        closest_match = None
         closest_diff = None
 
         for plooi, price in plooi_prices.items():
             if price is None:
                 continue
 
             diff = invoice_price - price
-            diff = factuurprijs - price
-
-            # dichtstbijzijnde plooi (voor "Niet zeker")
-            # directe match
             if abs(diff) < 0.01:
-                direct_match = (plooi, diff)
+                direct_match = diff
+                rec["Plooi match"] = plooi
+                rec["Verschil"] = _format_diff(diff)
                 break
 
-            # dichtstbijzijnde match
             if closest_diff is None or abs(diff) < abs(closest_diff):
                 closest_diff = diff
-                closest_plooi = plooi
-                closest_match_plooi = plooi
+                closest_match = plooi
 
-            # directe match (bv. exact gelijk tot op 1 cent)
-            if abs(diff) < 0.01:
-                if direct_match_diff is None or abs(diff) < abs(direct_match_diff):
-                    direct_match_diff = diff
-                    direct_match_plooi = plooi
-
-        if direct_match_plooi is not None:
-            rec["Plooi match"] = direct_match_plooi
-            rec["Verschil"] = _format_diff(direct_match_diff)
-        elif closest_plooi is not None:
-            rec["Plooi match"] = "Niet zeker"
+        if direct_match is None:
+            rec["Plooi match"] = closest_match or "N/A"
             rec["Verschil"] = _format_diff(closest_diff)
-        if direct_match:
-            rec["Plooi match"] = direct_match[0]
-            rec["Verschil"] = _format_diff(direct_match[1])
-        else:
-            rec["Plooi match"] = ""
-            rec["Verschil"] = ""
-            rec["Plooi match"] = "Niet zeker" if closest_match_plooi else "N/A"
-            rec["Verschil"] = _format_diff(closest_diff) if closest_diff else ""
 
         results.append(rec)
+
+    return results
