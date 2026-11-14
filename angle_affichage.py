import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt

df = pd.read_csv("resultats_amplitudes_dos/amplitudes_jeunes.csv")
df2 = pd.read_csv("resultats_amplitudes_dos/amplitudes_patients.csv")


plt.plot(df['amplitude'], label= "Amplitudes Dos Jeune", color= "teal", alpha=0.7)
plt.plot(df2['amplitude'], label= "Amplitudes Dos Agées", color= "red", alpha=0.7)

plt.xlabel("Index")
plt.ylabel("Amplitude")
plt.title("Comparaison des amplitudes d'ouverture du Dos chez les jeunes vs agées")
plt.legend()
plt.grid(True)

plt.show()