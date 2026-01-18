from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPen


class Zbiornik:
    def __init__(self, x, y, width=100, height=140, nazwa="", grzalka=None):
        self.temperatura = 20.0
        self.komunikat_wyslany = False
        self.grzalka = grzalka
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.nazwa = nazwa
        self.pojemnosc = 100.0
        self.aktualna_ilosc = 0.0
        self.poziom = 0.0  # Wartość 0.0 - 1.0

    def logika_termiczna(self):
        if self.grzalka:
            self.temperatura = self.grzalka.aktualizuj_temp(self.temperatura, self.aktualna_ilosc)
            if self.grzalka:
                # Aktualizacja temperatury
                self.temperatura = self.grzalka.aktualizuj_temp(self.temperatura, self.aktualna_ilosc)

                # Sprawdzanie czy osiągnięto 80 stopni
                if self.temperatura >= 100.0 and not self.komunikat_wyslany:
                    self.pokaz_alarm_temperatury()
                    self.komunikat_wyslany = True  # Oznaczamy, że już raz pokazaliśmy komunikat

                # Resetowanie flagi, jeśli woda ostygnie (np. poniżej 75 stopni)
                # Dzięki temu komunikat pojawi się ponownie przy kolejnym nagrzaniu
                if self.temperatura < 85.0:
                    self.komunikat_wyslany = False

    def pokaz_alarm_temperatury(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Alarm Temperatury")
        msg.setText(f"Uwaga! Woda w zbiorniku osiągnęła 100°C")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def draw(self, painter):
        # 1. Kolor cieczy zależny od temperatury
        if self.poziom > 0:
            h_cieczy = self.height * self.poziom
            y_start = self.y + self.height - h_cieczy

            # od niebieskiego (20°C) do czerwonego (100°C)
            ratio = min(1.0, (self.temperatura - 20) / 60)
            r = int(0 + (255 * ratio))
            b = int(255 - (200 * ratio))
            painter.setBrush(QColor(r, 100, b, 200))
            painter.setPen(Qt.NoPen)
            painter.drawRect(int(self.x + 3), int(y_start), int(self.width - 6), int(h_cieczy))

    def dodaj_ciecz(self, ilosc):
        wolne = self.pojemnosc - self.aktualna_ilosc
        dodano = min(ilosc, wolne)
        self.aktualna_ilosc += dodano
        self.aktualizuj_poziom()
        return dodano

    def usun_ciecz(self, ilosc):
        usunieto = min(ilosc, self.aktualna_ilosc)
        self.aktualna_ilosc -= usunieto
        self.aktualizuj_poziom()
        return usunieto

    def aktualizuj_poziom(self):
        self.poziom = self.aktualna_ilosc / self.pojemnosc

    def czy_pusty(self):
        return self.aktualna_ilosc <= 0.1

    def czy_pelny(self):
        return self.aktualna_ilosc >= self.pojemnosc

    # Punkty zaczepienia dla rur
    def punkt_gora_srodek(self):
        return (self.x + self.width / 2, self.y)

    def punkt_dol_srodek(self):
        return (self.x + self.width / 2, self.y + self.height)

    def punkt_lewy_srodek(self):
        return (self.x ,self.y + self.height / 2)

    def draw(self, painter):
        # 1. Rysowanie cieczy
        if self.poziom > 0:
            h_cieczy = self.height * self.poziom
            y_start = self.y + self.height - h_cieczy

            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 120, 255, 200))
            # Korekta wymiarów, aby ciecz mieściła się w obrysie (+3, -6)
            painter.drawRect(int(self.x + 3), int(y_start), int(self.width - 6), int(h_cieczy))

        # 2. Rysowanie obrysu
        pen = QPen(Qt.white, 4)
        pen.setJoinStyle(Qt.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))

        # 3. Podpis
        painter.setPen(Qt.white)
        painter.drawText(int(self.x), int(self.y - 10), self.nazwa)

        if self.grzalka:
            self.grzalka.draw(painter, self.x, self.y)
            painter.setPen(Qt.white)
            painter.drawText(int(self.x), int(self.y + self.height + 20), f"{self.temperatura:.1f}°C")

