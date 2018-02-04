import curses
import enum
import random
import threading
import math
import time


class Direction(enum.Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class Snake:
    def __init__(self, window, secondsPerStep=.5):
        self.secondsPerStep = secondsPerStep
        self.scr = window
        self.direction = Direction.RIGHT
        self.directionChanged = False
        self.score = 0
        self.initBoard()
        self.startDirectionListener()

    def startDirectionListener(self):
        t = threading.Thread(target=self.directionListener)
        t.setDaemon(True)
        t.start()

    def directionListener(self):
        while True:
            direction = curses.getch()
            if self.direction != direction:
                self.directionChanged = True
            if direction == curses.KEY_UP:
                self.direction = Direction.UP
            elif direction == curses.KEY_RIGHT:
                self.direction = Direction.RIGHT
            elif direction == curses.KEY_DOWN:
                self.direction = Direction.DOWN
            elif direction == curses.KEY_LEFT:
                self.direction = Direction.LEFT

    def initBoard(self):
        # Configure curses
        curses.noecho()
        curses.cbreak()
        self.scr.box()

        # Mark the initial head of the snake
        self.vertices = [[1, 1], [4, 1]]

        # Generate the first apple
        self.generateApple()

    def printBoard(self):
        self.scr.clear()
        for i in range(len(self.vertices) - 1):
            v1 = self.vertices[i]
            v2 = self.vertices[i + 1]

            # If these are horizontal vertices, draw a horizontal line.
            if self.horizontallyAligned(v1, v2):
                self.scr.hline(v1[1], v1[0], '~', v2[0] - v1[0])

            # If these are vertical vertices, draw a vertical line.
            elif self.verticallyAligned(v1, v2):
                self.scr.vline(v1[1], v1[0], '}', v2[1] - v1[1])

        # Draw the apple.
        self.scr.addch(self.apple[1], self.apple[0], 'x')

        # Refresh.
        self.scr.box()
        self.scr.refresh()

    def horizontallyAligned(self, v1, v2):
        return v1[1] == v2[1]

    def verticallyAligned(self, v1, v2):
        return v1[0] == v2[0]

    def adjacent(self, v1, v2):
        return (int(math.fabs(v1[0] - v2[0])) == 1) \
            or (int(math.fabs(v1[1] - v2[1])) == 1)

    def generateApple(self):
        self.apple = [random.randint(1, curses.COLS - 1),
                      random.randint(1, curses.LINES - 1)]

    def step(self):
        # Determine the direction in which to move
        self.moveSnake()

        # If the game is lost, handle that.
        if self.isLost():
            self.handleLoss()

    def moveSnake(self):
        # If the tail of the snake is only one spot away from the first bend,
        # then just remove the tail vertex.
        v1, v2 = self.vertices[0], self.vertices[1]
        if self.adjacent(v1, v2):
            self.vertices.pop(0)

        # Otherwise, advance the tail by one tile.
        else:
            if self.horizontallyAligned(v1, v2):
                if v1[0] < v2[0]:
                    v1[0] += 1
                else:
                    v1[0] -= 1
            elif self.verticallyAligned(v1, v2):
                if v1[1] < v2[1]:
                    v1[1] += 1
                else:
                    v1[1] -= 1

        # Now move the head.
        # If the direction has been changed, add a new vertex to the snake.
        if self.directionChanged:
            self.directionChanged = False
            v = self.vertices[-1]
            if self.direction == Direction.UP:
                newV = [v[0], v[1] + 1]
            elif self.direction == Direction.RIGHT:
                newV = [v[0] + 1, v[1]]
            elif self.direction == Direction.DOWN:
                newV = [v[0], v[1] - 1]
            elif self.direction == Direction.LEFT:
                newV = [v[0] - 1, v[1]]
            self.vertices.append(newV)

        # Advance the head vertex by one space.
        v = self.vertices[-1]
        if self.direction == Direction.UP:
            self.vertices[-1] = [v[0], v[1] + 1]
        elif self.direction == Direction.RIGHT:
            self.vertices[-1] = [v[0] + 1, v[1]]
        elif self.direction == Direction.DOWN:
            self.vertices[-1] = [v[0], v[1] - 1]
        elif self.direction == Direction.LEFT:
            self.vertices[-1] = [v[0] - 1, v[1]]

    def isLost(self):
        # TODO
        return False

    def handleLoss(self):
        # TODO
        return

    def play(self):
        while not self.isLost():
            time.sleep(self.secondsPerStep)
            self.step()
            self.printBoard()


def main(stdscr):
    s = Snake(window=stdscr)
    s.play()


if __name__ == "__main__":
    curses.wrapper(main)
