import pandas as pd 
import missingno as msno 
import matplotlib.pyplot as plt

df = pd.read_csv("data_t/5J_/Jeune 5 15N8.csv") 
df2 = pd.read_csv("data_t/A2_/Patient 2 15%N10.csv")

plt.figure(figsize=(8, 6))

# Scatter du premier DataFrame
plt.scatter(df['dos_z'], df['dos_y'], label="Jeune", color = "teal", alpha=0.7)
# Scatter du deuxième DataFrame
plt.scatter(df2['dos_z'], df2['dos_y'], color = "red", label="Patient Agé", alpha=0.7)

plt.xlabel("dos_z")
plt.ylabel("dos_y")
plt.gca().invert_xaxis()
plt.title("Comparaison du mouvement du Dos (Jeune vs Patient Agé)")
plt.legend()
plt.grid(True)

plt.show()



