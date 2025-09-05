from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QLabel


class ElidedLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.full_text = text
        self.setWordWrap(False)  # don’t wrap
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def setText(self, text: str):
        self.full_text = text
        super().setText(text)

    def resizeEvent(self, event):
        """Recalculate ellipsis text when resized"""
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self.full_text, Qt.ElideRight, self.width())
        super().setText(elided)
        super().resizeEvent(event)
