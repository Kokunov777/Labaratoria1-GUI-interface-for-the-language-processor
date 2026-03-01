from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import Signal, Qt


class OutputWidget(QTextEdit):
    error_clicked = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
      
        self.setReadOnly(True)
        
       
        font = QFont("Courier New", 10)
        font.setFixedPitch(True)
        self.setFont(font)
        
       
        self.setStyleSheet("background-color: #f5f5f5;")
        
    
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
    def append_message(self, message, message_type="info"):
      
        if message_type == "error":
     
            self.append(f"❌ {message}")
        elif message_type == "success":
            self.append(f"✅ {message}")
        elif message_type == "warning":
            self.append(f"⚠️ {message}")
        else:
            self.append(f"ℹ️ {message}")
    
    def clear_output(self):
        
        self.clear()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            cursor = self.cursorForPosition(event.pos())
            line_number = cursor.blockNumber() + 1
            
            block_text = cursor.block().text()
            
          
            if "Error at line" in block_text or "ошибка в строке" in block_text.lower():
                import re
                match = re.search(r'line (\d+)', block_text, re.IGNORECASE)
                if match:
                    error_line = int(match.group(1))
                    self.error_clicked.emit(error_line)
                else:
                    self.error_clicked.emit(line_number)
        
        super().mousePressEvent(event)