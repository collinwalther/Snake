import curses
import enum
import random
import threading
import math
import time


class Direction(enum.Enum):
    UP = curses.KEY_UP
    RIGHT = curses.KEY_RIGHT
    DOWN = curses.KEY_DOWN
    LEFT = curses.KEY_LEFT

    @staticmethod
    def areOpposite(cursesDirection1, cursesDirection2):
        try:
            d1, d2 = Direction(cursesDirection1), Direction(cursesDirection2)
        except ValueError:
            return False
        if d1 == Direction.UP and d2 == Direction.DOWN:
            return True
        elif d1 == Direction.RIGHT and d2 == Direction.LEFT:
            return True
        elif d1 == Direction.DOWN and d2 == Direction.UP:
            return True
        elif d1 == Direction.LEFT and d2 == Direction.RIGHT:
            return True
        return False

    @staticmethod
    def isDirection(cursesDirection):
        try:
            d = Direction(cursesDirection)
        except ValueError:
            return False
        return d == Direction.UP \
                or d == Direction.RIGHT \
                or d == Direction.DOWN \
                or d == Direction.LEFT


class Snake:
    def __init__(self, window, secondsPerStep=.25, startLength=3):
        self.secondsPerStep = secondsPerStep
        self.scr = window
        self.direction = Direction.RIGHT
        self.directionChanged = False
        self.score = 0
        self.startLength = startLength
        self.initBoard()
        self.startDirectionListener()

    def startDirectionListener(self):
        t = threading.Thread(target=self.directionListener)
        t.setDaemon(True)
        t.start()

    def directionListener(self):
        while True:
            direction = self.scr.getch()
            if Direction.isDirection(direction) \
                    and self.direction != direction \
                    and not Direction.areOpposite(self.direction, direction):
                self.directionChanged = True
                self.direction = Direction(direction)

    def initBoard(self):
        # Configure curses
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.scr.box()
        self.scr.keypad(True)

        # Mark the initial head and tail of the snake
        self.vertices = [[1, 1], [1 + self.startLength, 1]]

        # Generate the first apple
        self.generateApple()

    def printBoard(self):
        self.scr.clear()
        for i in range(len(self.vertices) - 1):
            v1 = self.vertices[i]
            v2 = self.vertices[i + 1]

            # If these are horizontal vertices, draw a horizontal line.
            if self.horizontallyAligned(v1, v2):
                diff = v2[0] - v1[0]
                if diff > 0:
                    self.scr.hline(v1[1], v1[0], 'O', diff)
                else:
                    self.scr.hline(v1[1], v1[0] + diff + 1, 'O', abs(diff))

            # If these are vertical vertices, draw a vertical line.
            elif self.verticallyAligned(v1, v2):
                diff = v2[1] - v1[1]
                if diff > 0:
                    self.scr.vline(v1[1], v1[0], 'O', diff)
                else:
                    self.scr.vline(v1[1] + diff + 1, v1[0], 'O', abs(diff))

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
        self.apple = [random.randint(1, curses.COLS - 2),
                      random.randint(1, curses.LINES - 2)]

    def step(self):
        # Check to see if the snake eats the apple this turn.  This affects
        # whether the snake grows in size or not.
        increase = False
        if self.snakeOnApple():
            increase = True
            self.consumeApple()
            self.generateApple()
        
        # Move the snake.
        self.moveSnake(increase)

        # If the game is lost, handle that.
        if self.isLost():
            self.handleLoss()
            
    def snakeOnApple(self):
        if self.vertices[-1] == self.apple:
            return True
        return False

    def consumeApple(self):
        self.score += 1

    def moveSnake(self, increase=False):
        # If the tail of the snake is only one spot away from the first bend,
        # then just remove the tail vertex.
        if increase == False:
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
            self.vertices.append([v[0], v[1]])

        # Advance the head vertex by one space.
        v = self.vertices[-1]
        if self.direction == Direction.UP:
            self.vertices[-1] = [v[0], v[1] - 1]
        elif self.direction == Direction.RIGHT:
            self.vertices[-1] = [v[0] + 1, v[1]]
        elif self.direction == Direction.DOWN:
            self.vertices[-1] = [v[0], v[1] + 1]
        elif self.direction == Direction.LEFT:
            self.vertices[-1] = [v[0] - 1, v[1]]

    def isLost(self):
        # Check if the snake is out of bounds.
        for v in self.vertices:
            if v[0] > curses.COLS - 2 \
                    or v[0] < 1 \
                    or v[1] > curses.LINES - 2 \
                    or v[1] < 1:
                return True

        # Check if the head has intersected the body.
        #head = self.vertices[-1]
        #for i in range(len(self.vertices) - 1):
        #    v1, v2 = self.vertices[i], self.vertices[i + 1]
        #    if self.horizontallyAligned(v1, v2) and self.horizontallyAligned(head, v1):
        #        diff = v2[0] - v1[0]
        #        if diff > 0:
        #            if v1[0] <= head[0] <= v2[0]:
        #                return True
        #        else:
        #            if v2[0] <= head[0] <= v1[0]:
        #                return True
        #    elif self.verticallyAligned(v1, v2) and self.verticallyAligned(head, v1):
        #        diff = v2[1] - v1[1]
        #        if diff > 0:
        #            if v1[1] <= head[1] <= v2[1]:
        #                return True
        #        else:
        #            if v2[1] <= head[1] <= v1[1]:
        #                return True
        return False

    def handleLoss(self):
        self.scr.clear()
        loseMessage = "You lose :("
        self.scr.addstr(curses.LINES // 2, (curses.COLS - len(loseMessage)) // 2, loseMessage)
        scoreMessage = "Score: {}".format(self.score)
        self.scr.addstr(curses.LINES // 2 + 1, (curses.COLS - len(scoreMessage)) // 2, scoreMessage)
        quitMessage = "Press any key to quit."
        self.scr.addstr(curses.LINES // 2 + 2, (curses.COLS - len(quitMessage)) // 2, quitMessage)
        self.scr.box() 
        self.scr.refresh()
        self.scr.getch()
        exit(0)
        return

    def play(self):
        while not self.isLost():
            time.sleep(self.secondsPerStep)
            self.step()
            self.printBoard()


def main(stdscr):
    s = Snake(window=stdscr, secondsPerStep=.05, startLength=10)
    s.play()


if __name__ == "__main__":
    curses.wrapper(main)
