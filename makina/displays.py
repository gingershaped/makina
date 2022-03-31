from time import sleep
from sys import stderr

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
        print(text, file=stderr)
        if pos:
            print("at position:", pos, file=stderr)

class SimpleDisplay(Display):
    def log(self, text):
        print(text)

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