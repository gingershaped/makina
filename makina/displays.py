import traceback
from time import sleep
from sys import stderr
from makina.constants import *

try:
    import turtle
except ImportError:
    turtle = None

class Display:
    def __init__(self, world):
        self.world = world
        self._log = ""
    def clear(self):
        print("\033[2J", end="")
        print("\033[H", end="")
    def log(self, text, end="\n"):
        self._log += str(text)
        self._log += end
    def blit(self):
        pass
    def error(self, text, pos=None):
        if issubclass(type(text), Exception):
            traceback.print_exc()
        else:
            print(text, file=stderr)
        if pos:
            print("at position:", pos, file=stderr)

    def onNewAutomaton(self, automaton):
        pass
    def onAutomatonHalted(self, automaton):
        pass
    def onAutomatonChild(self, automaton, child):
        pass
    def onAutomatonMove(self, automaton, direction):
        pass

class SimpleDisplay(Display):
    def log(self, text, end = "\n"):
        print(text, end = end, flush = True)

class FancyDisplay(Display):
    def __init__(self, world):
        super().__init__(world)
        print("\033[?25l")
    def __del__(self):
        print("\033[?25h")
    def blit(self):
        self.clear()
        d = self.world.array.copy()
        for i in self.world.tickingList:
            try:
                d[i.position[0], i.position[1]] = "@"
            except IndexError:
                pass
        for row in d:
            r = ""
            for c in row:
                r += c
            print(r)
        print("--------")
        for l in self._log.split("\n"):
            print(l)
        sleep(0.1)
    def error(self, message, pos):
        self.clear()
        d = self.world.array.copy()
        for i in self.world.tickingList:
            try:
                d[i.position[0], i.position[1]] = "@"
            except IndexError:
                pass
        for x, row in enumerate(d):
            for y, c in enumerate(row):
                if x == pos[0] and y == pos[1]:
                    print("\x1b[1;31m@\x1b[0m", end="")
                else:
                    print(c, end="")
            print()
        print("--------")
        super().error(message, pos)
        print("--------")
        for l in self._log.split("\n"):
            print(l)
        sleep(0.1)

class TurtleDisplay(Display):
    ANGLEFORDIRECTION = {Direction.UP: 0, Direction.DOWN: 180, Direction.LEFT: 270, Direction.RIGHT: 90}
    COLORS = ["red", "green", "blue", "orange", "purple"]
    def __init__(self, world):
        super().__init__(world)
        if not turtle:
            print("The turtle module is needed to use the turtle display!", file=sys.stderr)
            exit(1)
        turtle.mode("logo")
        turtle.tracer(0)
        turtle.screensize(1000, 1000)
        turtle.register_shape("cross", ((-5, -5), (5, 5), (0, 0), (5, -5), (-5, 5), (0, 0)))
        self.color = 0
        self.turtles = {}
        self.labelTurtle = turtle.Turtle()
        self.labelTurtle.up()
        self.labelTurtle.ht()
        for y, row in enumerate(world.array):
            for x, char in enumerate(row):
                self.labelTurtle.goto(x * 8 * 2 - 8, -y * 8 * 2 - 8)
                self.labelTurtle.write(char, align = "center")
        turtle.update()
    def clear(self):
        turtle.clearscreen()
    def log(self, text, end = "\n"):
        print(text, end = end, flush = True)
    
    def blit(self):
        turtle.update()
        sleep(0.1)

    def onNewAutomaton(self, automaton):
        t = turtle.Turtle()
        t.up()
        t.setpos(automaton.position[1] * 16 - 8, -automaton.position[0] * 16)
        t.setheading(TurtleDisplay.ANGLEFORDIRECTION[automaton.direction])
        t.pencolor(TurtleDisplay.COLORS[self.color])
        self.color += 1
        if self.color >= len(TurtleDisplay.COLORS):
            self.color = 0
        t.down()
        self.turtles[automaton] = t
    def onAutomatonMove(self, automaton, direction):
        t = self.turtles[automaton]
        t.setpos(automaton.position[1] * 16 - 8, -automaton.position[0] * 16)
        t.setheading(TurtleDisplay.ANGLEFORDIRECTION[automaton.direction])
    def onAutomatonHalted(self, automaton):
        t = self.turtles[automaton]
        t.clear()
        t.ht()

    def error(self, message, pos):
        super().error(message, pos)
        t = None
        for automaton in self.turtles:
            if automaton.position == pos:
                t = self.turtles[automaton]
        t.shape("cross")
        while True:
            turtle.update()