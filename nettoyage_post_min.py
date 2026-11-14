# nettoyage_post_min.py
# Script qui prend les fichiers dans data_segmented/
# et crée data_t/ en retirant tout après le minimum de doigts_y

import os
import pandas as pd

INPUT_FOLDER = "data_segmented"
OUTPUT_FOLDER = "data_t"
FINGER_Y = "doigts_y"


def cut_after_min_y(df: pd.DataFrame) -> pd.DataFrame:
    """
    Retourne le DataFrame coupé juste après que doigts_y ait atteint son minimum.
    La phase où le doigt remonte est donc supprimée.
    """
    if FINGER_Y not in df.columns:
        print(f"Colonne {FINGER_Y} non trouvée, fichier laissé tel quel.")
        return df

    idx_min = df[FINGER_Y].idxmin()
    return df.loc[:idx_min].copy()


def process_all_data(input_folder=INPUT_FOLDER, output_folder=OUTPUT_FOLDER):
    print("\n--- DÉBUT DU TRAITEMENT post-minimum doigt_y ---\n")

    if not os.path.exists(input_folder):
        print(f"Le dossier {input_folder} est introuvable.")
        return

    os.makedirs(output_folder, exist_ok=True)

    for participant_folder in os.listdir(input_folder):
        full_participant_path = os.path.join(input_folder, participant_folder)

        if not os.path.isdir(full_participant_path):
            continue

        print(f"\nParticipant : {participant_folder}")

        output_participant_folder = os.path.join(output_folder, participant_folder)
        os.makedirs(output_participant_folder, exist_ok=True)

        for file in os.listdir(full_participant_path):
            if not file.lower().endswith(".csv"):
                continue

            input_path = os.path.join(full_participant_path, file)
            output_path = os.path.join(output_participant_folder, file)

            df = pd.read_csv(input_path)

            # Retirer index automatique éventuellement
            if df.columns[0].lower().startswith(("unnamed", "index")):
                df = df.iloc[:, 1:]

            # Couper au minimum doigt_y
            df_cut = cut_after_min_y(df)
            df_cut.to_csv(output_path, index=False)

            print(f"  → {file} : {len(df_cut)} frames conservées")

    print("\n--- FIN DU TRAITEMENT ✔ Fichiers dans data_t/ ---\n")


# Lancer automatiquement
if __name__ == "__main__":
    process_all_data()