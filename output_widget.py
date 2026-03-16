from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import Signal, Qt
import re

class OutputWidget(QTextEdit):
    
    error_clicked = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setReadOnly(True)
        
        font = QFont("Courier New", 10)
        font.setFixedPitch(True)
        self.setFont(font)
        
        self.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #cccccc;
            }
        """)
        
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
    
    def append_message(self, message):
        self.append(message)
    
    def clear_output(self):
        self.clear()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            cursor = self.cursorForPosition(event.pos())
            line_number = cursor.blockNumber() + 1
            
            block_text = cursor.block().text()
            
            match = re.match(r'^(\d+)', block_text.strip())
            if match:
                error_line = int(match.group(1))
                self.error_clicked.emit(error_line)
            else:
                match = re.search(r'line (\d+)', block_text, re.IGNORECASE)
                if match:
                    error_line = int(match.group(1))
                    self.error_clicked.emit(error_line)
        
        super().mousePressEvent(event)