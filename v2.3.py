import tkinter
import turtle
import time
from random import choice

"""
Version 2.2.3 du projet Super Maze

Première intégration de la génération et des déplacements.

Seul problème rencontré :
Il faut définir les murs par le milieu du mur et non son extrêmité haute. Car le joueur se déplace sur des milieux de murs.
"""

"""
logs :
- forward|turn_left|turn_right
- 0|1|2|3
"""

playing = True
players = [0, 1]
keys_up = ["Up", "Z"]
keys_down = ["Down", "S"]
keys_left = ["Left", "Q"]
keys_right = ["Right", "D"]
keys_redo = ["A", "X"]

class Laby :

        UNIT = 20
        RAY = 200
        # WARNING : (2*RAY)/UNIT MUST BE integer
        FREQ = 30
        REACH = 20#la 'portée' d'un curseur

        def __init__(self,canvas, screen, buildfile=None):
                """Attributs :
                - self.canvas (passé comme paramètre)
                - self.screen : couche de liaison entre turtle et tkinter
                - self.walls : contient, dans deux clés séparées, les murs verticaux et horizontaux"""
                self.canvas = canvas
                #self.screen = turtle.TurtleScreen(self.canvas)
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

                self.walls = dict(v=set(),h=set())
                # cet attribut contient les coordonnées des murs tracés
                # (v:vertical ; h:horizontal)
                # un mur est défini par les coordonnées du coin en haut à droite

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
        retour : booléeen : la case devant soi
"""
                m, (fl,fr) = self.ahead(left,right)
                if abs(m[0])>Laby.RAY or abs(m[1])>Laby.RAY :
                        #limites atteintes

                        del self.pos_turtle[(left,right)]
                        self.remove.add(i)

                        #voir add_wall
                        pos_a = left.pos()
                        pos_b = right.pos()
                        if pos_a[0] == pos_b[0] and self.out is None and (round(pos_a[0]),round(max(pos_a[1],pos_b[1]))) != (Laby.RAY,Laby.RAY) :
                                #le mur est vertical
                                self.out = (round(pos_a[0]),round(max(pos_a[1],pos_b[1])))
                        elif self.out is None and (round(pos_a[0]),round(max(pos_a[1],pos_b[1]))) != (Laby.RAY,Laby.RAY) :
                                self.out = (round(max(pos_a[0],pos_b[0])) ,round(pos_a[1]))
                        else :#il n'y a pas lieu de créer une sortie ; on fait une imapasse
                               left.goto(right.pos())
                elif m in self.pos_tracker :
                        #déplacement impossible
                        left.goto(right.pos())#on fait une impasse

                        del self.pos_turtle[(left,right)]
                        self.remove.add(i)

                else :
                        return True
                return False

        def draw_border(self):
                """Cette fonction dessine la bordure autour du labyrinthe, sauf pour l'emplacement de la sortie"""
                steps_per_side = (2*Laby.RAY)//Laby.UNIT#le nombre de cases par côté
                t = turtle.RawTurtle(self.screen)
                t.ht()
                t.speed(0)
                t.up()
                t.goto(Laby.RAY,Laby.RAY)# coin en haut à droite
                t.down()
                t.right(90)
                t_ = t.clone()
                t_.right(90)
                #on doit aborder chaque côté par le coin en haut à droite (un mur est défini par le coin en haut à droite)
                #on crée donc deux turtles qui feront chacunes un demi-périmètre en partant de ce coin

                #t tourne en sens +
                #t_ tourne en sens -

                for a in range(2):#2 car 4 côtés du labytinthe // 2 turtles qui y travaillent
                        for b in range(steps_per_side):
                                for cursor in (t,t_):
                                        if cursor.pos() == self.out :#si on est sur la sortie, on ne dessine pas de bordure
                                                cursor.up()
                                                cursor.forward(Laby.UNIT)
                                                cursor.down()
                                        else :#sinon, on dessine ET on rajoute le mur qui correspond
                                                start = cursor.pos()
                                                cursor.forward(Laby.UNIT)
                                                self.add_wall(start,cursor.pos())
                        t.right(90)
                        t_.left(90)
                self.screen.update()#cette ligne semble nécessaire ; elle met à jour le dessin global du labyrinthe
        def moyenne(x,y,z):
            if x == int and y == int():
                return (x|y)/2
        def add_wall(self,pos_a,pos_b):
                """Ajoute le mur de coordonnées délimité par pos_a et pos_b à la bonne clé de self.walls"""

                if pos_a[0] == pos_b[0]:#le mur est vertical
                        self.walls["v"].add((pos_a[0], max(pos_a[1],pos_b[1]) ))
                        #Rajout d'Alexandre:
                else :#le mur est horizontal
                        self.walls["h"].add((max(pos_a[0],pos_b[0]),pos_a[1]))
                        #Marche uniquement si les deux coordonnées sont uniquement positives ou négatives
                        #self.walls["h"].add(( (pos_a[0]+pos_b[0])/2, pos_a[1] ))


        def middle(x,y) :
                """renvoie (moyenne de x, moyenne de y)"""
                return (sum(x)/len(x),sum(y)/len(y))

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

class Game :



    def __init__(self, canvas, screen, players):
        """
        Fonction d'initialisation de notre classe. On définit toutes les variables dont on a besoin.
        """
        self.canvas = canvas
        self.screen = screen
        self.players = players
        self.move_number = []
        self.coord_player = []
        self.playing = True
        self.start_game = 0
        self.end_game = 0
        self.walls = {}
        self.out = ()

    def binding(self, event):
        """
        On récupère les entrées claviers et on dispatche. C'est plus propre et plus joli...
        """
        if game.binding:
            str.capitalize(event.keysym)
            if str.capitalize(event.keysym) in keys_up:
                self.move_y(self.players[keys_up.index(str.capitalize(event.keysym))], 10)
            elif str.capitalize(event.keysym) in keys_down:
                self.move_y(self.players[keys_down.index(str.capitalize(event.keysym))], -10)
            elif str.capitalize(event.keysym) in keys_left:
                self.move_x(self.players[keys_left.index(str.capitalize(event.keysym))], -10)
            elif str.capitalize(event.keysym) in keys_right:
                self.move_x(self.players[keys_right.index(str.capitalize(event.keysym))], 10)
            elif str.capitalize(event.keysym) in keys_redo:
                self.redo_move(move_number, coord_player, self.players[keys_redo.index(str.capitalize(event.keysym))])
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
        for x, y in coord_player[self.players.index(player)]:
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

        print(x ,y)


        # Check des bordures
        # Si true, alors on n'y va pas
        if self.collision_checking(x, y):
            return False
        if self.goal_checking(x, y):
            self.end_game = int(time.time())
            self.playing = False
            return False
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
        #On utilise laby.out qui contient les coordonnées de la sortie.
        print(self.out)
        if (x,y) == self.out:
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
        self.walls = walls["h"] | walls["v"]

    def get_out(self, out):
        self.out = out

class Parameters :

    def __init__(self, main_window):
        self.param_window = Toplevel(main_window)


if __name__ == '__main__':
        from sys import argv
        buildfile = None
        if len(argv) > 1 :
                buildfile = open(argv[1])
        if len(argv) > 2 :
                Laby.RAY = int(argv[2])
        main_window = tkinter.Tk()
        canvas = turtle.ScrolledCanvas(main_window)
        screen = turtle.TurtleScreen(canvas)
        turtles = turtle.RawTurtle(canvas)
        turtles.color("red")

        canvas.pack(fill="both",expand=True)

        game = Game(canvas, screen, players)
        #On initialise nos turtles de joueur(s)
        for i in range(len(game.players)):
            print(i)
            game.players[i] = turtle.RawTurtle(screen)
            game.players[i].st()
            game.players[i].up()
            game.players[i].home()
            game.players[i].speed(0)
            game.move_number.append(0)
            game.coord_player.append([])


        laby = Laby(canvas, screen, buildfile)
        screen.tracer(delay=None)

        game.get_walls(laby.walls)
        game.get_out(laby.out)
        if game.playing:
            main_window.bind("<Key>", game.binding)

        screen.onkey(turtles.goto(100, 100),"a")
        screen.listen()
        main_window.mainloop()
