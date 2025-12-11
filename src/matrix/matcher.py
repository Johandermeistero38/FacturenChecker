import re

def normalize_stofnaam(stof_raw: str) -> str:
    """
    Zet ruwe stofnaam uit factuur om naar een gestandaardiseerde naam.
    Werkt met substring matching.
    """

    stof_raw = stof_raw.lower().strip()

    mapping = {
        "cosa": "cosa",
        "corsa": "cosa",     # fout in PDF → fix
        "mixx": "mixx",
        "bo mixx": "bo mixx",
        "b0 mixx": "bo mixx",
        "dos lados": "dos lados",
        "isola": "isola",
        "mey": "mey",
        "marsa": "marsa",
        "matiz": "matiz",
        "hamilton": "hamilton",
        "saludo": "saludo",
        "texture": "texture",
        "vintage": "vintage",
        "voile": "voile",
        "cotton fr": "cotton fr",
        "inbetween voile": "voile",
        "inbetween": "voile",
        "between": "between",
        "color": "color",
    }

    for key, value in mapping.items():
        if key in stof_raw:
            return value

    return stof_raw  # fallback


def round_dimension(value_mm: int):
    """Zet mm om naar cm en rond af op staffels van 10."""
    cm = value_mm / 10
    afgerond = int(round(cm / 10) * 10)
    return afgerond


def evaluate_rows(rows, matrices):
    results = []

    for row in rows:
        stof = normalize_stofnaam(row["stof"])
        breedte = round_dimension(row["breedte"])
        hoogte = round_dimension(row["hoogte"])
        factuurprijs = row["prijs"]

        if stof not in matrices:
            results.append({
                "stof": stof,
                "afgerond": f"{breedte} x {hoogte}",
                "factuurprijs": factuurprijs,
                "status": "Geen matrix gevonden",
                "plooi": "N/A",
                "verschil": "N/A"
            })
            continue

        df = matrices[stof]

        prijzen_per_plooi = {}

        for plooi in df.index:
            try:
                prijs = df.loc[plooi, breedte]
            except:
                prijs = None

            prijzen_per_plooi[plooi] = prijs

        beste_plooi = None
        beste_prijsverschil = None

        for plooi, prijs in prijzen_per_plooi.items():
            if prijs is None:
                continue

            verschil = factuurprijs - prijs

            if (beste_prijsverschil is None) or abs(verschil) < abs(beste_prijsverschil):
                beste_plooi = plooi
                beste_prijsverschil = verschil

        if beste_plooi is None:
            results.append({
                "stof": stof,
                "afgerond": f"{breedte} x {hoogte}",
                "factuurprijs": factuurprijs,
                "plooi": "N/A",
                "verschil": "N/A",
            })
            continue

        results.append({
            "stof": stof,
            "afgerond": f"{breedte} x {hoogte}",
            "factuurprijs": factuurprijs,
            "plooi": beste_plooi,
            "verschil": round(beste_prijsverschil, 2),
        })

    return results
