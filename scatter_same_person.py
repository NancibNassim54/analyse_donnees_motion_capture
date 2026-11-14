import pandas as pd 
import missingno as msno 
import matplotlib.pyplot as plt

df = pd.read_csv("data_segmented/4J_/Jeune 4 15%N1.csv") 

plt.figure(figsize=(8, 6))

# Scatter du premier DataFrame
plt.scatter(df['dos_z'], df['dos_y'], label="Dos", color = "teal", alpha=0.7)
plt.scatter(df['epaule_z'], df['epaule_y'], label="Epaule", color = "red",  alpha=0.7)

plt.xlabel("axe_z")
plt.ylabel("axe_y")
plt.gca().invert_xaxis()
plt.title("Comparaison du mouvement de deux membres différents")
plt.legend()
plt.grid(True)

plt.show()



