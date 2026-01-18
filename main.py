import sys
from PyQt5.QtWidgets import QApplication
from symulacja import SymulacjaKaskady


if __name__ == '__main__':
    app = QApplication(sys.argv)
    okno = SymulacjaKaskady()
    okno.show()
    sys.exit(app.exec())