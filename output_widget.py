from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import Signal, Qt
import re


class OutputWidget(QTextEdit):
    """Виджет для отображения результатов работы языкового процессора"""
    
    error_clicked = Signal(int)  # номер строки
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Запрещаем редактирование
        self.setReadOnly(True)
        
        # Устанавливаем моноширинный шрифт как в терминале
        font = QFont("Courier New", 10)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Устанавливаем цвет фона как на скриншоте (белый)
        self.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #cccccc;
            }
        """)
        
        # Включаем перенос строк
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)  # Без переноса, как на скриншоте
    
    def append_message(self, message):
        """Добавляет сообщение в область вывода"""
        self.append(message)
    
    def clear_output(self):
        """Очищает область вывода"""
        self.clear()
    
    def mousePressEvent(self, event):
        """Обрабатывает клики мышью для перехода к строке"""
        if event.button() == Qt.MouseButton.LeftButton:
            cursor = self.cursorForPosition(event.pos())
            line_number = cursor.blockNumber() + 1
            
            # Получаем текст строки
            block_text = cursor.block().text()
            
            # Ищем номер строки в начале сообщения (как на скриншоте: "1", "2", "3", "4")
            match = re.match(r'^(\d+)', block_text.strip())
            if match:
                error_line = int(match.group(1))
                self.error_clicked.emit(error_line)
            else:
                # Если не нашли номер в начале, пробуем найти в любом месте
                match = re.search(r'line (\d+)', block_text, re.IGNORECASE)
                if match:
                    error_line = int(match.group(1))
                    self.error_clicked.emit(error_line)
        
        super().mousePressEvent(event)