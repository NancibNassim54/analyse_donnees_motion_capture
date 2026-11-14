import pandas as pd 
import missingno as msno 
import matplotlib.pyplot as plt

df = pd.read_csv("data_segmented/4J_/Jeune 4 15%N1.csv") 


msno.matrix(df) #On regarde la matrice pour voir si il y'a des trous dans les données
plt.show()