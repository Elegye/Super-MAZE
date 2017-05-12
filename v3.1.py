import tkinter
import turtle
import time
from random import choice, randint
from PIL import Image, ImageTk
#import pyglet

"""
Version 3.1 du projet Super Maze

Première intégration de la génération et des déplacements et de l'interface d'accueil!
Ajout du son!

Seul problème rencontré :
Il faut définir les murs par le milieu du mur et non son extrêmité haute. Car le joueur se déplace sur des milieux de murs.
"""

"""
logs :
- forward|turn_left|turn_right
- 0|1|2|3
"""
players = [0, 1]

class Laby :

        UNIT = 20
        RAY = 200
        # WARNING : (2*RAY)/UNIT MUST BE integer
        FREQ = 60
        REACH = 20#la 'portée' d'un curseur

        def __init__(self,canvas,screen, buildfile=None):
                """Attributs :
                - self.canvas (passé comme paramètre)
                - self.screen : couche de liaison entre turtle et tkinter
                - self.walls : contient l'enseble des murs"""
                self.canvas = canvas
                self.screen = screen

                self.screen.tracer(n=Laby.FREQ)

                left = turtle.RawTurtle(self.screen)#le mur gauche
                right = turtle.RawTurtle(self.screen)#le mur droit

                left.speed(0)#i.e. max
                right.speed(0)

                left.up()
                left.goto((0,Laby.UNIT))
                left.down()
                left.ht()
                right.ht()

                self.walls = set()
                # cet attribut contient les coordonnées des murs tracés

                self.out = None#les coordonnées de la sortie
                #WARNING : la sortie (Laby.RAY,Laby.RAY) n'est pas valable, car elle code pour deux côtés (elle est en haut ET à droite)

                self.pos_tracker = set()#l'ensemble des case déjà parcourues
                self.pos_turtle = dict()#les positions actuelles de tous les couples de turtles

                self.turtles = [(left,right),]
                self.remove = set()
                self.adding = list()
                #il ne faut pas modifier self.turtles pendant qu'on itère dessus ;
                #d'où self.remove et self.adding

                if buildfile is not None :#on a un log à suivre
                        buildfile = iter(buildfile)
                        while len(self.turtles) :
                                for i,(left,right) in enumerate(self.turtles):
                                        if not self.can_goon(left,right,i) :
                                                continue
                                        else :
                                                log_line = next(buildfile)[:-1]
                                                func = getattr(self,log_line[:-1])
                                                fork = int(log_line[-1])
                                                self.pos_tracker.add(self.ahead(left,right)[0])
                                                func(left,right,fork=fork)
                                                self.can_goon(left,right,i)
                                self.turtles = [x for i,x in enumerate(self.turtles) if i not in self.remove]+self.adding
                                self.remove = set()
                                self.adding = list()
                                for l,r in self.turtles :
                                        self.pos_turtle[(l,r)] = self.ahead(l,r)[0]

                while len(self.turtles) :
                        for i,(left,right) in enumerate(self.turtles):
                                if not self.can_goon(left,right,i) :
                                        continue
                                #si on ne peut plus avancer : on se suicide (dans can_goon) et on repart sur le couple suivant

                                self.pos_tracker.add(self.ahead(left,right)[0])
                                #la case devant soi va être remplie par ce tour de boucle

                                #le déplacement doit-il être aléatoire ou forcé ?
                                reachable = True
                                for func in self.moves :
                                        self.gone = set()
                                        if not self.parse_area(*self.ahead(*self.ahead(left,right,func)[1])[0]):
                                                #si la case devant / à gauche / à droite ne peut être remplie que ppar ce couple
                                                reachable = False
                                                break

                                if reachable :#on n'est "responsable" d'aucune case : déplacement aléatoire sans embranchement
                                        func = choice(self.moves)
                                        fork = 0
                                else :#on est "responsable" d'au moins une case : déplacement forcé
                                        case = 0
                                        #cette variable représente l'environnement du couple : les cases devant, à gauche, à droite sont-elles libres ou pas ?
                                        #case varie entre 0 et 8 => 3 bits binaires pour 3 cases à tester
                                        for j,func in enumerate(self.moves) :
                                                pos = self.ahead(*self.ahead(left,right,func)[1])[0]
                                                #pos = les coordonnées de la case à tester
                                                if pos not in self.pos_tracker \
                                                        and abs(pos[0])<=Laby.RAY \
                                                        and abs(pos[1])<= Laby.RAY :
                                                        case += 2**j
                                                elif (abs(pos[0])>Laby.RAY or abs(pos[1])>Laby.RAY) and self.out is None :
                                                    case += 2**j#pour garantir une sortie
                                        if len(self.turtles)+len(self.adding)-len(self.remove) == 1 :
                                                # A DEPLACER AVANT LA BOUCLE FOR
                                                #si on n'a qu'un couple de turtles (ne sert qu'au premier tour de boucle), on part tout aléatoire
                                                case = choice(range(8))
                                        func,fork = self.forced_move[case]


                                func(left,right,fork=fork)
                                #on ne se déplace vraiment que maintenant
                                print(func.__name__+str(fork))
                                #et on génère le log

                                self.can_goon(left,right,i)
                                # on refait can_goon ici pour ne pas stocker de donées inutiles

                        # "mise à jour" des variables impactées par la boucle
                        self.turtles = [x for i,x in enumerate(self.turtles) if i not in self.remove]+self.adding
                        self.remove = set()
                        self.adding = list()
                        for l,r in self.turtles :
                                self.pos_turtle[(l,r)] = self.ahead(l,r)[0]

                self.draw_border()
                #on peut maintenant dessiner la bordure (déjà faite en grande partie), puis supprimer les attributs inutiles
                del self.pos_tracker, self.pos_turtle, self.remove, self.adding, self.turtles

        def can_goon(self,left,right,i):
                """Cette méthode teste si la case devant le couple (left,right) est libre ;
                sinon, si elle a atteint le bord et que la sortie (self.out) n'est pas encore définie, elle crée cette sortie.
                sinon, elle crée un cul-de-sac.
                i est nécessaire pour être rajouté à self.remove
                retour : booléeen : la case devant soi"""
                m, (fl,fr) = self.ahead(left,right)
                if abs(m[0])>Laby.RAY or abs(m[1])>Laby.RAY :
                        #limites atteintes
                        pos_a = left.pos()
                        pos_b = right.pos()
                        if self.out is None  :
                                self.out = (Laby.middle((pos_a[0],pos_b[0]),(pos_a[1],pos_b[1])))
                        else :#il n'y a pas lieu de créer une sortie ; on fait une imapasse
                                self.add_wall(left.pos(),right.pos())
                                left.goto(right.pos())
                        del self.pos_turtle[(left,right)]
                        self.remove.add(i)

                elif m in self.pos_tracker :
                        #déplacement impossible
                        self.add_wall(left.pos(),right.pos())
                        left.goto(right.pos())#on fait une impasse

                        del self.pos_turtle[(left,right)]
                        self.remove.add(i)

                else :
                        return True
                return False

        def draw_border(self):
                """Cette fonction dessine la bordure autour du labyrinthe, sauf pour l'emplacement de la sortie"""
                steps_per_side = (2*Laby.RAY)//Laby.UNIT
                t = turtle.RawTurtle(self.screen)
                t.ht()
                t.speed(0)
                t.up()
                t.goto(-Laby.RAY,-Laby.RAY)# coin en bas à gauche
                t.down()
                for _ in range(4) :
                        for _ in range(steps_per_side) :
                                p = t.pos()
                                t.forward(Laby.UNIT)
                                if Laby.middle((p[0],t.xcor()),(p[1],t.ycor())) == self.out :
                                        t.undo()
                                        t.up()
                                        t.forward(Laby.UNIT)
                                        t.down()
                                else :
                                        self.add_wall(p,t.pos())
                        t.left(90)
                self.screen.update()

        def add_wall(self,pos_a,pos_b):
                """Ajoute le mur de coordonnées délimité par pos_a et pos_b à la bonne clé de self.walls"""
                self.walls.add(Laby.middle((pos_a[0],pos_b[0]),(pos_a[1],pos_b[1])))
                self.walls.add(pos_a)
                self.walls.add(pos_b)

        def middle(x,y) :
                """renvoie (moyenne de x, moyenne de y)"""
                return (round(sum(x)/len(x)),round(sum(y)/len(y)))

        """Méthodes de déplacement : déplacent le couple (left, right).
        le(s) premiers(s) déplacement(s) concerne(nt) toujours left, puis right le cas échéant.
        Il y a toujours deux déplacements (sans compter les rotations)
        paramètre fork : faire un/des embranchement(s). 0<=fork<=3 : entier sur deux bits => nième bit = faire un embranchement lors du nième déplacement
        siilent permet de ne pas interagir avec pos_tracker, adding et add_wall. Il force fork=0"""

        def forward(self,left,right,fork=0,silent=False):
                if not silent :
                        if fork%2 :
                                new_ll = left.clone()
                                new_ll.left(90)
                                left.up()
                        else :
                                _ = left.pos()
                left.forward(Laby.UNIT)
                if not silent :
                        if fork%2 :
                                left.down()
                                new_lr = left.clone()
                                new_lr.left(90)
                                self.adding.append((new_ll,new_lr))
                        else :
                                self.add_wall(_,left.pos())

                        if fork > 1 :
                                new_rr = right.clone()
                                new_rr.right(90)
                                right.up()
                        else :
                                _ = right.pos()
                right.forward(Laby.UNIT)
                if not silent :
                        if fork > 1 :
                                right.down()
                                new_rl = right.clone()
                                new_rl.right(90)
                                self.adding.append((new_rl,new_rr))
                        else :
                                self.add_wall(_,right.pos())

        def turn_left(self,left,right,fork=0,silent=False):
                left.left(90)

                if not silent :
                        if fork%2 :
                                new_ll = right.clone()
                                new_ll.right(90)
                                right.up()
                        else :
                                _ = right.pos()
                right.forward(Laby.UNIT)
                if not silent :
                        if fork%2 :
                                right.down()
                                new_lr = right.clone()
                                new_lr.right(90)
                                self.adding.append((new_lr,new_ll))
                        else :
                                self.add_wall(_,right.pos())

                        if fork > 1 :
                                new_rr = right.clone()
                                right.up()
                        else :
                                _ = right.pos()
                right.left(90)
                right.forward(Laby.UNIT)
                if not silent :
                        if fork > 1 :
                                right.down()
                                new_rl = right.clone()
                                new_rl.right(90)
                                self.adding.append((new_rl,new_rr))
                        else :
                                self.add_wall(_,right.pos())

        def turn_right(self,left,right,fork=0,silent=False):
                right.right(90)
                if not silent :
                        if fork%2 :
                                new_ll = left.clone()
                                new_ll.left(90)
                                left.up()
                        else :
                                _ = left.pos()
                left.forward(Laby.UNIT)
                if not silent :
                        if fork%2 :
                                left.down()
                                new_lr = left.clone()
                                new_lr.left(90)
                                self.adding.append((new_ll,new_lr))
                        else :
                                self.add_wall(_,left.pos())

                        if fork > 1 :
                                new_rr = left.clone()
                                left.up()
                        else :
                                _ = left.pos()
                left.right(90)
                left.forward(Laby.UNIT)
                if not silent :
                        if fork > 1 :
                                left.down()
                                new_rl = left.clone()
                                new_rl.left(90)
                                self.adding.append((new_rr,new_rl))
                        else :
                                self.add_wall(_,left.pos())

        forced_move = property(fget=lambda self : {
                0:(self.forward,0),
                1:(self.forward,0),
                2:(self.turn_left,0),
                3:(self.turn_left,2),
                4:(self.turn_right,0),
                5:(self.turn_right,2),
                6:(self.turn_left,1),
                7:(self.forward,3)})
        """Ce dictionnaire contient la liste des déplacements dans les cas de déplacement forcés"""

        moves = property(fget=lambda self:[
                self.forward,self.turn_left,self.turn_right])
        """Cette liste est l"ensemble des déplacements possibles pour un couple"""

        def ahead(self,left,right,func=None):
                """Cette méthode "explore" la case devant (left,right) et renvoie les coordonnées de son milieu
                ainsi les turtles "fantômes" utilisés, qui résultent de func(left,right,silent=True) ; func est self.forward par défaut"""
                if func is None :
                        func = self.forward
                fake_left = left.clone()
                fake_right = right.clone()
                fake_left.up()
                fake_right.up()

                func(fake_left,fake_right,silent=True)
                m = ({left.xcor(),fake_left.xcor(),right.xcor(),fake_right.xcor()},
                     {left.ycor(),fake_left.ycor(),right.ycor(),fake_right.ycor()})
                m = [{round(x) for x in string} for string in m]
                return [Laby.middle(*m),(fake_left,fake_right)]

        def parse_area(self,x,y,nth_call=0):
                """teste si on peut atteindre un couple de turtles depuis la case de coordonnées (x,y) en moins de Laby.RANGE cases
                nth_call est utilisée pour prévenir les erreurs de récursivité"""
                self.gone.add((x,y))
                if (x,y) in self.pos_turtle.values() :
                        return True
                elif nth_call > Laby.REACH :
                        return False
                else :
                        for (i,j) in [(x-Laby.UNIT,y), (x+Laby.UNIT,y), (x,y-Laby.UNIT), (x,y+Laby.UNIT)] :
                                if (i,j) in self.pos_tracker or (i,j) in self.gone or abs(i)>=Laby.RAY or abs(j)>=Laby.RAY :
                                        continue
                                if self.parse_area(i,j,nth_call=nth_call+1) :
                                        return True
                        return False

        def testme(self):
                t = turtle.RawTurtle(self.screen)
                t.up()
                t.ht()
                for w in self.walls :
                        t.goto(w)
                        t.dot(5,"red")
class Game :

    def __init__(self, canvas, screen, players, ignition, main_window):
        """
        Fonction d'initialisation de notre classe. On définit toutes les variables dont on a besoin.
        """
        self.canvas = canvas
        self.screen = screen
        self.players = players
        self.main_window = main_window
        self.players_name = ["Joueur 1", "Joueur 2", "Joueur 3"]
        self.move_number = []
        self.coord_player = []
        self.playing = True
        self.start_game = 0
        self.end_game = 0
        self.walls = {}
        self.out = ()
        self.results = {}
        self.ignition = ignition
        #self.continuous_sound("Never_Again")

    def binding(self, event):
        """
        On récupère les entrées claviers et on dispatche. C'est plus propre et plus joli...
        """
        #On vérifie si le joueur qui veut se déplacer le peut
        if self.playing:
            str.capitalize(event.keysym)
            if str.capitalize(event.keysym) in Parameters.keys["keys_up"]:
                self.move_y(self.players[Parameters.keys["keys_up"].index(str.capitalize(event.keysym))], 10)
            elif str.capitalize(event.keysym) in Parameters.keys["keys_down"]:
                self.move_y(self.players[Parameters.keys["keys_down"].index(str.capitalize(event.keysym))], -10)
            elif str.capitalize(event.keysym) in Parameters.keys["keys_left"]:
                self.move_x(self.players[Parameters.keys["keys_left"].index(str.capitalize(event.keysym))], -10)
            elif str.capitalize(event.keysym) in Parameters.keys["keys_right"]:
                self.move_x(self.players[Parameters.keys["keys_right"].index(str.capitalize(event.keysym))], 10)
            elif str.capitalize(event.keysym) in Parameters.keys["keys_redo"]:
                self.redo_move(self.move_number[Parameters.keys["keys_redo"].index(str.capitalize(event.keysym))], self.coord_player[Parameters.keys["keys_redo"].index(str.capitalize(event.keysym))], self.players[Parameters.keys["keys_redo"].index(str.capitalize(event.keysym))])
            else:
                    return False
        else:
            return False

    def redo_move(self, move_number, coord_player, player):
        """
        Permet de retracer le parcours du joueur.
        On postionne tout d'abbord le joueur à son endroit initial
        :param move_number: le nombre de déplacement(s) du joueur.
        :param coord_player: toutes les coordonnées du joueur.
        :type move_number: int
        :type coord_player: list
        """
        self.move(0,0,player,False)

        # On parcours les coordonnées afin d'en extraire les coordonnées des points.
        for x, y in coord_player:
            #Déplace successivement le joueur de l'origine jusqu'à sa dernière position.
            self.move(x,y,player,False)

    def set_coord(self, x, y, player):
        """
        Permet de stocker les coordonnées du joueur dans une liste.

        :param x: On récupère la coordonnée x du point à enregistrer
        :param y: On récupère la coordonnée y du point à enregistrer
        :type x: float
        :type y: float:
        :return: Liste des coordonnées du joueur avec en indice le numéro
        du déplacement.
        """
        # Dans le cas du premier déplacement, il faut insérer les coordonnées
        #de l'origine
        if self.move_number[self.players.index(player)] == 0:
            self.coord_player[self.players.index(player)].append((0,0))
        #Ajouter et return les coordonnées du joueur. Retour par simple précaution, si on l'use un jour.
        self.coord_player[self.players.index(player)].append(player.position())
        return self.coord_player


    def move(self, x, y, player, stocker = True):
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
        #Si c'est le premier déplacement,
        if self.move_number[self.players.index(player)]==0:
            self.start_game = int(time.time())
        #On stocke ou pas?
        if stocker == True:
            self.set_coord(x,y, player)
            self.move_number[self.players.index(player)]  += 1
        # Check des bordures
        # Si true, alors on n'y va pas
        if self.collision_checking(x, y):
            return False
        if self.goal_checking(x, y):
            self.end_game = int(time.time())
            self.playing = False
            self.results[str(self.end_game-self.start_game)] = str(self.players_name[self.players.index(player)])
            #self.results.update({self.players_name[self.players.index(player)]: self.end_game-self.start_game})
            #On vide la fenêtre
            self.canvas.pack_forget()
            self.display_results()
        player.goto(x, y)
        self.screen.update()


    def collision_checking(self, x, y):
        """
        Checking des collisions éventuelles au pixel près.
        :param x: coordonnée x à vérifier
        :param y: coordonnée y à vérifier
        :return: True si collision et False si pas de collisions.
        """

        # Si les coordonnées (x,y) sont dans la liste des coordonnées de la bordure
        #if (x,y) in self.walls:
            #return True
        if (x,y) in self.walls:
            return True
        else:
            return False

    def goal_checking(self, x, y):
        #On utilise self.out qui contient les coordonnées de la sortie.
        if x == self.out[0] and y == self.out[1]:
            return True
        else:
            return False

    def move_x(self, player, coord = 0):
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

        self.move(player.xcor()+coord, player.ycor(), player)

    def move_y(self, player, coord = 0):
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

        self.move(player.xcor(), player.ycor()+coord, player)

    def get_walls(self, walls):
        self.walls = walls

    def get_out(self, out):
        self.out = list(out)

    def display_results(self):
        sorted(self.results.values())
        print(self.results)
        toplevel = tkinter.Toplevel(self.main_window)
        for temps, joueur in self.results.items():
            tkinter.Message(toplevel, text=str(joueur)+" en "+str(temps)+" secondes").pack()

        tkinter.Button(toplevel, text="Retour à l'accueil", command=lambda :self.ignition.set_home() and toplevel.delete()).pack()
        
    def continuous_sound(self, sound):
        player = pyglet.media.Player()
        source = pyglet.media.load("src/"+str(sound)+".wav")
        player.queue(source)
        player.play()

class Parameters :

    Players_Max = 3
    keys = {                "keys_up" : ["Up", "Z", "Y"],
                            "keys_down" : ["Down", "S", "H"],
                            "keys_left" : ["Left", "Q", "G"],
                            "keys_right" : ["Right", "D", "J"],
                            "keys_redo" : ["A", "X", "N"]
                      }
    Sounds = ["Never_Again", "K-B11"]
    RAY = Laby.RAY

    def __init__(self, parent):
        self.window = tkinter.Toplevel(parent, height = 600, width = 400)
        self.window.title("Configuration")
        #Nos labels sont dans des listes
        self.labels = {}
        self.entries = {}
        
        #Nos données aussi
        self.data = {
        "RAY" : Parameters.RAY
        }
        
        self.get_settings()
        

    def set_players(self):
##        for i in range(int(self.data["players"].get())):
##            Ignition.PLAYERS = list(range(i+1))
        Ignition.PLAYERS = list(range(int(self.data["players"].get())))
        self.set_settings()
        self.get_settings()

    def set_settings(self):
        print(self.entries)
        for command, key in self.entries.items():
                print(command, key)
                Parameters.keys[str(command)][:len(key)] = [widget.get() for widget in key]
                print(Parameters.keys)
    

    def get_settings(self):

        self.labels["Label"] = tkinter.Label(self.window, text="Nombre de joueur(s) : ")
        self.labels["Label"].grid(column=1, row=1)
        self.data["players"] = tkinter.Spinbox(self.window, from_=1, to=3)
        self.data["players"].grid(column=2, row=1)

        tkinter.Button(self.window, text="Valider", command=self.set_players).grid(column=4, row=1)

        #self.window.after(1000, self.get_settings)

        self.labels["Commandes"] = tkinter.Label(self.window, text="Commandes").grid(column=1, row=3)
        self.labels["sound"] = tkinter.Label(self.window, text="Choisissez votre musique :").grid(column=1, row=2)
        self.data["sound"] = tkinter.Spinbox(self.window, values=Parameters.Sounds).grid(column=2, row=2)
##        for i in range(len(Ignition.PLAYERS)):
##            #On fait les labels de la page
        if True :
            self.labels["players"] = [tkinter.Label(self.window, text="Joueur "+str(i+1)) for i in Ignition.PLAYERS]
            [widget.grid(column=2+i, row=4) for i,widget in enumerate(self.labels["players"])]
            
            self.labels["keys_up"] = tkinter.Label(self.window, text="Haut")
            self.labels["keys_up"].grid(column=1, row=5)
            self.labels["keys_down"] = tkinter.Label(self.window, text="Bas")
            self.labels["keys_down"].grid(column=1, row=6)
            self.labels["keys_left"] = tkinter.Label(self.window, text="Gauche")
            self.labels["keys_left"].grid(column=1, row=7)
            self.labels["keys_right"] = tkinter.Label(self.window, text="Droite")
            self.labels["keys_right"].grid(column=1, row=8)
            self.labels["keys_redo"] = tkinter.Label(self.window, text="Refaire")
            self.labels["keys_redo"].grid(column=1, row=9)

            self.entries["keys_up"] = [tkinter.Entry(self.window) for i in Ignition.PLAYERS]
            for i,widget in enumerate(self.entries["keys_up"]) :
                    widget.insert(0,Parameters.keys["keys_up"][i])
                    widget.bind("<Key>",lambda event : widget.insert(0,event.char))
                    widget.grid(column=2+i, row=5, padx=5, pady=5)

            self.entries["keys_down"] = [tkinter.Entry(self.window) for i in Ignition.PLAYERS]
            for i,widget in enumerate(self.entries["keys_down"]) :
                    widget.insert(0, Parameters.keys["keys_down"][i])
                    widget.bind("<Key>",lambda event : widget.insert(0,event.char))
                    widget.grid(column=2+i, row=6, padx=5, pady=5)

            self.entries["keys_left"] = [tkinter.Entry(self.window) for i in Ignition.PLAYERS]
            for i,widget in enumerate(self.entries["keys_left"]) :
                    widget.insert(0, Parameters.keys["keys_left"][i])
                    widget.bind("<Key>",lambda event : widget.insert(0,event.char))
                    widget.grid(column=2+i, row=7, padx=5, pady=5)

            self.entries["keys_right"] = [tkinter.Entry(self.window) for i in Ignition.PLAYERS]
            for i,widget in enumerate(self.entries["keys_right"]) :
                    widget.insert(0, Parameters.keys["keys_right"][i])
                    widget.bind("<Key>",lambda event : widget.insert(0,event.char))
                    widget.grid(column=2+i, row=8, padx=5, pady=5)

            self.entries["keys_redo"] = [tkinter.Entry(self.window) for i in Ignition.PLAYERS]
            for i,widget in enumerate(self.entries["keys_redo"]) :
                    widget.insert(0, Parameters.keys["keys_redo"][i])
                    widget.bind("<Key>",lambda event : widget.insert(0,event.char))
                    widget.grid(column=2+i, row=9, padx=5, pady=5)


class Ignition :
    PLAYERS = [0,1]
    SOUND = "Never_Again"

    def __init__(self, buildfile=None):
        self.players = Ignition.PLAYERS
        self.players_color = ["red", "green", "blue", "purple", "green", "yellow", "black", "pink", "grey"]
        self.buildfile = buildfile
        self.is_in_game = False
        self.color = 0

        self.main_window = tkinter.Tk()
        #On dimensionne la fenêtre à la taille de l'image
        self.main_window.geometry("941x756")

        self.set_home()

        self.main_window.bind("<Button-1>", self.home_binding)
        self.main_window.mainloop()

    def set_home(self):
        self.is_in_game = False
        self.main_window.title("Super Maze")
        self.home_maze = Image.open("src/home_maze.png")
        self.photo = ImageTk.PhotoImage(self.home_maze)
        self.main_canvas = tkinter.Canvas(self.main_window, width=self.home_maze.size[0], height = self.home_maze.size[1])
        self.main_canvas.create_image(0,0, anchor = tkinter.NW, image=self.photo)
        self.main_canvas.pack()

    def init_solo_game(self):
        self.is_in_game = True
        self.main_window.title("Super Maze - Partie Solo")
        self.canvas = turtle.ScrolledCanvas(self.main_window)
        self.screen = turtle.TurtleScreen(self.canvas)

        self.canvas.pack(fill="both",expand=True)

        self.game = Game(self.canvas, self.screen, [0], self, self.main_window)

        #On initialise nos turtles de joueur(s)
        for i in self.game.players:
            self.game.players[i] = turtle.RawTurtle(self.screen)
            self.game.players[i].st()
            self.game.players[i].up()
            self.game.players[i].home()
            self.game.players[i].speed(0)
            self.color = self.players_color[randint(0, len(self.players_color)-1)]
            self.game.players[i].fillcolor(self.color)
            self.game.move_number.append(0)
            self.game.coord_player.append([])
            #On affiche la couleur du joueur:
            tkinter.Label(self.canvas, text="Joueur "+str(i+1), fg=self.game.players[i].fillcolor()).grid(row=1, column=1)

        self.laby = Laby(self.canvas, self.screen, self.buildfile)
        self.screen.tracer(delay=None)

        self.game.get_walls(self.laby.walls)
        self.game.get_out(self.laby.out)

        self.main_window.bind("<Key>", self.game.binding)

    def init_multi_game(self):
        self.is_in_game = True
        self.main_window.title("Super Maze - Partie Locale")
        self.canvas = turtle.ScrolledCanvas(self.main_window)
        self.screen = turtle.TurtleScreen(self.canvas)

        self.canvas.pack(fill="both",expand=True)

        self.game = Game(self.canvas, self.screen, Ignition.PLAYERS, self, self.main_window)

        #On initialise nos turtles de joueur(s)
        for i in range(len(Ignition.PLAYERS)):
            self.game.players[i] = turtle.RawTurtle(self.screen)
            self.game.players[i].st()
            self.game.players[i].up()
            self.game.players[i].home()
            self.game.players[i].speed(0)
            self.color = self.players_color[randint(0, len(self.players_color))]
            self.game.players[i].fillcolor(self.color)
            self.game.move_number.append(0)
            self.game.coord_player.append([])
            #On affiche la couleur du joueur:
            tkinter.Label(self.canvas, text="Joueur "+str(i+1), fg=self.game.players[i].fillcolor()).grid(row=1, column=1)


        self.laby = Laby(self.canvas, self.screen, self.buildfile)
        self.screen.tracer(delay=None)

        self.game.get_walls(self.laby.walls)
        self.game.get_out(self.laby.out)

        self.main_window.bind("<Key>", self.game.binding)

    def init_network_game(self):
        return True
    def home_binding(self, event):
        if self.is_in_game == False:
            if event.y > 160 and event.y < 210 and event.x > 370 and event.x < 630:
                self.main_canvas.pack_forget()
                self.init_solo_game()
            elif event.y > 430 and event.y < 480 and event.x > 160 and event.x < 440:
                self.main_canvas.pack_forget()
                self.init_multi_game()
            elif event.y > 560 and event.y < 610 and event.x > 500 and event.x < 830:
                self.main_canvas.pack_forget()
                self.init_network_game()
            elif event.y > 660 and event.y < 720 and event.x > 90 and event.x < 380:
                Parameters(self.main_window)
            else:
                return False


if __name__ == '__main__':
    #Pour la ligne de commande
        from sys import argv
        buildfile = None
        if len(argv) > 1 :
                Ignition.buildfile = open(argv[1])
        if len(argv) > 2 :
                Laby.RAY = int(argv[2])

        ignition = Ignition(buildfile)
