from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QTextCharFormat, QSyntaxHighlighter, QFont, QColor, QTextCursor
from PySide6.QtCore import QRegularExpression, Qt


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor(0, 0, 255))  
        self.keyword_format.setFontWeight(QFont.Weight.Bold)
        
        keywords = [
            'and', 'assert', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'exec', 'finally',
            'for', 'from', 'global', 'if', 'import', 'in',
            'is', 'lambda', 'not', 'or', 'pass', 'print',
            'raise', 'return', 'try', 'while', 'with', 'yield',
            'True', 'False', 'None', 'async', 'await'
        ]
        
        self.highlighting_rules = []
        for word in keywords:
            pattern = QRegularExpression(f'\\b{word}\\b')
            self.highlighting_rules.append((pattern, self.keyword_format))
        
 
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor(0, 128, 0))  
        

        self.highlighting_rules.append(
            (QRegularExpression('".*"'), self.string_format)
        )
        self.highlighting_rules.append(
            (QRegularExpression("'.*'"), self.string_format)
        )
        
       
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor(128, 128, 128))  # Серый
        self.comment_format.setFontItalic(True)
        
        self.highlighting_rules.append(
            (QRegularExpression('#[^\n]*'), self.comment_format)
        )

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)


class EditorWidget(QTextEdit):
   
    def __init__(self, parent=None):
        super().__init__(parent)

        font = QFont("Courier New", 10)
        font.setFixedPitch(True)
        self.setFont(font)
 
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
  
        self.highlighter = PythonHighlighter(self.document())
        
    def is_modified(self):
       
        return self.document().isModified()
    
    def set_modified(self, modified):
        
        self.document().setModified(modified)
    
    def clear(self):
    
        self.setPlainText("")
        self.set_modified(False)
    
    def get_text(self):
       
        return self.toPlainText()
    
    def set_text(self, text):
       
        self.setPlainText(text)
        self.set_modified(False)
    
    def goto_line(self, line_number):
    
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        
    
        for _ in range(line_number - 1):
            cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
        
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        self.setTextCursor(cursor)
        self.setFocus()