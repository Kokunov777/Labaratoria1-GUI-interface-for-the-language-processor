import os
import sys

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QFileDialog, QMessageBox, QApplication, QTextEdit,
    QSplitter, QStatusBar, QLabel
)
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtCore import Qt, QSize

from editor_widget import EditorWidget
from output_widget import OutputWidget


class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.current_file = None
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        
        self.update_window_title()
        
        self.setMinimumSize(800, 600)
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        self.editor = EditorWidget()
        self.editor.textChanged.connect(self.on_text_changed)
        splitter.addWidget(self.editor)
        
        self.output = OutputWidget()
        self.output.error_clicked.connect(self.goto_error_line)
        splitter.addWidget(self.output)
        
        splitter.setSizes([int(self.height() * 0.7), int(self.height() * 0.3)])
        
        main_layout.addWidget(splitter)
    
    def setup_menu(self):
        file_menu = self.menuBar().addMenu("Файл")
    
        new_action = QAction("Создать", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Открыть", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Сохранить", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Сохранить как", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()

        exit_action = QAction("Выход", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = self.menuBar().addMenu("Правка")
        
        undo_action = QAction("Отменить", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Повторить", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Вырезать", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction("Копировать", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction("Вставить", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste_action)

        delete_action = QAction("Удалить", self)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.triggered.connect(self.editor.cut)  # В Qt delete удаляет без копирования
        edit_menu.addAction(delete_action)
        
        edit_menu.addSeparator()

        select_all_action = QAction("Выделить все", self)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(self.editor.selectAll)
        edit_menu.addAction(select_all_action)

        text_menu = self.menuBar().addMenu("Текст")
        
        text_items = [
            "Постановка задачи", "Грамматика", "Классификация грамматики",
            "Метод анализа", "Тестовый пример", "Список литературы",
            "Исходный код программы"
        ]
        
        for item in text_items:
            action = QAction(item, self)
            action.triggered.connect(lambda checked, text=item: self.show_text_info(text))
            text_menu.addAction(action)

        run_menu = self.menuBar().addMenu("Пуск")
        run_action = QAction("Запустить анализ", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self.run_analyzer)
        run_menu.addAction(run_action)

        help_menu = self.menuBar().addMenu("Справка")

        help_action = QAction("Вызов справки", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        self.actions = {
            'new': new_action,
            'open': open_action,
            'save': save_action,
            'undo': undo_action,
            'redo': redo_action,
            'cut': cut_action,
            'copy': copy_action,
            'paste': paste_action,
            'run': run_action,
            'help': help_action,
            'about': about_action
        }
    
    def setup_toolbar(self):
        toolbar = self.addToolBar("Инструменты")
        toolbar.setIconSize(QSize(24, 24))
        
        toolbar.addAction(self.actions['new'])
        toolbar.addAction(self.actions['open'])
        toolbar.addAction(self.actions['save'])
        toolbar.addSeparator()
        toolbar.addAction(self.actions['undo'])
        toolbar.addAction(self.actions['redo'])
        toolbar.addSeparator()
        toolbar.addAction(self.actions['copy'])
        toolbar.addAction(self.actions['cut'])
        toolbar.addAction(self.actions['paste'])
        toolbar.addSeparator()
        toolbar.addAction(self.actions['run'])
        toolbar.addSeparator()
        toolbar.addAction(self.actions['help'])
        toolbar.addAction(self.actions['about'])
    
    def setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        self.cursor_position_label = QLabel("Стр: 1, Стб: 1")
        self.statusbar.addPermanentWidget(self.cursor_position_label)
        
        self.file_info_label = QLabel("")
        self.statusbar.addWidget(self.file_info_label)

        self.editor.cursorPositionChanged.connect(self.update_cursor_position)
    
    def update_cursor_position(self):
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.cursor_position_label.setText(f"Стр: {line}, Стб: {col}")
    
    def update_window_title(self):
        title = "Текстовый редактор"
        if self.current_file:
            title = f"{os.path.basename(self.current_file)} - {title}"
        if self.editor.is_modified():
            title = f"*{title}"
        self.setWindowTitle(title)
    
    def on_text_changed(self):
        self.update_window_title()
    
    def new_file(self):
        if self.maybe_save():
            self.editor.clear()
            self.current_file = None
            self.update_window_title()
            self.output.clear_output()
            self.output.append_message("Создан новый документ")
    
    def open_file(self):
        if self.maybe_save():
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Открыть файл", "",
                "Текстовые файлы (*.txt);;Python файлы (*.py);;Все файлы (*.*)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        text = file.read()
                    
                    self.editor.set_text(text)
                    self.current_file = file_path
                    self.update_window_title()
                    self.output.clear_output()
                    self.output.append_message(f"Файл открыт: {file_path}")
                    self.file_info_label.setText(f"Открыт: {os.path.basename(file_path)}")
                    
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл:\n{str(e)}")
    
    def save_file(self):
        if self.current_file:
            return self.save_file_to_path(self.current_file)
        else:
            return self.save_file_as()
    
    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить файл", "",
            "Текстовые файлы (*.txt);;Python файлы (*.py);;Все файлы (*.*)"
        )
        
        if file_path:
            return self.save_file_to_path(file_path)
        
        return False
    
    def save_file_to_path(self, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.editor.get_text())
            
            self.current_file = file_path
            self.editor.set_modified(False)
            self.update_window_title()
            self.output.append_message(f"Файл сохранен: {file_path}")
            self.file_info_label.setText(f"Сохранен: {os.path.basename(file_path)}")
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
            return False
    
    def maybe_save(self):
        if not self.editor.is_modified():
            return True
        
        reply = QMessageBox.question(
            self, "Сохранение",
            "Документ был изменен. Сохранить изменения?",
            QMessageBox.StandardButton.Save | 
            QMessageBox.StandardButton.Discard | 
            QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Save:
            return self.save_file()
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:  # Cancel
            return False
    
    def closeEvent(self, event):
        if self.maybe_save():
            event.accept()
        else:
            event.ignore()
    
    def show_text_info(self, item_name):
        QMessageBox.information(
            self, 
            item_name,
            f"Это заглушка для пункта меню '{item_name}'.\n"
            "В следующей лабораторной работе здесь будет отображаться соответствующая информация."
        )
    
    def run_analyzer(self):
        text = self.editor.get_text()
        
        if not text.strip():
            self.output.append_message("Текст для анализа пуст", "warning")
            return
        
        self.output.clear_output()
        self.output.append_message("Запуск анализатора...", "info")

        lines = text.split('\n')
        self.output.append_message(f"Анализ завершен. Найдено строк: {len(lines)}", "success")

        if "error" in text.lower() or "ошибка" in text.lower():
            for i, line in enumerate(lines, 1):
                if "error" in line.lower() or "ошибка" in line.lower():
                    self.output.append_message(f"Error at line {i}: Найдена синтаксическая ошибка", "error")
    
    def goto_error_line(self, line_number):
        self.editor.goto_line(line_number)
        self.output.append_message(f"Переход к строке {line_number}", "info")
    
    def show_help(self):
        help_text = """
        <h2>Руководство пользователя</h2>
        
        <h3>Меню Файл:</h3>
        <ul>
            <li><b>Создать (Ctrl+N)</b> - создает новый документ</li>
            <li><b>Открыть (Ctrl+O)</b> - открывает существующий файл</li>
            <li><b>Сохранить (Ctrl+S)</b> - сохраняет текущий документ</li>
            <li><b>Сохранить как (Ctrl+Shift+S)</b> - сохраняет документ под новым именем</li>
            <li><b>Выход (Ctrl+Q)</b> - закрывает приложение</li>
        </ul>
        
        <h3>Меню Правка:</h3>
        <ul>
            <li><b>Отменить (Ctrl+Z)</b> - отменяет последнее действие</li>
            <li><b>Повторить (Ctrl+Y)</b> - повторяет отмененное действие</li>
            <li><b>Вырезать (Ctrl+X)</b> - вырезает выделенный текст</li>
            <li><b>Копировать (Ctrl+C)</b> - копирует выделенный текст</li>
            <li><b>Вставить (Ctrl+V)</b> - вставляет текст из буфера обмена</li>
            <li><b>Удалить (Del)</b> - удаляет выделенный текст</li>
            <li><b>Выделить все (Ctrl+A)</b> - выделяет весь текст</li>
        </ul>
        
        <h3>Меню Текст:</h3>
        <ul>
            <li>Содержит информационные пункты для будущей реализации языкового процессора</li>
        </ul>
        
        <h3>Меню Пуск (F5):</h3>
        <ul>
            <li>Запускает анализ текста (имитация работы)</li>
        </ul>
        
        <h3>Особенности:</h3>
        <ul>
            <li>Подсветка синтаксиса Python</li>
            <li>При клике на сообщение об ошибке в области вывода, курсор в редакторе переходит к соответствующей строке</li>
            <li>При изменении текста в заголовке окна появляется звездочка (*)</li>
            <li>При закрытии или открытии нового файла программа предлагает сохранить изменения</li>
        </ul>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Справка")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(help_text)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    
    def show_about(self):
        QMessageBox.about(
            self,
            "О программе",
            "<h2>Текстовый редактор</h2>"
            "<p>Версия: 1.0</p>"
            "<p>Лабораторная работа №1: Разработка пользовательского интерфейса</p>"
            "<p><b>Автор:</b> Студент группы 313</p>"
            "<p><b>Технологии:</b> Python + PySide6 </p>"
            "<p>Программа реализует базовый текстовый редактор "
            "с функциями файловых операций, редактирования текста "
            "и подготовкой к интеграции языкового процессора.</p>"
            "<p>© 2026</p>"
        )