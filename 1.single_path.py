#!/usr/bin/env python3
import turtle, tkinter
from random import choice

main_window = tkinter.Tk()
canvas = turtle.ScrolledCanvas(main_window)
canvas.pack(fill="both",expand=True)
screen = turtle.TurtleScreen(canvas)

"""
Ce script :
- crée une GUI pour turtle (l.6-9)
- crée un chemin aléatoire, sans embranchement, justqu'à ce qu'il se referme sur lui-même
"""

left = turtle.RawTurtle(screen)#le mur gauche
right = turtle.RawTurtle(screen)#le mur droit

left.speed(0)#i.e. max
right.speed(0)

left.up()
left.goto((0,10))
left.down()

pos_tracker = set()


def middle(x,y) :
        return (sum(x)/len(x),sum(y)/len(y))

def record_track(func):
        def f(left,right,track=True):
                if track :
                        global pos_tracker
                        x = {left.xcor(),right.xcor()}
                        y = {left.ycor(),right.ycor()}
                func(left,right)
                #les turtles ne se déplacent pas précisément ;
                #on les fait ici arriver sur des coordonnées entières
                left.goto(round(left.xcor()),round(left.ycor()))
                right.goto(round(right.xcor()),round(right.ycor()))
                if track :
                        x |= {left.xcor(),right.xcor()}
                        y |= {left.ycor(),right.ycor()}
                        pos_tracker.add(middle(x,y))
        f.__qualname__ = func.__qualname__
        return f

@record_track
def forward(left,right):
        left.forward(10)
        right.forward(10)

@record_track
def turn_left(left,right):
        left.left(90)
        right.forward(10)
        right.left(90)
        right.forward(10)

@record_track
def turn_right(left,right):
        left.forward(10)
        left.right(90)
        left.forward(10)
        right.right(90)


while True :
        fake_left = left.clone()
        fake_right = right.clone()
        fake_left.up()
        fake_right.up()
        fake_left.ht()
        fake_right.ht()

        forward(fake_left,fake_right,track=False)#we use forward, turn_left or _right would have done the same thing.
        m = ({left.xcor(),fake_left.xcor(),right.xcor(),fake_right.xcor()}, {left.ycor(),fake_left.ycor(),right.ycor(),fake_right.ycor()})
        m = middle(*m)
        if m not in pos_tracker :
                choice([forward,turn_left,turn_right])(left,right)
        else :
                break
left.ht()
right.ht()
main_window.mainloop()
