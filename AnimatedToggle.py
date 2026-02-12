from PySide6.QtCore import Qt, QPropertyAnimation, Property, QEasingCurve, Signal
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor


class AnimatedToggle(QWidget):
    toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 26)

        self._checked = False
        self._offset = 2

        self.anim = QPropertyAnimation(self, b"offset", self)
        self.anim.setDuration(180)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

    def mousePressEvent(self, event):
        self.on_click()

    def on_click(self):
        self._checked = not self._checked

        self.anim.stop()
        self.anim.setStartValue(self._offset)
        self.anim.setEndValue(26 if self._checked else 2)
        self.anim.start()

        self.toggled.emit(self._checked)
        self.update()
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # background
        bg = QColor("#4CAF50") if self._checked else QColor("#777")
        p.setBrush(bg)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(0, 0, self.width(), self.height(), 13, 13)

        # knob
        p.setBrush(Qt.white)
        p.drawEllipse(self._offset, 2, 22, 22)

    def getOffset(self):
        return self._offset

    def setOffset(self, value):
        self._offset = value
        self.update()

    offset = Property(float, getOffset, setOffset)

    def isChecked(self):
        return self._checked
