#!/usr/bin/env python3
import turtle, tkinter, itertools
from random import choice, randrange

UNIT = 20
RAY = 200

main_window = tkinter.Tk()
canvas = turtle.ScrolledCanvas(main_window)
canvas.pack(fill="both",expand=True)
screen = turtle.TurtleScreen(canvas)
screen.tracer(n=60)

"""
Ce script :
- crée une GUI pour turtle (l.6-9)
- crée un labyrinthe aléatoire jusqu'à ce qu'il se referme sur lui-même
"""

left = turtle.RawTurtle(screen)#le mur gauche
right = turtle.RawTurtle(screen)#le mur droit

left.speed(0)#i.e. max
right.speed(0)

left.up()
left.goto((0,UNIT))
left.down()
left.ht()
right.ht()


def middle(x,y) :
        return (sum(x)/len(x),sum(y)/len(y))

def decorator(func):
        def f(left,right,track=True,fork=0):
                """fork is used to make forks in the labyrinthe
                 case : 0 no fork
                 case 1 : fork on the first move
                 case 2 : fork on the second move
                 case 3 : for on both moves
                 priority : moves are made first for left, then for right"""
                assert round(left.distance(right)) == UNIT
                if track :
                        global pos_tracker, pos_turtle
                        x = {round(left.xcor()),round(right.xcor())}
                        y = {round(left.ycor()),round(right.ycor())}


                result = func(left,right,fork)
                #les turtles ne se déplacent pas précisément ;
                #on les fait ici arriver sur des coordonnées entières
                left.goto(round(left.xcor()),round(left.ycor()))
                right.goto(round(right.xcor()),round(right.ycor()))

                if track :
                        x |= {round(left.xcor()),round(right.xcor())}
                        y |= {round(left.ycor()),round(right.ycor())}
                        pos_tracker.add(middle(x,y))

                        for l,r in [(left,right)]+result :
                                pos_turtle[(l,r)] = ahead(l,r)[0]
                return result

        f.__qualname__ = func.__qualname__
        return f


@decorator
def forward(left,right,fork=0):
        created = list()
        if fork%2 :
                new_ll = left.clone()
                new_ll.left(90)
                left.up()
        left.forward( UNIT)
        if fork%2 :
                left.down()
                new_lr = left.clone()
                new_lr.left(90)
                created.append((new_ll,new_lr))

        if fork > 1 :
                new_rr = right.clone()
                new_rr.right(90)
                right.up()
        right.forward( UNIT)
        if fork > 1 :
                right.down()
                new_rl = right.clone()
                new_rl.right(90)
                created.append((new_rl,new_rr))
        return created

@decorator
def turn_left(left,right,fork=0):
        created = list()
        left.left(90)

        if fork%2 :
                new_ll = right.clone()
                new_ll.right(90)
                right.up()
        right.forward( UNIT)
        if fork%2 :
                right.down()
                new_lr = right.clone()
                new_lr.right(90)
                created.append((new_lr,new_ll))

        if fork > 1 :
                new_rr = right.clone()
                right.up()
        right.left(90)
        right.forward( UNIT)
        if fork > 1 :
                right.down()
                new_rl = right.clone()
                new_rl.right(90)
                created.append((new_rl,new_rr))
        return created

@decorator
def turn_right(left,right,fork=0):
        created = list()
        right.right(90)
        if fork%2 :
                new_ll = left.clone()
                new_ll.left(90)
                left.up()
        left.forward( UNIT)
        if fork%2 :
                left.down()
                new_lr = left.clone()
                new_lr.left(90)
                created.append((new_ll,new_lr))

        if fork > 1 :
                new_rr = left.clone()
                left.up()
        left.right(90)
        left.forward( UNIT)
        if fork > 1 :
                left.down()
                new_rl = left.clone()
                new_rl.left(90)
                created.append((new_rr,new_rl))
        return created

def ahead(left,right,func=forward):
        fake_left = left.clone()
        fake_right = right.clone()
        fake_left.up()
        fake_right.up()
        fake_left.ht()
        fake_right.ht()

        func(fake_left,fake_right,track=False)
        m = ({left.xcor(),fake_left.xcor(),right.xcor(),fake_right.xcor()},
             {left.ycor(),fake_left.ycor(),right.ycor(),fake_right.ycor()})
        m = [{round(x) for x in string} for string in m]
        return [middle(*m),(fake_left,fake_right)]

def parse_area(x,y,avoid=-1):
        """return True if a turtle couple can be reached from (x,y)"""
        if (x,y) in gone :
                return False
        gone.add((x,y))
        if (x,y) in pos_turtle.values() :
                return True
        else :
                for n,(i,j) in enumerate([(x-10,y), (x+10,y), (x,y-10), (x,y+10)]) :
                        if (i,j) in pos_tracker or abs(i)<=RAY or abs(j)<=RAY or n==avoid:
                                continue
                        if parse_area(x,y,avoid=n^1) :
                                return True
                return False


forced_move = {
        0:(forward,0),
        1:(forward,0),
        2:(turn_left,0),
        3:(turn_left,2),
        4:(turn_right,0),
        5:(turn_right,2),
        6:(turn_left,1),
        7:(forward,3)}

pos_tracker = set()
pos_turtle = dict()

turtles = [(left,right),]
remove = set()
adding = list()

while len(turtles)  :
        print(len(turtles),end="")
        for i,(left,right) in enumerate(turtles):
                m, (fl,fr) = ahead(left,right)
                if m in pos_tracker  or abs(m[0])>RAY or abs(m[1])>RAY  :#déplacement impossible / limites atteintes
                        left.goto(right.pos())
                        del pos_turtle[(left,right)]
                        remove.add(i)
                        print(".",end="")
                        continue

                pos_tracker.add(m)

                #le déplacement doit-il être aléatoire ou forcé ?
                reachable = False
                for func in [forward,turn_left,turn_right] :
                        gone = set()
                        if parse_area(*ahead(*ahead(fl,fr,func)[1])[0]):
                                reachable = True
                # gone = set()
                # reachable = parse_area(*m)
                # if  reachable :
                #         left.color("red");right.color("red")
                #         input("?")
                #         left.color("black");right.color("black")
                # else :
                #         left.color("blue");right.color("blue")
                #         input("!")
                #         left.color("black");right.color("black")


                if reachable :#déplacement aléatoire
                        func = choice([forward,turn_left,turn_right])
                        fork = randrange(4)
                        print("-",end="")
                else :#déplacement forcé
                        case = 0
                        for j,func in enumerate([forward,turn_left,turn_right]) :
                                fl,fr = ahead(left,right,func)[1]
                                if ahead(fl,fr)[0] not in pos_tracker :
                                        case += 2**j
                        func,fork = forced_move[case]
                        print("_",end="")

                fl.goto(ahead(left,right)[0])
                fl.dot(5,"blue")
                adding.extend(func(left,right,fork=fork))

                m, (fl,fr) = ahead(left,right)
                if m in pos_tracker or abs(m[0])>RAY or abs(m[1])>RAY :#déplacement impossible
                        left.goto(right.pos())
                        del pos_turtle[(left,right)]
                        remove.add(i)
                        print(".",end="")
        print()

        turtles,remove,adding = [x for i,x in enumerate(turtles) if i not in remove]+adding, set(), list()
main_window.mainloop()
