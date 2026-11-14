# amplitude_dos.py
# Lit data_angle_dos/, calcule l’amplitude (max-min) de chaque fichier CSV
# et écrit deux fichiers : amplitudes_jeunes.csv et amplitudes_patients.csv
# dans resultats_amplitudes/

import os
import pandas as pd

INPUT_FOLDER = "data_angle_genou"
OUTPUT_FOLDER = "resultats_amplitudes_genou"

COLUMN_NAME = "knee_angle_deg"


def compute_amplitude(df):
    """
    Calcule : amplitude = max(back_angle_deg) - min(back_angle_deg)
    Retourne un float.
    """
    if COLUMN_NAME not in df.columns:
        raise KeyError(f"Colonne manquante : {COLUMN_NAME}")

    return float(df[COLUMN_NAME].max() - df[COLUMN_NAME].min())


def process_all(input_folder=INPUT_FOLDER, output_folder=OUTPUT_FOLDER):
    print("\n--- CALCUL DES AMPLITUDES ---\n")

    if not os.path.exists(input_folder):
        print(f"❌ Dossier introuvable : {input_folder}")
        return

    os.makedirs(output_folder, exist_ok=True)

    amplitudes_jeunes = []
    amplitudes_patients = []

    # Parcours des sous-dossiers (1J_, 2J_, ..., A1_, A2_, ...)
    for participant in os.listdir(input_folder):
        p_in = os.path.join(input_folder, participant)
        if not os.path.isdir(p_in):
            continue

        print(f"Dossier participant : {participant}")

        # Détection jeune / patient
        est_jeune = participant.endswith("J_")
        est_patient = participant.startswith("A")

        # Parcours des fichiers CSV de ce participant
        for file in os.listdir(p_in):
            if not file.lower().endswith(".csv"):
                continue

            f_in = os.path.join(p_in, file)

            try:
                df = pd.read_csv(f_in, sep=',')
                amplitude = compute_amplitude(df)
            except Exception as e:
                print(f"⚠️ {file} ignoré : {e}")
                continue

            row = {
                "participant": participant,
                "fichier": file,
                "amplitude": amplitude
            }

            if est_jeune:
                amplitudes_jeunes.append(row)
            elif est_patient:
                amplitudes_patients.append(row)

            print(f"  ✔ {file} → amplitude = {amplitude:.3f}")

    # Export final
    pd.DataFrame(amplitudes_jeunes).to_csv(
        os.path.join(output_folder, "amplitudes_jeunes.csv"),
        index=False
    )

    pd.DataFrame(amplitudes_patients).to_csv(
        os.path.join(output_folder, "amplitudes_patients.csv"),
        index=False
    )

    print("\n--- FIN ✔ Résultats dans resultats_amplitudes/ ---\n")


if __name__ == "__main__":
    process_all()