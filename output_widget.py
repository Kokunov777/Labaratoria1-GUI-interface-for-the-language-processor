from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QFont, QTextCursor, QColor
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
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 2px;
            }
        """)
        
    
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
    def append_message(self, message, message_type="info"):
        """Добавляет сообщение в область вывода с цветовым выделением"""
        if message_type == "error":
   
            self.setTextColor(QColor(255, 0, 0))
            self.append(f"❌ {message}")
        elif message_type == "success":

            self.setTextColor(QColor(0, 128, 0))
            self.append(f"✅ {message}")
        elif message_type == "warning":
   
            self.setTextColor(QColor(255, 165, 0))
            self.append(f"⚠️ {message}")
        else:
 
            self.setTextColor(QColor(0, 0, 0))
            self.append(f"ℹ️ {message}")
        

        self.setTextColor(QColor(0, 0, 0))
    
    def append(self, text):

        super().append(text)

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
    
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
                return
            

            match = re.search(r'[Сс]трок[ае]\s+(\d+)', block_text)
            if match:
                error_line = int(match.group(1))
                self.error_clicked.emit(error_line)
                return

            match = re.search(r'[Ll]ine\s+(\d+)', block_text)
            if match:
                error_line = int(match.group(1))
                self.error_clicked.emit(error_line)
                return
            
 
            match = re.search(r'\b(\d+)\b', block_text)
            if match:
                error_line = int(match.group(1))
                
                if error_line < 1000:  # разумный номер строки
                    self.error_clicked.emit(error_line)
                    return
        super().mousePressEvent(event)
    
    def highlight_error_line(self, line_number):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        cursor.movePosition(QTextCursor.MoveOperation.Down, n=line_number-1)
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        self.setTextCursor(cursor)