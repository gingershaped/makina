from makina.constants import *
from functools import partial
from time import sleep

LITERALS = {
    "t": [str, ConsecutiveBehavior.CONCAT],
    "n": [int, ConsecutiveBehavior.OVERWRITE]
}

HALT = [" ", ""]

class InstructionRegistry:
    def __init__(self):
        self.reg = {}
        self._obeyWhenReading = []
        for l in LITERALS:
            self.reg[l] = partial(self.startLiteral, l, *LITERALS[l])
    def register(self, name, func):
        if name in self.reg:
            raise Exception("There is already an instruction named " + name + "!")
        self.reg[name] = func
    def exec(self, name, automaton):
        if automaton.state == State.READING and name != ";":
            if name in HALT:
                automaton.retcache = None
                automaton.halt()
                return
            if name in self.reg:
                 if self.reg[name] in self._obeyWhenReading and not automaton.ignoreNext:
                     return self.reg[name](automaton)
            if automaton.ignoreNext:
                automaton.ignoreNext = False
            automaton.retcache += name
        else:
            try:
                return self.reg[name](automaton)
            except KeyError:
                if name in HALT:
                    return automaton.halt()
                else:
                    automaton.world.error("Invalid symbol: " + name, automaton)
    def startLiteral(self, l, type, consecutiveBehavior, automaton):
        automaton.state = State.READING
        automaton.literalType = [type, consecutiveBehavior]

    def processParamInstr(self, automaton, instruction, params, directionOverrides):
        assert params < 3, "Cannot have > 2 params!"
        if automaton.state == State.WAITING:
            automaton.state = State.NORMAL
            return instruction(automaton, *automaton.retvals())
        elif automaton.state == State.NORMAL:
            automaton.state = State.WAITING
            for x in ([Rotation.LEFT, Rotation.RIGHT] if not directionOverrides else directionOverrides)[:params]:
                c = automaton.spawnChild()
                c.turn(x)
                c.move()
                
    def i(self, name, params = None, directionOverrides = None):
        if not params:
            return lambda f: self.register(name, f)
        return lambda f: self.register(name, lambda a: self.processParamInstr(a, f, params, directionOverrides))

    def obeyWhenReading(self):
        def _a(f):
            self._obeyWhenReading.append(f)
            return f
        return _a

        
        
reg = InstructionRegistry()

@reg.i(";")
def semicolon(automaton):
    if automaton.state == State.READING:
        automaton.state = State.NORMAL
        if automaton.literalType[1] == ConsecutiveBehavior.CONCAT:
            automaton.retval += automaton.literalType[0](automaton.retcache)
        elif automaton.literalType[1] == ConsecutiveBehavior.OVERWRITE:
            automaton.retval = automaton.literalType[0](automaton.retcache)
        automaton.literalType = None
        automaton.retcache = ""
@reg.i(":")
@reg.obeyWhenReading()
def colon(automaton):
    if automaton.state == State.READING:
        automaton.ignoreNext = True

@reg.i("^")
@reg.obeyWhenReading()
def up(automaton):
    automaton.direction = Direction.UP
@reg.i(">")
@reg.obeyWhenReading()
def right(automaton):
    automaton.direction = Direction.RIGHT
@reg.i("v")
@reg.obeyWhenReading()
def down(automaton):
    automaton.direction = Direction.DOWN
@reg.i("<")
@reg.obeyWhenReading()
def left(automaton):
    automaton.direction = Direction.LEFT
@reg.i("O")
@reg.obeyWhenReading()
def crossroads(automaton):
    pass
@reg.i("H")
@reg.obeyWhenReading()
def hblock(automaton):
    if automaton.direction in [Direction.LEFT, Direction.RIGHT]:
        automaton.halt()
@reg.i("I")
@reg.obeyWhenReading()
def iblock(automaton):
    if automaton.direction in [Direction.UP, Direction.DOWN]:
        automaton.halt()

@reg.i("P", 1)
def print_(automaton, text):
    automaton.world.display.log(text)
@reg.i("p", 1)
def printNnl(automaton, text):
    automaton.world.display.log(text, end = "")
@reg.i("r")
def printReturn(automaton):
    automaton.world.display.log(automaton.retval)
@reg.i("i")
def input_(automaton):
    return input("Input > ")
@reg.i("E")
def numInput(automaton):
  return int(input("Input >"))

@reg.i("T", 2)
def index(automaton, thing, index):
    return thing[index]

@reg.i("+", 2)
def add(automaton, n1, n2):
    return n1 + n2
@reg.i("*", 2)
def multiply(automaton, n1, n2):
    return n1 * n2
@reg.i("-", 2)
def subtract(automaton, n1, n2):
    return n1 - n2
@reg.i("/", 2)
def floordiv(automaton, n1, n2):
    return n1 // n2
@reg.i("%", 2)
def modulo(automaton, n1, n2):
    return n1 % n2
@reg.i("u", 1)
def increment(automaton, cell):
  try:
    automaton.world.memory[cell] += 1
  except KeyError:
    automaton.world.memory[cell] = 1
@reg.i("d", 1)
def decrement(automaton, cell):
  automaton.world.memory[cell] -= 1

@reg.i("m", 1)
def castToInt(automaton, thing):
    return int(thing)
@reg.i("s", 1)
def castToStr(automaton, thing):
    return str(thing)
@reg.i("N")
def castToIntInPlace(automaton):
    automaton.retval = int(automaton.retval)
@reg.i("S")
def castToStrInPlace(automaton):
    automaton.retval = str(automaton.retval)

@reg.i("L", 1)
def length(automaton, thing):
    return len(thing)

@reg.i("l", 2)
def lessThan(automaton, n2, n1):
    return n1 < n2
@reg.i("g", 2)
def greaterThan(automaton, n2, n1):
    return n1 > n2
@reg.i("e", 2)
def lessThanOrEqualTo(automaton, n2, n1):
    return n1 <= n2
@reg.i("o", 2)
def greaterThanOrEqualTo(automaton, n2, n1):
    return n1 >= n2

@reg.i("?", 1, [Rotation.STRAIGHT])
def if_(automaton, condition):
    if condition:
        automaton.direction = Direction((automaton.direction.value - 1) % 4)
    else:
        automaton.direction = Direction((automaton.direction.value + 1) % 4)

@reg.i("J")
@reg.obeyWhenReading()
def jump(automaton):
    automaton.move(automaton.direction)
@reg.i("U")
@reg.obeyWhenReading()
def uturn(automaton):
    automaton.turn(Rotation.UTURN)
    automaton.move()

@reg.i("w", 2)
def write(automaton, data, cell):
    automaton.world.memory[cell] = data
@reg.i("C", 1)
def read(automaton, cell):
    if cell not in automaton.world.memory:
        return 0
    return automaton.world.memory[cell]

@reg.i("x")
def memdump(automaton):
    automaton.world.display.log(automaton.world.memory)
