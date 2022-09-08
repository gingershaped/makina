import numpy as np
from makina.constants import *
from makina.instructions import reg
from makina.displays import *
from copy import deepcopy
from time import sleep
import argparse

DIRMAP = {Direction.UP: (0, -1), Direction.DOWN: (0, 1), Direction.RIGHT: (1, 1), Direction.LEFT: (1, -1)}
DISPLAYS = {
    "simple": {
        "desc": "(default) No graphics, just I/O. Fastest by far.",
        "display": SimpleDisplay
    },
    "fancy": {
        "desc": "Display ASCII-art of the program running in your terminal.",
        "display": FancyDisplay
    },
    "turtle": {
        "desc": "(requires turtle module) Display a graphical version of the program running.",
        "display": TurtleDisplay
    }
}

class World:
    @classmethod
    def fromData(cls, data, display = None, rowsep = "\n"):
        lines = data.split(rowsep)
        cells = [list(x) for x in lines]
        maxWidth = max([len(x) for x in lines])
        for r in cells:
            if len(r) < maxWidth:
                for x in range(maxWidth - len(r)):
                    r.append("")
        return World(np.array(cells, dtype=str), display)
        
    def __init__(self, array, display = None):
        self.array = array
        self.display = display(self) if display else SimpleDisplay(self)
        self.tickingList = []
        self.memory = {}
        a = Automaton(self)

    def cell(self, pos):
        return self.array[pos[0], pos[1]]

    def tick(self):
        if not len(self.tickingList):
            return False
        for a in self.tickingList:
            try:
                a.step()
            except Exception as e:
                self.error(e, a)
        self.display.blit()
        return True

    def runUntilDone(self):
        while self.tick():
            pass

    def error(self, message, automaton = None):
        self.display.error(message, automaton.position)
        exit(1)

class Automaton:
    def __init__(self, world, position = [0, 0], direction = Direction.RIGHT):
        self.state = State.NORMAL
        self.literalType = None
        self.world = world
        self.position = position
        self.direction = direction

        self.children = []
        self.retval = ""
        self.retcache = ""
        self.ignoreNext = False

        self.world.tickingList.append(self)
        self.world.display.onNewAutomaton(self)

    def step(self):
        if self.state == State.NORMAL or self.state == State.READING:
            try:
                cell = self.world.cell(self.position)
            except IndexError:
                return self.halt()
            else:
                h = reg.exec(cell, self)
                if h != None:
                    self.retval = h
                if self.state != State.HALTED and self.state != State.WAITING:
                    self.move(self.direction)
        elif self.state == State.WAITING:
            if all([c.state == State.HALTED for c in self.children]):
                try:
                    cell = self.world.cell(self.position)
                except IndexError:
                    return self.halt()
                else:
                    h = reg.exec(cell, self)
                    if h != None:
                        self.retval = h
                    if self.state != State.HALTED:
                        self.move(self.direction)

    def move(self, direction = None):
        if not direction:
            direction = self.direction
        dm = DIRMAP[direction]
        self.position[dm[0]] += dm[1]
        self.world.display.onAutomatonMove(self, direction)
        if self.position[0] < 0 or self.position[0] > self.world.array.shape[0] or self.position[1] < 0 or self.position[1] > self.world.array.shape[1]:
            self.halt()
    def turn(self, rotation):
        self.direction = Direction((self.direction.value + rotation.value) % 4)

    def retvals(self):
        r = [c.retval for c in self.children]
        self.children = []
        return r

    def halt(self):
        self.world.tickingList.remove(self)
        self.state = State.HALTED
        self.world.display.onAutomatonHalted(self)

    def spawnChild(self):
        child = Automaton(self.world, deepcopy(self.position), deepcopy(self.direction))
        self.children.append(child)
        self.world.display.onAutomatonChild(self, child)
        return child


def run(program, display):
    world = World.fromData(program, display)
    world.runUntilDone()
    
def main():
    import argparse

    class DisplayAction(argparse.Action):
        def __init__(self, option_strings, dest):
            super(DisplayAction, self).__init__(
                option_strings=option_strings,
                dest=dest,
                const="list",
                nargs="?",
                default="simple",
                help="The display to use, leave blank for a list of displays"
            )
        def __call__(self, parser, namespace, values, option_string=None):
            if values == "list":
                print("Available displays:")
                for d in DISPLAYS:
                    print(d, "-", DISPLAYS[d]["desc"])
                parser.exit()
            else:
                setattr(namespace, self.dest, values)
    
    parser = argparse.ArgumentParser(description = "Run makina programs")
    parser.add_argument('file', metavar='file', help='A path to the file to run')
    parser.add_argument('-d', '--display', action=DisplayAction)
    args = parser.parse_args()
    display = DISPLAYS[args.display]["display"]
    run(open(args.file, "r").read(), display = display)