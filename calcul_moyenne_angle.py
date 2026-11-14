import pandas as pd
import os

def traiter_dossier(chemin_dossier, dossier_sortie):
    """
    Traite chaque fichier CSV d’un dossier séparément
    et génère un fichier de résultats pour chaque fichier.
    """

    # Crée le dossier de sortie s'il n'existe pas
    os.makedirs(dossier_sortie, exist_ok=True)

    # Parcourt tous les fichiers du dossier d'entrée
    for nom_fichier in os.listdir(chemin_dossier):
        if nom_fichier.lower().endswith(".csv"):
            chemin_complet = os.path.join(chemin_dossier, nom_fichier)

            # Lecture robuste
            df = pd.read_csv(
                chemin_complet,
                sep=None,
                engine="python",
                header=None,
                names=["patient", "essai", "valeur"]
            )

            df["valeur"] = pd.to_numeric(df["valeur"], errors="coerce")

            # --------------------------
            # 1) Stats par patient
            # --------------------------
            stats_par_patient = df.groupby("patient")["valeur"].agg(
                ["count", "mean", "std", "min", "max"]
            )

            # --------------------------
            # 2) Stats globales DU FICHIER
            # --------------------------
            stats_globales = df["valeur"].agg(
                ["count", "mean", "std", "min", "max"]
            ).to_frame().T  # transforme en ligne

            stats_globales.index = ["global"]

            # --------------------------
            # 3) Fusion des deux
            # --------------------------
            resultat_final = pd.concat([stats_par_patient, stats_globales])

            # --------------------------
            # 4) Export du fichier individuel
            # --------------------------
            nom_sortie = os.path.splitext(nom_fichier)[0] + "_resultats.csv"
            chemin_sortie = os.path.join(dossier_sortie, nom_sortie)

            resultat_final.to_csv(chemin_sortie, index=True)

            print(f"✔ Fichier généré pour {nom_fichier} → {chemin_sortie}")


# ====================================================
# 💾 TRAITEMENT DES 2 DOSSIERS
# ====================================================

traiter_dossier("resultats_amplitudes_dos", r"amplitude_moyenne\amplitude_moyenne_dos")
traiter_dossier("resultats_amplitudes_genou", r"amplitude_moyenne\amplitude_moyenne_genou")
