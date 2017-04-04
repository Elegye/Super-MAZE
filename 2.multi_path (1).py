#!/usr/bin/env python3
import turtle, tkinter
from random import choice, randrange

main_window = tkinter.Tk()
canvas = turtle.ScrolledCanvas(main_window)
canvas.pack(fill="both",expand=True)
screen = turtle.TurtleScreen(canvas)

"""
Ce script :
- crée une GUI pour turtle (l.6-9)
- crée un labyrinthe aléatoire jusqu'à ce qu'il se referme sur lui-même
Cette version est un peu plus lente que l'autre
"""

left = turtle.RawTurtle(screen)#le mur gauche
right = turtle.RawTurtle(screen)#le mur droit

left.speed(0)#i.e. max
right.speed(0)

left.color("red")
right.color("red")

left.up()
left.goto((0,10))
left.down()
left.ht()
right.ht()

proba_law = lambda : randrange(5)>3

def middle(x,y) :
        return (sum(x)/len(x),sum(y)/len(y))

def step(turtle,wall=1):
        """wall arg : set to -1 for a left wall, and to 1 for a right wall"""
        if proba_law() :
                t0 = turtle.clone()
                t0.right(90*wall)
                turtle.up()
                turtle.forward(10)
                turtle.down()
                t1 = turtle.clone()
                t1.right(90*wall)
                if wall == -1 :
                        return [[t0,t1],]
                else :
                        return [[t1,t0],]
        else :
                turtle.forward(10)
                return list()

def decorator(func):
        def f(left,right,track=True):
                if track :
                        global pos_tracker
                        x = {left.xcor(),right.xcor()}
                        y = {left.ycor(),right.ycor()}

                result = func(left,right)
                #les turtles ne se déplacent pas précisément ;
                #on les fait ici arriver sur des coordonnées entières
                left.goto(round(left.xcor()),round(left.ycor()))
                right.goto(round(right.xcor()),round(right.ycor()))

                if track :
                        x |= {left.xcor(),right.xcor()}
                        y |= {left.ycor(),right.ycor()}
                        pos_tracker.add(middle(x,y))
                return result

        f.__qualname__ = func.__qualname__
        return f


@decorator
def forward(left,right):
        return step(left,-1)+step(right,1)

@decorator
def turn_left(left,right):
        left.left(90)
        _ = step(right,1)
        right.left(90)
        return _+step(right,1)

@decorator
def turn_right(left,right):
        right.right(90)
        _ = step(left,-1)
        left.right(90)
        return _+step(left,-1)


pos_tracker = set()

turtles = [[left,right],]
remove = set()
adding = list()

while len(turtles) :
        for i,couple in enumerate(turtles):
                left,right = couple
                fake_left = left.clone()
                fake_right = right.clone()
                fake_left.up()
                fake_right.up()
                # fake_left.ht()
                # fake_right.ht()

                forward(fake_left,fake_right,track=False)
                m = ({left.xcor(),fake_left.xcor(),right.xcor(),fake_right.xcor()},
                     {left.ycor(),fake_left.ycor(),right.ycor(),fake_right.ycor()})
                m = [{round(x) for x in string} for string in m]
                m = middle(*m)
                if m not in pos_tracker :
                        func = choice([forward,turn_left,turn_right])
                        adding.extend(func(left,right))
                        # fake_left.goto(m)
                        # fake_left.dot(5,"red")
                else :
                        remove.add(i)
                        # left.ht()
                        # right.ht()

        turtles,remove,adding = [x for i,x in enumerate(turtles) if i not in remove]+adding,set(),list()

main_window.mainloop()
