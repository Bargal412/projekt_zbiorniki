from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPen, QPainterPath

class Grzalka:
    def __init__(self, x_offset, y_offset):
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.wlaczona = False
        self.moc = 0.20  # Jak szybko rośnie temperatura

    def aktualizuj_temp(self, obecna_temp, ilosc_wody):
        # Grzejemy tylko gdy jest woda i grzałka ON
        if self.wlaczona and ilosc_wody > 5.0:
            if obecna_temp < 100.0:
                return obecna_temp + self.moc
        elif ilosc_wody < 5.0:
            obecna_temp = 20.0
        elif obecna_temp > 20.0:
            return obecna_temp - 0.05  # chłodzenie
        return obecna_temp

    def draw(self, painter, x_zbiornika, y_zbiornika):
        # Rysowanie spirali grzałki
        kolor = QColor(255, 50, 50) if self.wlaczona else QColor(100, 100, 100)
        painter.setPen(QPen(kolor, 3, Qt.SolidLine, Qt.RoundCap))

        start_x = x_zbiornika + self.x_offset
        start_y = y_zbiornika + self.y_offset

        # kształt grzałki
        path = QPainterPath()
        path.moveTo(start_x, start_y)
        for i in range(4):
            path.lineTo(start_x + 10 + i * 15, start_y - 10)
            path.lineTo(start_x + 17 + i * 15, start_y)
        painter.drawPath(path)