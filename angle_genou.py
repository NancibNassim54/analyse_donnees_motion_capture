# angle_genou.py
# Lit data_t/, calcule l'angle au genou (cheville–genou–hanche)
# et écrit les angles uniquement dans data_angle_genou/

import os
import pandas as pd
import numpy as np

INPUT_FOLDER = "data_t"
OUTPUT_FOLDER = "data_angle_genou"

# Préfixes des colonnes
A_PREFIX = "cheville"
K_PREFIX = "genou"
H_PREFIX = "hanche"


def compute_knee_angle(df):
    """Calcule l'angle en degrés au niveau du genou (cheville-genou-hanche)."""

    ax, ay, az = f"{A_PREFIX}_x", f"{A_PREFIX}_y", f"{A_PREFIX}_z"
    kx, ky, kz = f"{K_PREFIX}_x", f"{K_PREFIX}_y", f"{K_PREFIX}_z"
    hx, hy, hz = f"{H_PREFIX}_x", f"{H_PREFIX}_y", f"{H_PREFIX}_z"

    required = [ax, ay, az, kx, ky, kz, hx, hy, hz]
    for col in required:
        if col not in df.columns:
            raise KeyError(f"Colonne manquante : {col}")

    # vecteurs genou→cheville et genou→hanche (plan YZ uniquement)
    u = np.stack([df[ay] - df[ky], df[az] - df[kz]], axis=1)
    v = np.stack([df[hy] - df[ky], df[hz] - df[kz]], axis=1)
    u = np.stack([df[ax] - df[kx], df[ay] - df[ky], df[az] - df[kz]], axis=1)
    v = np.stack([df[hx] - df[kx], df[hy] - df[ky], df[hz] - df[kz]], axis=1)

    dot = np.sum(u * v, axis=1)
    norm_u = np.linalg.norm(u, axis=1)
    norm_v = np.linalg.norm(v, axis=1)

    eps = 1e-8
    cos_angle = dot / (norm_u * norm_v + eps)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)

    angles_rad = np.arccos(cos_angle)
    return np.degrees(angles_rad)


def process_all(input_folder=INPUT_FOLDER, output_folder=OUTPUT_FOLDER):
    print("\n--- CALCUL ANGLE GENOU ---\n")

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
            if not file.lower().endswith(".csv"):
                continue

            f_in = os.path.join(p_in, file)
            df = pd.read_csv(f_in)

            try:
                angles = compute_knee_angle(df)
            except KeyError as e:
                print(f"⚠️ {file} ignoré : {e}")
                continue

            # Nouveau dataframe contenant uniquement les angles
            df_out = pd.DataFrame({"knee_angle_deg": angles})
            f_out = os.path.join(p_out, file)
            df_out.to_csv(f_out, index=False)

            print(f"  ✔ {file} traité ({len(df_out)} angles)")

    print("\n--- FIN ✔ Résultats dans data_angle_genou/ ---\n")


if __name__ == "__main__":
    process_all()
