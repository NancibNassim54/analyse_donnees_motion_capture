# angle_dos.py
# Lit data_t/, calcule l'angle du dos (hanche — dos — epaule)
# dans le plan YZ et écrit uniquement les angles dans data_angle_dos/

import os
import pandas as pd
import numpy as np

INPUT_FOLDER = "data_t"
OUTPUT_FOLDER = "data_angle_dos"

H_PREFIX = "hanche"
D_PREFIX = "dos"
E_PREFIX = "epaule"


def compute_back_angle(df):
    """
    Calcule l'angle du dos dans le plan YZ :
        hanche —— dos —— epaule
    avec dos comme sommet.
    Retourne un tableau d'angles en degrés.
    """

    hy, hz = f"{H_PREFIX}_y", f"{H_PREFIX}_z"
    dy, dz = f"{D_PREFIX}_y", f"{D_PREFIX}_z"
    ey, ez = f"{E_PREFIX}_y", f"{E_PREFIX}_z"

    required = [hy, hz, dy, dz, ey, ez]
    for col in required:
        if col not in df.columns:
            raise KeyError(f"Colonne manquante : {col}")

    # vecteurs dos→hanche et dos→epaule (plan YZ uniquement)
    u = np.stack([df[hy] - df[dy], df[hz] - df[dz]], axis=1)
    v = np.stack([df[ey] - df[dy], df[ez] - df[dz]], axis=1)

    # produit scalaire et normes
    dot = np.sum(u * v, axis=1)
    norm_u = np.linalg.norm(u, axis=1)
    norm_v = np.linalg.norm(v, axis=1)

    eps = 1e-8
    cos_angle = dot / (norm_u * norm_v + eps)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)

    angles_rad = np.arccos(cos_angle)
    return np.degrees(angles_rad)


def process_all(input_folder=INPUT_FOLDER, output_folder=OUTPUT_FOLDER):
    print("\n--- CALCUL ANGLE DU DOS ---\n")

    if not os.path.exists(input_folder):
        print(f"❌ Dossier introuvable : {input_folder}")
        return

    os.makedirs(output_folder, exist_ok=True)

    for participant in os.listdir(input_folder):
        p_in = os.path.join(input_folder, participant)
        if not os.path.isdir(p_in):
            continue

        print(f"Participant : {participant}")

        p_out = os.path.join(output_folder, participant)
        os.makedirs(p_out, exist_ok=True)

        for file in os.listdir(p_in):
            if not file.lower().endswith('.csv'):
                continue

            f_in = os.path.join(p_in, file)
            df = pd.read_csv(f_in)

            try:
                angles = compute_back_angle(df)
            except KeyError as e:
                print(f"⚠️ {file} ignoré : {e}")
                continue

            df_out = pd.DataFrame({"back_angle_deg": angles})
            f_out = os.path.join(p_out, file)
            df_out.to_csv(f_out, index=False)

            print(f"  ✔ {file} traité ({len(df_out)} angles)")

    print("\n--- FIN ✔ Résultats dans data_angle_dos/ ---\n")


if __name__ == "__main__":
    process_all()