from PyQt5.QtGui import QColor, QPen, QPainterPath

class Zawor:
    def __init__(self, x_offset=0, y_offset=0):
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.otwarty = True

    def przelacz(self):
        self.otwarty = not self.otwarty

    def draw(self, painter, x, y):
        # Parametry wyglądu
        size = 15  # szerokość/wysokość skrzydełka
        kolor = QColor(46, 204, 113) if self.otwarty else QColor(231, 76, 60)

        painter.setPen(QPen(QColor(0, 0, 0), 2))  # czarna obwódka
        painter.setBrush(kolor)  # wypełnienie środka

        path = QPainterPath()

        # Lewy trójkąt (wierzchołek w x, y)
        path.moveTo(x - size, y - size)
        path.lineTo(x, y)
        path.lineTo(x - size, y + size)
        path.closeSubpath()

        # Prawy trójkąt (wierzchołek w x, y)
        path.moveTo(x + size, y - size)
        path.lineTo(x, y)
        path.lineTo(x + size, y + size)
        path.closeSubpath()

        painter.drawPath(path)
