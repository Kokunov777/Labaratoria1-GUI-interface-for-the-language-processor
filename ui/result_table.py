from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Signal, Qt

class ResultTable(QTableWidget):
    
    error_clicked = Signal(int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels([
            "Условный код",
            "Тип лексемы",
            "Лексема",
            "Строка",
            "Позиция"
        ])
        
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.verticalHeader().setVisible(False)
        
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(False)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.setFont(QFont("Courier New", 9))
    
    def display_tokens(self, tokens, errors):
        self.setRowCount(0)
        
        for token in tokens:
            self._add_token_row(token)
        
        for error in errors:
            self._add_error_row(error)
    
    def _add_token_row(self, token):
        row = self.rowCount()
        self.insertRow(row)
        
        code_item = QTableWidgetItem(str(token.type))
        code_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 0, code_item)
        
        type_item = QTableWidgetItem(token.get_type_name())
        self.setItem(row, 1, type_item)
        
        value_item = QTableWidgetItem(token.value)
        self.setItem(row, 2, value_item)
        
        line_item = QTableWidgetItem(str(token.line))
        line_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 3, line_item)
        
        pos_item = QTableWidgetItem(f"{token.start_pos}-{token.end_pos}")
        pos_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 4, pos_item)
    
    def _add_error_row(self, error):
        row = self.rowCount()
        self.insertRow(row)
        
        code_item = QTableWidgetItem("ERR")
        code_item.setForeground(QColor(255, 0, 0))
        code_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 0, code_item)
        
        type_item = QTableWidgetItem("Ошибка")
        type_item.setForeground(QColor(255, 0, 0))
        self.setItem(row, 1, type_item)
        
        value_item = QTableWidgetItem(error.get('message', 'Неизвестная ошибка'))
        value_item.setForeground(QColor(255, 0, 0))
        self.setItem(row, 2, value_item)
        
        line_item = QTableWidgetItem(str(error.get('line', '?')))
        line_item.setForeground(QColor(255, 0, 0))
        line_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 3, line_item)
        
        pos_item = QTableWidgetItem(str(error.get('pos', '?')))
        pos_item.setForeground(QColor(255, 0, 0))
        pos_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 4, pos_item)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            if item:
                row = item.row()
                line_item = self.item(row, 3)
                pos_item = self.item(row, 4)
                
                if line_item and pos_item:
                    try:
                        line = int(line_item.text())
                        pos_text = pos_item.text()
                        if '-' in pos_text:
                            start_pos = int(pos_text.split('-')[0])
                        else:
                            start_pos = int(pos_text)
                        
                        self.error_clicked.emit(line, start_pos)
                    except:
                        pass
        
        super().mousePressEvent(event)
    
    def clear_results(self):
        self.setRowCount(0)