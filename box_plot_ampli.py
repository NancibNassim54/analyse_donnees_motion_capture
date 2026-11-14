import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# --- 1. CONFIGURATION DES FICHIERS ---
FILE_JEUNES = "resultats_amplitudes_genou/amplitudes_jeunes.csv"
FILE_PATIENTS = "resultats_amplitudes_genou/amplitudes_patients.csv"
COLUMN_DATA = "amplitude" # La colonne contenant les valeurs à tracer


# --- 2. LECTURE ET PRÉPARATION DES DONNÉES ---

# Lire le fichier des Jeunes et ajouter la colonne 'Groupe'
df_jeunes = pd.read_csv(FILE_JEUNES)
df_jeunes['Groupe'] = 'Jeunes'

# Lire le fichier des Patients et ajouter la colonne 'Groupe'
df_patients = pd.read_csv(FILE_PATIENTS)
df_patients['Groupe'] = 'Patients Agés'

# Concaténer les deux DataFrames en un seul pour l'affichage avec Seaborn
df_combined = pd.concat([df_jeunes, df_patients], ignore_index=True)


# --- 3. GÉNÉRATION DU BOXPLOT ---

# Configuration du style
sns.set_theme(style="whitegrid")

# Création de la figure et des axes Matplotlib
plt.figure(figsize=(8, 6))

# Génération du Boxplot avec Seaborn
# x : variable catégorielle (les groupes)
# y : variable numérique (l'amplitude)
boxplot = sns.boxplot(
    data=df_combined,
    x='Groupe',
    y=COLUMN_DATA,
    palette=["#246c66", "#7a1616"] # Couleurs personnalisées pour les groupes
)

# Ajouter des points de données individuels (swarmplot) pour voir la distribution
# Note: ceci est optionnel mais rend le graphique plus informatif
sns.swarmplot(
    data=df_combined,
    x='Groupe',
    y=COLUMN_DATA,
    color='k', # Couleur des points : noir
    size=3,    # Taille des points
    alpha=0.6, # Transparence des points
    ax=boxplot.axes # Assurer qu'il s'affiche sur le même axe
)

# --- 4. PERSONNALISATION DU GRAPHIQUE ---
plt.title(f"Comparaison de l'amplitude de l'angle du genou par groupe", fontsize=14)
plt.xlabel("Groupe de Participants", fontsize=12)
plt.ylabel("Amplitude de l'angle du genou (deg)", fontsize=12)

# Afficher la figure
plt.show()