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
"""

left = turtle.RawTurtle(screen)#le mur gauche
right = turtle.RawTurtle(screen)#le mur droit

left.speed(0)#i.e. max
right.speed(0)

left.up()
left.goto((0,10))
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
                if track :
                        global pos_tracker
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
        left.forward(10)
        if fork%2 :
                left.down()
                new_lr = left.clone()
                new_lr.left(90)
                created.append([new_ll,new_lr])

        if fork > 1 :
                new_rr = right.clone()
                new_rr.right(90)
                right.up()
        right.forward(10)
        if fork > 1 :
                right.down()
                new_rl = right.clone()
                new_rl.right(90)
                created.append([new_rl,new_rr])
        return created

@decorator
def turn_left(left,right,fork=0):
        created = list()
        left.left(90)

        if fork%2 :
                new_ll = right.clone()
                new_ll.right(90)
                right.up()
        right.forward(10)
        if fork%2 :
                right.down()
                new_lr = right.clone()
                new_lr.right(90)
                created.append([new_lr,new_ll])

        if fork > 1 :
                new_rr = right.clone()
                right.up()
        right.left(90)
        right.forward(10)
        if fork > 1 :
                right.down()
                new_rl = right.clone()
                new_rl.right(90)
                created.append([new_rl,new_rr])
        return created

@decorator
def turn_right(left,right,fork=0):
        created = list()
        right.right(90)
        if fork%2 :
                new_ll = left.clone()
                new_ll.left(90)
                left.up()
        left.forward(10)
        if fork%2 :
                left.down()
                new_lr = left.clone()
                new_lr.left(90)
                created.append([new_ll,new_lr])

        if fork > 1 :
                new_rr = left.clone()
                left.up()
        left.right(90)
        left.forward(10)
        if fork > 1 :
                left.down()
                new_rl = left.clone()
                new_rl.left(90)
                created.append([new_rr,new_rl])
        return created


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
                fake_left.ht()
                fake_right.ht()
                
                forward(fake_left,fake_right,track=False)
                m = ({left.xcor(),fake_left.xcor(),right.xcor(),fake_right.xcor()},
                     {left.ycor(),fake_left.ycor(),right.ycor(),fake_right.ycor()})
                m = [{round(x) for x in string} for string in m]
                m = middle(*m)
                if m not in pos_tracker :
                        func = choice([forward,turn_left,turn_right])
                        adding.extend(func(left,right,fork=randrange(4)))
                        fake_left.goto(m)
                        fake_left.dot(3,"blue")
                else :
                        remove.add(i)

        turtles,remove,adding = [x for i,x in enumerate(turtles) if i not in remove]+adding,set(),list()

main_window.mainloop()
