import os
import pandas as pd
import numpy as np
from scipy.spatial.distance import euclidean


def resample_file(path):
    """Rééchantillonne un CSV 200 Hz → 60 Hz."""
    
    df = pd.read_csv(path)

    # Retirer la première colonne si c’est un index automatique
    if df.columns[0].lower().startswith(("unnamed", "index")):
        df = df.iloc[:, 1:]

    # Ajouter un temps basé sur 200 Hz
    df["time"] = df.index / 200.0
    df = df.set_index("time")

    duration = df.index[-1]

    # Grille à 60 Hz
    new_times = np.arange(0, duration, 1/60)

    # Interpolation
    df_resampled = df.reindex(new_times).interpolate(method="linear")

    df_resampled.reset_index(drop=True, inplace=True)

    return df_resampled


def process_all_data(input_folder="data", output_folder="data_resampled"):
    """Traite toute l'arborescence du dossier data/."""
    
    print("\n--- DÉBUT DU TRAITEMENT ---\n")

    for participant_folder in os.listdir(input_folder):
        full_participant_path = os.path.join(input_folder, participant_folder)

        # Vérifier que c'est un dossier (1J_, 2J_, A1_, etc.)
        if not os.path.isdir(full_participant_path):
            continue

        print(f"\nParticipant : {participant_folder}")

        # Dossier de sortie correspondant
        output_participant_folder = os.path.join(output_folder, participant_folder)
        os.makedirs(output_participant_folder, exist_ok=True)

        # Parcourir les fichiers CSV
        for file in os.listdir(full_participant_path):
            if file.lower().endswith(".csv"):
                input_path = os.path.join(full_participant_path, file)
                output_path = os.path.join(output_participant_folder, file)

                print(f"  → Rééchantillonnage : {file}")

                df_resampled = resample_file(input_path)
                df_resampled.to_csv(output_path, index=False)

        print(f"✔ Terminé pour {participant_folder}")

    print("\n--- TOUS LES FICHIERS ONT ÉTÉ TRAITÉS ✔ ---\n")



# Lancer le traitement
process_all_data("data")



# Points d'intérêt (Doigts) pour le calcul de la vitesse
FINGER_COLUMNS = ['doigts_x', 'doigts_y', 'doigts_z']
SAMPLING_RATE = 60 # Hz (car vous avez rééchantillonné à 60 Hz)
VELOCITY_THRESHOLD_PERCENT = 0.05 # 5% de la vitesse maximale

def segment_movement(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule la vitesse 3D du bout des doigts et segmente le mouvement.
    
    L'enregistrement est conservé uniquement lorsque la vitesse est > 5% de la vitesse maximale.
    """
    
    if not all(col in df.columns for col in FINGER_COLUMNS):
        print("  Erreur : Colonnes des doigts (x, y, z) non trouvées. Retourne le DataFrame original.")
        return df

    # --- 1. Calcul de la Vitesse 3D du bout des doigts ---
    
    # Calcul du déplacement 3D entre chaque frame (distance entre P(t) et P(t-1))
    # Il est important d'utiliser la distance euclidienne (3D)
    
    # Calculer la différence entre les positions consécutives
    diff_pos = df[FINGER_COLUMNS].diff().fillna(0)
    
    # Calculer le déplacement (magnitude de la différence de position)
    displacement_3d = np.sqrt(
        diff_pos['doigts_x']**2 + diff_pos['doigts_y']**2 + diff_pos['doigts_z']**2
    )
    
    # Vitesse = Déplacement / Intervalle de temps (1/60 seconde)
    # L'unité dépend des unités dans le CSV (souvent en mm/frame si les unités sont en mm)
    # Vitesse (mm/s ou unité/s) = Déplacement * Fréquence d'échantillonnage
    df['vitesse_doigts'] = displacement_3d * SAMPLING_RATE

    # --- 2. Détermination du Seuil et Segmentation ---
    
    # La première ligne a souvent une vitesse de 0 après diff().fillna(0), on l'ignore.
    max_velocity = df['vitesse_doigts'].iloc[1:].max() 

    if max_velocity == 0:
        print("  Avertissement : Vitesse maximale nulle ou très faible. Aucune segmentation effectuée.")
        return df # Retourne tout le DF si le mouvement n'a pas été détecté.

    # Définir le seuil de vitesse
    threshold = max_velocity * VELOCITY_THRESHOLD_PERCENT
    
    # Isoler les frames où la vitesse est supérieure au seuil
    df_segmented = df[df['vitesse_doigts'] >= threshold].copy()
    
    # Optionnel : Retirer la colonne de vitesse ajoutée pour le calcul
    df_segmented.drop(columns=['vitesse_doigts'], inplace=True)

    return df_segmented


def process_all_data_segmented(input_folder="data_resampled", output_folder="data_segmented"):
    """
    Applique la segmentation basée sur la vitesse à tous les fichiers
    dans le dossier d'entrée et les sauvegarde dans un nouveau dossier.
    """
    
    print("\n--- DÉBUT DE LA SEGMENTATION DU MOUVEMENT ---\n")
    print(f"Seuil de segmentation : {VELOCITY_THRESHOLD_PERCENT * 100}% de la Vitesse Maximale.")

    if not os.path.exists(input_folder):
        print(f"\n Erreur: Le dossier d'entrée '{input_folder}' n'existe pas. Veuillez lancer le rééchantillonnage d'abord.")
        return

    # Parcourir tous les participants
    for participant_folder in os.listdir(input_folder):
        full_participant_path = os.path.join(input_folder, participant_folder)

        if not os.path.isdir(full_participant_path):
            continue

        print(f"\nParticipant : {participant_folder}")

        # Dossier de sortie correspondant
        output_participant_folder = os.path.join(output_folder, participant_folder)
        os.makedirs(output_participant_folder, exist_ok=True)

        # Parcourir les fichiers CSV
        for file in os.listdir(full_participant_path):
            if file.lower().endswith(".csv"):
                input_path = os.path.join(full_participant_path, file)
                output_path = os.path.join(output_participant_folder, file)

                # Charger et segmenter le fichier
                df = pd.read_csv(input_path)
                
                # S'assurer que les index non nommés sont retirés si le fichier en contient
                if df.columns[0].lower().startswith(("unnamed", "index")):
                    df = df.iloc[:, 1:]

                df_segmented = segment_movement(df)

                # Sauvegarder le fichier segmenté
                df_segmented.to_csv(output_path, index=False)
                
                print(f"  → Fichier segmenté: {file} ({len(df_segmented)} frames)")

        print(f"✔ Terminé pour {participant_folder}")

    print("\n--- SEGMENTATION TERMINÉE. NOUVEAUX FICHIERS DANS 'data_segmented' ✔ ---\n")

# Lancer le traitement (en supposant que 'data_resampled' est le dossier créé précédemment)
process_all_data_segmented("data_resampled", "data_segmented")