import sys
import random
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QLabel, QMessageBox
from PyQt5.QtGui import QPainter, QPen, QBrush
from PyQt5.QtCore import Qt, QPoint, QTimer


class SnakeBody(object):
    def __init__(self, x, y):
        self.head = Node(x, y)
        self.tail = self.head
        self.step = 10
        self.length = 1
        self.speed = 3
        self.rate = 10
        self.status = "play"

    def add(self, x, y):
        # Создаем узел
        # Предыдущий узел для нового узла устанавливаем текущий узел хвоста
        # Следующитй узел для текущего узла хвоста устанавливаем новый узел
        # Устанавливаем узлом хвоста новый узел
        node = Node(x, y)
        node.prev = self.tail
        self.tail.next = node
        self.tail = node

    def move(self, x, y, grow=False):
        # Удаляем узел с хвоста, если змейка не растет
        # Добавляем узел в голову с новыми координатами
        if not grow and self.length > 2:
            self.tail = self.tail.prev
            self.tail.next = None
        node = Node(x, y)
        node.next = self.head
        self.head.prev = node
        self.head = node
        if grow or self.length < 3:
            self.length += 1
            if self.length % self.rate == 0:
                self.speed += 1

    def up(self, grow=False):
        x = self.head.x
        y = self.head.y
        self.move(x, y - self.step, grow)

    def down(self, grow=False):
        x = self.head.x
        y = self.head.y
        self.move(x, y + self.step, grow)

    def left(self, grow=False):
        x = self.head.x
        y = self.head.y
        self.move(x - self.step, y, grow)

    def right(self, grow=False):
        x = self.head.x
        y = self.head.y
        self.move(x + self.step, y, grow)


class Node(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.next = None
        self.prev = None

    def __str__(self):
        return "%d, %d" % (self.x, self.y)


class Meal(object):
    def __init__(self, x1, x2, y1, y2, size):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.size = size
        self.x = None
        self.y = None

    def seed(self):
        self.x = random.randint(self.x1, self.x2)
        self.y = random.randint(self.y1, self.y2)
        self.x -= self.x % self.size
        self.y -= self.y % self.size


class SnakeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.snakeSize = 10
        self.fieldSize = 50
        self.statusWidth = 100
        self.game = Game(self.snakeSize, self.fieldSize, self.statusWidth)
        self.initUI()

    def initUI(self):
        QMainWindow.__init__(self)
        self.statusBar()
        self.setMouseTracking(True)

        self.statusBar().showMessage('Ready')
        self.setCentralWidget(self.game)

        width = self.statusWidth+(self.fieldSize+4)*self.snakeSize
        height = self.game.height()+self.snakeSize*4
        self.setFixedSize(width, height)
        self.setWindowTitle('Snake')
        self.show()


class Game(QWidget):
    def __init__(self, snakeSize, fieldSize, statusWidth):
        super(Game, self).__init__()
        self.statusWidth = statusWidth
        self.snakeSize = snakeSize
        self.fieldSize = fieldSize
        self.gameWidth = snakeSize*(fieldSize+5)+statusWidth
        self.gameHeight = snakeSize*(fieldSize+5)
        self.status = Status(self.statusWidth)
        self.snake = Snake(self.snakeSize, self.fieldSize, self.status)
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: rgb(255,255,255); margin:5px; border:1px solid rgb(0, 0, 0); ")
        self.setFixedSize(self.gameWidth, self.gameHeight)
        hbox = QHBoxLayout()
        hbox.addWidget(self.snake)
        hbox.addWidget(self.status)
        self.setLayout(hbox)
        self.show()


class Status(QWidget):
    def __init__(self, size):
        super(Status, self).__init__()
        self.size = size
        self.scoreLabel = QLabel("score")
        self.speedLabel = QLabel("speed")
        self.initUI()

    def initUI(self):
        self.setFixedWidth(self.size)
        self.setStyleSheet("background-color: rgb(255,255,255); margin:5px; border:1px solid rgb(0, 0, 0); ")
        self.setWindowTitle('Status')
        self.setMouseTracking(True)

        box = QVBoxLayout()
        box.addStretch(1)
        box.addWidget(self.scoreLabel)
        box.addWidget(self.speedLabel)

        self.setLayout(box)
        self.show()


class Snake(QWidget):
    def __init__(self, snakeSize, fieldSize, status):
        super(Snake, self).__init__()
        self.direction = 0
        self.status = status
        self.directions = ((-snakeSize, 0), (0, -snakeSize), (snakeSize, 0), (0, snakeSize))
        self.names = ('left', 'up', 'right', 'down')
        self.snakeSize = snakeSize
        self.fieldSize = fieldSize
        self.snakebody = None
        self.min_x = snakeSize*2
        self.max_x = snakeSize*(fieldSize+2)
        self.min_y = snakeSize*2
        self.max_y = snakeSize*(fieldSize+2)
        self.timer = None
        self.pause = False
        self.setFocusPolicy(Qt.StrongFocus)
        self.initGame()
        self.initUI()

    def initGame(self):
        self.meal = Meal(self.min_x, self.max_x, self.min_y, self.max_y, self.snakeSize)
        self.meal.seed()
        self.snakebody = SnakeBody(self.size().width()//2, self.size().height()//2)
        self.timer = QTimer()
        self.timer.setInterval(1000//self.snakebody.speed)
        self.timer.timeout.connect(self.setCoordinates)
        self.timer.start()
        self.direction = 0
        self.pause = False

    def initUI(self):
        self.setStyleSheet("background-color: rgb(255,255,255); margin:5px; border:1px solid rgb(0, 0, 0); ")
        self.setFixedSize((self.fieldSize+5) * self.snakeSize, (self.fieldSize + 5) * self.snakeSize)
        self.setWindowTitle('Snake')
        self.setMouseTracking(True)
        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left and self.direction in (0, 1, 3):
            self.direction = 0
        elif event.key() == Qt.Key_Up and self.direction in (0, 1, 2):
            self.direction = 1
        elif event.key() == Qt.Key_Right and self.direction in (1, 2, 3):
            self.direction = 2
        elif event.key() == Qt.Key_Down and self.direction in (0, 2, 3):
            self.direction = 3
        elif event.key() == Qt.Key_Pause:
            self.pause = not self.pause
            if self.pause:
                self.timer.stop()
            else:
                self.timer.start()
        else:
            super(Snake, self).keyPressEvent(event)

    def gameOver(self):
        self.snakebody.status = "gameover"
        self.timer.stop()

        buttonReply = QMessageBox.question(
            self,
            'Game over',
            "Again?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if buttonReply == QMessageBox.Yes:
            self.initGame()
            self.initUI()
        else:
            sys.exit(0)

    def setCoordinates(self):
        pos_x, pos_y = self.snakebody.head.x, self.snakebody.head.y
        grow = pos_x == self.meal.x and pos_y == self.meal.y

        if pos_x < self.min_x or pos_x > self.max_x or pos_y < self.min_y or pos_y > self.max_y:
            self.gameOver()

        if grow:
            self.meal.seed()
        if self.direction == 0:
            self.snakebody.left(grow)
        if self.direction == 1:
            self.snakebody.up(grow)
        if self.direction == 2:
            self.snakebody.right(grow)
        if self.direction == 3:
            self.snakebody.down(grow)

        self.update()

    def mouseMoveEvent(self, e):
        print(f'point: x={e.x()} y={e.y()}')

    def paintEvent(self, e):
        paint = QPainter(self)
        self.drawBorderAndField(paint)
        self.drawBunny(paint)
        self.drawSnake(paint)
        self.setLabelValues()

    def drawBorderAndField(self, paint):
        paint.setPen(QPen(Qt.darkGreen, self.snakeSize, Qt.SolidLine))
        paint.setBrush(QBrush(Qt.yellow, Qt.DiagCrossPattern))
        paint.drawRect(
            self.snakeSize,
            self.snakeSize,
            self.snakeSize*(self.fieldSize+2),
            self.snakeSize*(self.fieldSize+2)
        )

    def drawBunny(self, paint):
        bunny = QPoint(self.meal.x, self.meal.y)
        paint.setPen(QPen(Qt.blue, self.snakeSize))
        paint.drawPoint(bunny)

    def drawSnake(self, paint):
        paint.setPen(QPen(Qt.red, self.snakeSize, Qt.DotLine))
        paint.setBrush(QBrush(Qt.lightGray, Qt.Dense5Pattern))
        size = self.size()

        head = self.snakebody.head
        while head:
            paint.drawPoint(head.x, head.y)
            head = head.next

        print(f"direction={self.names[self.direction]} point=({self.snakebody.head}) bounds=(0, {size.width()}, 0, {size.height()})")

    def setLabelValues(self):
        self.status.scoreLabel.setText(f"score: {self.snakebody.length}")
        self.status.speedLabel.setText(f"speed: {self.snakebody.speed}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SnakeApp()
    sys.exit(app.exec_())