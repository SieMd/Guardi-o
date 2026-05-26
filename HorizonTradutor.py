import sys
import mss
import numpy as np
import cv2
import easyocr

from deep_translator import GoogleTranslator
from PyQt5.QtWidgets import QApplication, QTextEdit, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer

reader = easyocr.Reader(['en'])
translator = GoogleTranslator(source="auto", target="pt")

monitor = {
    "top": 780,
    "left": 0,
    "width": 620,
    "height": 300
}

mensagens_vistas = set()


class ChatOverlay(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )

        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setGeometry(0, 600, 620, 200)

        layout = QVBoxLayout()

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)

        self.chat.setStyleSheet("""
        QTextEdit{
            background-color: rgba(0,0,0,120);
            color: white;
            font-size: 14px;
            padding:5px;
        }
        """)

        layout.addWidget(self.chat)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.capture_screen)
        self.timer.start(1500)

    def capture_screen(self):

        with mss.mss() as sct:

            screenshot = sct.grab(monitor)
            img = np.array(screenshot)

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            result = reader.readtext(gray)

            linhas = []

            for (bbox, text, prob) in result:

                if prob > 0.55:
                    linhas.append(text)

            if len(linhas) == 0:
                return

            texto = " ".join(linhas)

            if texto in mensagens_vistas:
                return

            mensagens_vistas.add(texto)

            try:

                traducao = translator.translate(texto)

                self.chat.append(f"{texto}")
                self.chat.append(f"→ {traducao}")
                self.chat.append("")

                self.chat.verticalScrollBar().setValue(
                    self.chat.verticalScrollBar().maximum()
                )

            except:
                pass


app = QApplication(sys.argv)

overlay = ChatOverlay()
overlay.show()

sys.exit(app.exec_())
