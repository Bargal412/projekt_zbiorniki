from PyQt5.QtWidgets import QWidget, QPushButton, QLabel , QSlider
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter
from Rura import Rura
from pompa import Pompa
from grzalka import Grzalka
from zbiornik import Zbiornik
from zawor import Zawor

class SymulacjaKaskady(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kaskada: Dol -> Gora")
        self.setFixedSize(900, 600)
        self.setStyleSheet("background-color: #222;")
        self.zawor_z1_z2 = Zawor(x_offset=120, y_offset=60)

        # Konfiguracja Zbiorników (schodkowo)
        # Zbiornik 1 (Górny lewy - źródło)
        self.z1 = Zbiornik(50, 50, nazwa="Zbiornik 1")
        self.z1.aktualna_ilosc = 100.0  # Pełny na start
        self.z1.aktualizuj_poziom()
        # Zbiornik 2 (Środkowy)
        self.z2 = Zbiornik(350, 200, nazwa="Zbiornik 2")
        # Zbiornik 3 (Dolny prawy)
        self.z3 = Zbiornik(650, 350, nazwa="Zbiornik 3", grzalka=Grzalka(15,125))
        # Zbiornik 4 (Górny prawy)
        self.z4 = Zbiornik(550,50, nazwa="Zbiornik 4")

        self.zbiorniki = [self.z1, self.z2, self.z3, self.z4]

        # Rura 1: Z1 (Dół) -> Z2 (Góra)
        p_start = self.z1.punkt_dol_srodek()
        p_koniec = self.z2.punkt_gora_srodek()
        mid_y = (p_start[1] + p_koniec[1]) / 2

        self.rura1 = Rura([
            p_start,
            (p_start[0], mid_y),
            (p_koniec[0], mid_y),
            p_koniec
        ])

        # Rura 2: Z2 (Dół) -> Z3 (Góra)
        p_start2 = self.z2.punkt_dol_srodek()
        p_koniec2 = self.z3.punkt_gora_srodek()
        mid_y2 = (p_start2[1] + p_koniec2[1]) / 2

        self.rura2 = Rura([
            p_start2,
            (p_start2[0], mid_y2),
            (p_koniec2[0], mid_y2),
            p_koniec2
        ])

        #Rura 3: Rura -> Z4 (Środek)
        p_start3 = (
            (p_start[0] + p_koniec[0]) / 2,
            (p_start[1] + p_koniec[1]) / 2
        )
        p_koniec3 = self.z4.punkt_lewy_srodek()

        self.rura3 = Rura([
            p_start3,
            (p_start3[0], p_koniec3[1]),
            p_koniec3
        ])

        self.rury = [self.rura1, self.rura2, self.rura3]

        # Timer i Sterowanie
        self.timer = QTimer()
        self.timer.timeout.connect(self.logika_przeplywu)

        # Zawor przycisk
        self.btn_zawor = QPushButton("Zawór", self)
        self.btn_zawor.setGeometry(150, 290, 80, 30)
        self.btn_zawor.clicked.connect(self.zawor_z1_z2.przelacz)
        self.btn_zawor.setStyleSheet("background-color: #1f77b4; color: #000000;")

        # Przycisk Start/Stop
        self.btn = QPushButton("Start/Stop", self)
        self.btn.setGeometry(65, 500, 100, 30)
        self.btn.setStyleSheet("background-color: #444; color: white;")
        self.btn.clicked.connect(self.przelacz_symulacje)

        self.running = False
        self.speed_base = 0.8
        self.pompa_mnoznik = 1.0
        self.pompa = Pompa(x=160,y=175)

        #Interfejs Sterujący (Dodatkowe przyciski)
        self.setup_manual_controls()
        self.setup_pump_controls()

        #przycisk do grzałki
        self.btn_h = QPushButton("Grzałka Z3", self)
        self.btn_h.setGeometry(150, 330, 80, 30)
        self.btn_h.clicked.connect(self.toggle_heater)
        self.btn_h.setStyleSheet("background-color: #F1C40F; color: white")

    def toggle_heater(self):
        if self.z3.grzalka:
            self.z3.grzalka.wlaczona = not self.z3.grzalka.wlaczona

    def setup_manual_controls(self):
        # Tworzymy przyciski dla każdego zbiornika (Napełnij / Opróżnij)
        # Z1 Controls
        self.create_tank_buttons(self.z1, 250, 500)
        # Z2 Controls
        self.create_tank_buttons(self.z2, 350, 500)
        # Z3 Controls
        self.create_tank_buttons(self.z3, 450, 500)
        # Z4 Controls
        self.create_tank_buttons(self.z4, 550, 500)

    def setup_pump_controls(self):
        # przyciski dla pompy
        lbl = QLabel("Pompa", self)
        lbl.setStyleSheet("color: cyan; font-size: 20px;")
        lbl.move(60, 300)

        btn_on = QPushButton("ON", self)
        btn_on.setGeometry(45, 330, 40, 30)
        btn_on.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; 
                color: white; 
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        btn_on.clicked.connect(lambda: self.wlacz_pompe(True))

        btn_off = QPushButton("OFF", self)
        btn_off.setGeometry(90, 330, 40, 30)
        btn_off.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; 
                color: white; 
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_off.clicked.connect(lambda: self.wlacz_pompe(False))

        self.lbl_speed = QLabel("Prędkość: 1.0x", self)
        self.lbl_speed.setStyleSheet("color: white; font-size: 14px;")
        self.lbl_speed.move(45, 370)

        # ustawienia suwaka
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setGeometry(45, 390, 150, 30)
        self.slider.setMinimum(10)  # 1.0x
        self.slider.setMaximum(50)  # 5.0x
        self.slider.setValue(10)

        self.slider.valueChanged.connect(self.zmien_predkosc_suwakiem)

    def wlacz_pompe(self, stan):
        self.pompa.wlaczona = stan
        self.update()

    def zmien_predkosc_suwakiem(self, wartosc):
        nowy_mnoznik = wartosc / 10.0
        self.pompa_mnoznik = nowy_mnoznik
        self.lbl_speed.setText(f"Prędkość: {nowy_mnoznik:.1f}x")

    def create_tank_buttons(self, zbiornik, x_pos, y_pos):
        lbl = QLabel(zbiornik.nazwa, self)
        lbl.setStyleSheet("color: magenta; font-size: 20px;")
        lbl.move(x_pos, y_pos - 20)


        btn_fill = QPushButton("+", self)
        btn_fill.setGeometry(x_pos, y_pos, 20, 30)
        btn_fill.setStyleSheet("background-color: green; color: black;")
        btn_fill.clicked.connect(lambda: self.reczne_napelnianie(zbiornik))


        btn_empty = QPushButton("-", self)
        btn_empty.setGeometry(x_pos + 45, y_pos, 20, 30)
        btn_empty.setStyleSheet("background-color: red; color: black;")
        btn_empty.clicked.connect(lambda: self.reczne_oproznianie(zbiornik))


    def reczne_napelnianie(self, zbiornik):
        zbiornik.aktualna_ilosc = zbiornik.pojemnosc
        zbiornik.aktualizuj_poziom()
        self.update()

    def reczne_oproznianie(self, zbiornik):
        zbiornik.aktualna_ilosc = 0.0
        zbiornik.aktualizuj_poziom()
        self.update()

    def przelacz_symulacje(self):
        if self.running:
            self.timer.stop()
        else:
            self.timer.start(20)  # 20ms interwał
        self.running = not self.running

    def logika_przeplywu(self):

        if not self.zawor_z1_z2.otwarty:
            self.rura1.ustaw_przeplyw(False)
            self.rura3.ustaw_przeplyw(False)
            z1_zablokowany = True
        else:
            z1_zablokowany = False

        if self.pompa.wlaczona:
            mnoznik = self.pompa_mnoznik
            flow_speed = self.speed_base * mnoznik
        else:
            flow_speed = self.speed_base

        # Flagi dla każdej rury z osobna
        stan_rura1 = False
        stan_rura2 = False
        stan_rura3 = False

        #  Z1 -> Z2
        if not z1_zablokowany and not self.z1.czy_pusty() and not self.z2.czy_pelny():
            ilosc = self.z1.usun_ciecz(flow_speed)
            self.z2.dodaj_ciecz(ilosc)
            stan_rura1 = True

        #  Z1 -> Z3
        elif not self.z1.czy_pusty() and not self.z3.czy_pelny() and not z1_zablokowany:
            ilosc = self.z1.usun_ciecz(flow_speed)
            self.z3.dodaj_ciecz(ilosc)
            stan_rura1 = True

        # Z2 -> Z3
        if not self.z2.czy_pusty() and not self.z3.czy_pelny():
            ilosc = self.z2.usun_ciecz(self.speed_base)
            self.z3.dodaj_ciecz(ilosc)
            stan_rura2 = True

        # Z1 -> Z4
        elif not self.z1.czy_pusty() and self.z2.czy_pelny() and not self.z4.czy_pelny() and self.z1.poziom > self.z4.poziom and not self.pompa.wlaczona and not z1_zablokowany:
            roznica = self.z1.poziom - self.z4.poziom
            if roznica > 0.01:
                ilosc = self.z1.usun_ciecz(flow_speed * 0.5)
                self.z4.dodaj_ciecz(ilosc)
                stan_rura3 = True
            else:
                stan_rura3 = False

        elif not self.z1.czy_pusty() and self.z2.czy_pelny() and not self.z4.czy_pelny() and self.pompa.wlaczona:
            ilosc = self.z1.usun_ciecz(flow_speed * 0.5)
            self.z4.dodaj_ciecz(ilosc)
            stan_rura3 = True


        # Z4 -> Z1
        elif not self.z4.czy_pusty() and self.z2.czy_pelny() and not self.z1.czy_pelny() and self.z4.poziom > self.z1.poziom and self.z4.poziom >= 0.45 and not self.pompa.wlaczona and not z1_zablokowany:
            roznica = self.z4.poziom - self.z1.poziom
            if roznica > 0.01:
                ilosc = self.z4.usun_ciecz(flow_speed)
                self.z1.dodaj_ciecz(ilosc)
                stan_rura3 = True
            else:
                stan_rura3 = False


        # Z4 -> dół
        poziom_wlotu = 0.45
        if self.z4.poziom >= poziom_wlotu and not z1_zablokowany:

            if not self.z2.czy_pelny():
                ilosc = self.z4.usun_ciecz(self.speed_base)
                self.z2.dodaj_ciecz(ilosc)
                stan_rura3 = True

            elif not self.z3.czy_pelny():
                ilosc = self.z4.usun_ciecz(self.speed_base)
                self.z3.dodaj_ciecz(ilosc)
                stan_rura3 = True

        # Przypisanie stanów do konkretnych rur
        self.rura1.ustaw_przeplyw(stan_rura1)
        self.rura2.ustaw_przeplyw(stan_rura2)
        self.rura3.ustaw_przeplyw(stan_rura3)

        # Temperatura w zbiorniku inicjacja
        for z in self.zbiorniki:
            z.logika_termiczna()


        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        for r in self.rury:
            r.draw(p)

        for z in self.zbiorniki:
            z.draw(p)

        self.pompa.draw(p)
        self.zawor_z1_z2.draw(p,250, 195)
