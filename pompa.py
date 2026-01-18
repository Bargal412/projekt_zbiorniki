from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPen

class Pompa:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rozmiar = 45
        self.wlaczona = False

    def draw(self, painter):
        painter.setPen(QPen(Qt.white, 3))
        painter.setBrush(QColor(80, 80, 80))
        painter.drawEllipse(self.x, self.y, self.rozmiar, self.rozmiar)

        kolor = QColor(0, 200, 0) if self.wlaczona else QColor(120, 120, 120)
        painter.setBrush(kolor)
        painter.drawEllipse(
            self.x + 10,
            self.y + 10,
            self.rozmiar - 20,
            self.rozmiar - 20
        )

        painter.setPen(Qt.white)
        painter.drawText(self.x - 5, self.y - 5, "Pompa")