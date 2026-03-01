import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setApplicationName("Текстовый редактор")
    app.setApplicationDisplayName("Текстовый редактор")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())