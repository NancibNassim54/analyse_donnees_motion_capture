import pandas as pd
import pygame
import sys, time

if len(sys.argv) != 2:
    print("please provide the path to the csv")

# normalisation
df = pd.read_csv(sys.argv[1])
xcols = []
ycols = []
zcols = []
for col in df:
    if "_x" in col: xcols.append(col)
    if "_y" in col: ycols.append(col)
    if "_z" in col: zcols.append(col)
maxx = df[xcols].max().max()
minx = df[xcols].min().min()
maxy = df[ycols].max().max()
miny = df[ycols].min().min()
maxz = df[zcols].max().max()
minz = df[zcols].min().min()

df[xcols] = (df[xcols]-minx)/(maxx-minx)
df[ycols] = (df[ycols]-miny)/(maxy-miny)
df[zcols] = (df[zcols]-minz)/(maxz-minz)

pygame.init()
width, height = 600, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Mouvement")

def getCoord(point, line):
    y = line[point+"_y"]
    z = line[point+"_z"]
    return ((1-z)*(width-20)+10, (1-y)*(height-20)+10)
    # return (z*(width-20)+10, x*(height-20)+10)

def display(line):
    screen.fill((0, 0, 0))
    pygame.draw.line(screen, (255, 0, 0), getCoord("poignet", line), getCoord("coude", line), 4)
    pygame.draw.line(screen, (255, 0, 0), getCoord("poignet", line), getCoord("doigts", line), 4)
    pygame.draw.line(screen, (255, 0, 0), getCoord("coude", line), getCoord("epaule", line), 4)
    pygame.draw.line(screen, (255, 0, 0), getCoord("dos", line), getCoord("epaule", line), 4)
    pygame.draw.line(screen, (255, 0, 0), getCoord("dos", line), getCoord("hanche", line), 4)
    pygame.draw.line(screen, (255, 0, 0), getCoord("genou", line), getCoord("hanche", line), 4)
    pygame.draw.line(screen, (255, 0, 0), getCoord("genou", line), getCoord("cheville", line), 4)
    pygame.draw.line(screen, (255, 0, 0), getCoord("pied", line), getCoord("cheville", line), 4)
    pygame.draw.line(screen, (255, 0, 0), getCoord("oeil", line), getCoord("oreille", line), 4)
    pygame.display.flip()

running = True
line = 0
speed = 5
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
    display(df.iloc[line])
    line+=1
    if line == len(df): line=0
    time.sleep(1/(speed*15))

pygame.quit()
sys.exit()

