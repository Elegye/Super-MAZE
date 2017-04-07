#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""
Version 2.2 du projet d'ISN.

Le but est d'arriver à se déplacer dans un environnement 2D, en détectant les
éventuels obstacles et en empêchant de les traverser.
La version ne gère qu'un seul joueur.
On se sert principalement des bibliothèques Turtle et Tkinter

TODO / V2.2 :
- Interface d'accueil
- Configuration des touches du joueur.
- Keybinding performants en vue de jouer à deux dans le Labyrinthe
- Mettre en place un but à atteindre, pour tester les différentes possibilités conceptuelles.

DONE / V2.1 :
- Réorganisation du code, différentes versions et solutions aux problèmes
rencontrés.
- Définition d'un point de départ du joueur, en concordance avec un point de départ pour le labyritnhe (plus tard)

- Système de hitbox pixel perfect avec liste composée de tuples des coordonnées des points de la bordure
 => La hitbox est presque pixel perfect, et est gérée avec une liste des points interdits de passage.
- Code en anglais
- La fenêtre de jeu se situe maintenant dans une fenêtre Tkinter, ce qui nous permettra d'étoffer un peu l'interface.
"""

import tkinter as tk
import turtle
from PIL import Image, ImageTk

"""

move_number | type : int | description : Le nombre de déplacement qu'a fait le joueur?
(x, y) | type : tuple | description: tuple contenant les valeurs successives des coordonnées prises par le joueur
coord_player | type : list | description : liste contenant toutes les coordonnées (x,y) du joueur. La clé est le nombre de déplacement -1.
coord_border | type: list | description : chaque coordonnée de chaque point constituant la bordure.

"""

move_number = 0
coord_player = [[], [], []]
coord_border = []
(x, y) = (0,0)
error = 0
axis_origin = ()
playing = False
players = [0, 1]
do = 0


# COnfigurations de base ...
SPEED = 0 #i.e. Le plus rapide
BORDER_SIZE = 600
BORDER_COLOR = "blue"
BORDER_START_X = -300
BORDER_START_Y = -300
BORDER_WEIGHT = 1


class Graphique(tk.Frame):
    """
    Classe qui s'occupe de tout l'affichage en dehors du jeu.
    """
    def __init__(self, instance=None):
        super().__init__(instance)
        self.pack()
        self.init_widget()

    def init_widget(self):
        self.config_keys = tk.Button(self, text = "Configurer les touches", command = self.configure_keys)
        self.config_keys.pack(side="top")
    def configure_keys(self):
        self.test = tk.Button(self, text = "Coucou!", command=quit)
        self.test.pack(side="top")



def redo_move(move_number, coord_player, player):
    """
    Permet de retracer le parcours du joueur.
    On postionne tout d'abbord le joueur à son endroit initial
    :param move_number: le nombre de déplacement(s) du joueur.
    :param coord_player: toutes les coordonnées du joueur.
    :type move_number: int
    :type coord_player: list

    TODO : gérer la direction des turtles à l'avenir ...
    """
    global players
    move(0,0,player,False)

    # On parcours les coordonnées afin d'en extraire les coordonnées des points.
    for x, y in coord_player[players.index(player)]:
        #Déplace successivement le joueur de l'origine jusqu'à sa dernière position.
        move(x,y,player,False)

def set_coord(x,y, player):
    """
    Permet de stocker les coordonnées du joueur dans une liste.

    :param x: On récupère la coordonnée x du point à enregistrer
    :param y: On récupère la coordonnée y du point à enregistrer
    :type x: float
    :type y: float:
    :return: Liste des coordonnées du joueur avec en indice le numéro
    du déplacement.
    """
    #On récupère move_number
    global move_number, players
    #Déboguage : qui bouge ?
    #debug(players.index(player))
    # Dans le cas du premier déplacement, il faut insérer les coordonnées
    #de l'origine
    if move_number == 0:
        coord_player[players.index(player)].append((0,0))
    #Ajouter et return les coordonnées du joueur.
    coord_player[players.index(player)].append(player.position())
    return coord_player

def get_coord(id):
    return player_coord

def move(x, y, player, stocker = True):
    """
    Se déplacer grâce à la méthode turtle.goto de Turtle.
    On lève le crayon au début pour ne pas tracer de traits moches partout,
    puis une fois arrivé au point, on le rabaisse.

    :param x: Coordonnée x à atteindre
    :param y: Coordonné y à atteindre
    :param player: Objet du joueur
    :param stocker: Déplacement à enregistrer ou non.
    :type x: int
    :type y: int
    :type player: object
    :type stocker: boolean
    """
    global move_number, error, coord_player

    player.up()

    #On stocke ou pas?
    if stocker == True:
        set_coord(x,y, player)
        move_number  += 1
    player.goto(x, y)


    # Check des bordures
    # Si true, alors on n'y va pas
    if collision_checking(x, y):
        player.undo()

    player.down()

def collision_checking(x, y):
    """
    Checking des collisions éventuelles au pixel près.
    :param x: coordonnée x à vérifier
    :param y: coordonnée y à vérifier
    :return: True si collision et False si pas de collisions.
    """
    global coord_border
    # Si les coordonnées (x,y) sont dans la liste des coordonnées de la bordure
    if (x,y) in coord_border:
        return True
    else:
        return False
def goal_checking(x, y):
    return False

def move_x(player, coord = 0):
    """
    On se déplace sur l'axe des abscisses.
    On oriente le turlte dans la direction du joueur.
    :param coord: dépalcement (en pixel) à faire
    :type coord: int
    """

    # Définit la direction du joueur
    if player.tiltangle()!=360 and coord > 0:
        player.setheading(360)
    if player.tiltangle()!=180 and coord < 0:
        player.setheading(180)

    move(player.xcor()+coord, player.ycor(), player)

def move_y(player, coord = 0):
    """
    On se déplace sur l'axe des ordonnées.
    On oriente le turtle dans la direction du joueur.
    :param coord: dépalcement (en pixel) à faire
    :type coord: int
    """

    # Définit la direction du joueur
    if player.tiltangle()!=90 and coord > 0:
        player.setheading(90)
    if player.tiltangle()!= 270 and coord < 0:
        player.setheading(270)

    move(player.xcor(), player.ycor()+coord, player)


def set_ext_border():
    global coord_border

    border = turtle.Turtle()
    border.color(BORDER_COLOR)
    border.speed(0)
    border.penup()
    border.setposition(BORDER_START_X,BORDER_START_Y)
    border.pensize(BORDER_WEIGHT)
    border.pendown()
    # Algorithme retenu :
    # On constitue un carré, donc 4 côtés identiques
    for i in range(4):
        #BORDER_LONGTH/10 = rng
        rng = range(60)
        #On avance de 10 car toutes les coordonnées sont multiples de 10 là chakal
        for i in rng:
            border.forward(10)
            x = int(border.xcor())
            y = int(border.ycor())
            coord_border.append((x,y))
        border.left(90)
    border.hideturtle()

def test(t):
    print(t)

keys_up = ["Up", "Z"]
#keys_up = [lambda event: test(event), "Up", "Z"]
keys_down = ["Down", "S"]
keys_left = ["Left", "Q"]
keys_right = ["Right", "D"]
keys_redo = ["A", "X"]

def binding(event):

    """
    On récupère les entrées claviers et on dispatche. C'est plus propre et plus joli...
    """
    keys = [keys_up, keys_down, keys_left, keys_right, keys_redo]
    str.capitalize(event.keysym)

    if str.capitalize(event.keysym) in keys_up:
        move_y(players[keys_up.index(str.capitalize(event.keysym))], 10)
    elif str.capitalize(event.keysym) in keys_down:
        move_y(players[keys_down.index(str.capitalize(event.keysym))], -10)
    elif str.capitalize(event.keysym) in keys_left:
        move_x(players[keys_left.index(str.capitalize(event.keysym))], -10)
    elif str.capitalize(event.keysym) in keys_right:
        move_x(players[keys_right.index(str.capitalize(event.keysym))], 10)
    elif str.capitalize(event.keysym) in keys_redo:
        redo_move(move_number, coord_player, players[keys_redo.index(str.capitalize(event.keysym))])
    else:
            False

    #On parcourt le tableau des keys.
    # for i in range(len(keys)):
    #     for n in range(1, len(players)+2):
    #         #print(keys[i][n])
    #         #print(event.keysym)
    #         if event.keysym in keys[i][n]:
    #             #print(keys[i])
    #             #print(keys[i][0](event.keysym))
    #             lambda : keys[i][0](event.keysym)
    #         else:
    #             return False


def init():
    root = tk.Tk()

    image = Image.open("super_maze.jpg")
    photo = ImageTk.PhotoImage(image)

    canvas = tk.Canvas(root, width = image.size[0], height = image.size[1])
    canvas.create_image(0,0, anchor = tk.NW, image=photo)
    canvas.pack()
    canvas.bind("F", play())

#init()
playing = True
while playing == True :

    main_window = turtle.getcanvas().master
    main_window.title("Coucou")

    #app = Graphique(main_window)

    #On met le bon nombre de joueur(s) sur l'écran:
    for i in range(len(players)):
        players[i] = turtle.Turtle()
        players[i].home()
        players[i].speed()

    # On met en place la bordure extérieure si elle n'existe pas déjà
    if not coord_border : set_ext_border()

    main_window.bind("<Key>", binding)

    main_window.mainloop()
