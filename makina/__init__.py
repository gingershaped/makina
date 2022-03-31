import numpy as np
from makina.constants import *
from makina.instructions import reg
from makina.displays import SimpleDisplay
from copy import deepcopy
from time import sleep

DIRMAP = {Direction.UP: (0, -1), Direction.DOWN: (0, 1), Direction.RIGHT: (1, 1), Direction.LEFT: (1, -1)}

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

    def spawnChild(self):
        child = Automaton(self.world, deepcopy(self.position), deepcopy(self.direction))
        self.children.append(child)
        return child
        

def run(program, display):
    world = World.fromData(program, display)
    world.runUntilDone()