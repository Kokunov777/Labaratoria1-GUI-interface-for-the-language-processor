import os
import sys
from PySide6.QtGui import QFont

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QFileDialog, QMessageBox, QApplication, QTextEdit,
    QSplitter, QStatusBar, QLabel, QPushButton, QToolBar
)
from PySide6.QtGui import QAction, QIcon, QKeySequence, QFont
from PySide6.QtCore import Qt, QSize, QTimer

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
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave)
        self.update_window_title()
        self.setMinimumSize(800, 600)
        self.center_window()
    
    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setHandleWidth(5)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #cccccc;
                height: 5px;
            }
            QSplitter::handle:hover {
                background-color: #999999;
            }
        """)

        self.editor = EditorWidget()
        self.editor.textChanged.connect(self.on_text_changed)
        self.editor.cursorPositionChanged.connect(self.update_cursor_position)
        self.splitter.addWidget(self.editor)
        self.output = OutputWidget()
        self.output.error_clicked.connect(self.goto_error_line)
        self.splitter.addWidget(self.output)
        self.splitter.setSizes([int(self.height() * 0.7), int(self.height() * 0.3)])
        
        main_layout.addWidget(self.splitter)
    
    def setup_menu(self):
        menu_font = QFont("Segoe UI", 9)
        self.menuBar().setFont(menu_font)
        file_menu = self.menuBar().addMenu("Файл")
        new_action = QAction("Создать", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.setStatusTip("Создать новый документ")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        open_action = QAction("Открыть", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip("Открыть существующий файл")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        save_action = QAction("Сохранить", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.setStatusTip("Сохранить текущий документ")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        save_as_action = QAction("Сохранить как", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.setStatusTip("Сохранить документ под новым именем")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        exit_action = QAction("Выход", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Выйти из программы")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        edit_menu = self.menuBar().addMenu("Правка")

        undo_action = QAction("Отменить", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.setStatusTip("Отменить последнее действие")
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Повторить", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.setStatusTip("Повторить отмененное действие")
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)
        edit_menu.addSeparator()

        cut_action = QAction("Вырезать", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.setStatusTip("Вырезать выделенный текст")
        cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_action)
        copy_action = QAction("Копировать", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.setStatusTip("Копировать выделенный текст")
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)
        paste_action = QAction("Вставить", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.setStatusTip("Вставить текст из буфера обмена")
        paste_action.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste_action)
        delete_action = QAction("Удалить", self)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.setStatusTip("Удалить выделенный текст")
        delete_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(delete_action)
        
        edit_menu.addSeparator()
        
        select_all_action = QAction("Выделить все", self)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.setStatusTip("Выделить весь текст")
        select_all_action.triggered.connect(self.editor.selectAll)
        edit_menu.addAction(select_all_action)
        
        text_menu = self.menuBar().addMenu("Текст")
        
        text_items = [
            "Постановка задачи",
            "Грамматика",
            "Классификация грамматики",
            "Метод анализа",
            "Тестовый пример",
            "Список литературы",
            "Исходный код программы"
        ]
        
        for item in text_items:
            action = QAction(item, self)
            action.setStatusTip(f"Показать информацию: {item}")
            action.triggered.connect(lambda checked, text=item: self.show_text_info(text))
            text_menu.addAction(action)
        
        run_menu = self.menuBar().addMenu("Пуск")
        run_action = QAction("Запустить анализ", self)
        run_action.setShortcut("F5")
        run_action.setStatusTip("Запустить синтаксический анализатор")
        run_action.triggered.connect(self.run_analyzer)
        run_menu.addAction(run_action)
        

        help_menu = self.menuBar().addMenu("Справка")
        

        help_action = QAction("Вызов справки", self)
        help_action.setShortcut("F1")
        help_action.setStatusTip("Открыть руководство пользователя")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        about_action = QAction("О программе", self)
        about_action.setStatusTip("Информация о программе")
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
            'delete': delete_action,
            'select_all': select_all_action,
            'run': run_action,
            'help': help_action,
            'about': about_action
        }
    
    def setup_toolbar(self):
      
        toolbar = self.addToolBar("Инструменты")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        
        self.add_toolbar_action(toolbar, self.actions['new'], "📄", "Новый")
        self.add_toolbar_action(toolbar, self.actions['open'], "📂", "Открыть")
        self.add_toolbar_action(toolbar, self.actions['save'], "💾", "Сохранить")
        
        toolbar.addSeparator()

        self.add_toolbar_action(toolbar, self.actions['undo'], "↩️", "Отменить")
        self.add_toolbar_action(toolbar, self.actions['redo'], "↪️", "Повторить")
        
        toolbar.addSeparator()
        
        self.add_toolbar_action(toolbar, self.actions['copy'], "📋", "Копировать")
        self.add_toolbar_action(toolbar, self.actions['cut'], "✂️", "Вырезать")
        self.add_toolbar_action(toolbar, self.actions['paste'], "📌", "Вставить")
        
        toolbar.addSeparator()

        self.add_toolbar_action(toolbar, self.actions['run'], "▶️", "Запуск анализа")
        
        toolbar.addSeparator()
        
        self.add_toolbar_action(toolbar, self.actions['help'], "❓", "Справка")
        self.add_toolbar_action(toolbar, self.actions['about'], "ℹ️", "О программе")
    
    def add_toolbar_action(self, toolbar, action, icon_text, tooltip):

        action.setText(icon_text)
        action.setToolTip(tooltip)
        toolbar.addAction(action)
    
    def setup_statusbar(self):

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        

        self.cursor_position_label = QLabel("Стр: 1, Стб: 1")
        self.cursor_position_label.setMinimumWidth(120)
        self.statusbar.addPermanentWidget(self.cursor_position_label)
        
        self.file_size_label = QLabel("Размер: 0 байт")
        self.file_size_label.setMinimumWidth(120)
        self.statusbar.addPermanentWidget(self.file_size_label)

        self.insert_mode_label = QLabel("ВСТ")
        self.insert_mode_label.setMinimumWidth(40)
        self.statusbar.addPermanentWidget(self.insert_mode_label)

        self.file_info_label = QLabel("Новый документ")
        self.statusbar.addWidget(self.file_info_label)

        self.temp_message_label = QLabel()
        self.temp_message_label.setStyleSheet("color: green;")
        self.statusbar.addWidget(self.temp_message_label)

        self.message_timer = QTimer()
        self.message_timer.setSingleShot(True)
        self.message_timer.timeout.connect(self.clear_temp_message)
    
    def show_temp_message(self, message, message_type="info"):
        colors = {
            "info": "green",
            "error": "red",
            "warning": "orange"
        }
        self.temp_message_label.setStyleSheet(f"color: {colors.get(message_type, 'green')};")
        self.temp_message_label.setText(message)
        self.message_timer.start(3000)  # 3 секунды
    
    def clear_temp_message(self):
        self.temp_message_label.clear()
    
    def update_cursor_position(self):
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.cursor_position_label.setText(f"Стр: {line}, Стб: {col}")
    
    def update_file_size(self):
        text = self.editor.get_text()
        size = len(text.encode('utf-8'))
        
        if size < 1024:
            size_str = f"{size} байт"
        elif size < 1024 * 1024:
            size_str = f"{size/1024:.1f} КБ"
        else:
            size_str = f"{size/(1024*1024):.1f} МБ"
        
        self.file_size_label.setText(f"Размер: {size_str}")
    
    def update_window_title(self):
        title = "Текстовый редактор"
        if self.current_file:
            title = f"{os.path.basename(self.current_file)} - {title}"
        if self.editor.is_modified():
            title = f"*{title}"
        self.setWindowTitle(title)
    
    def on_text_changed(self):
        self.update_window_title()
        self.update_file_size()
        
        if self.editor.is_modified():
            self.file_info_label.setText(f"✎ {os.path.basename(self.current_file) if self.current_file else 'Новый документ'}")
    
    def new_file(self):
        if self.maybe_save():
            self.editor.clear()
            self.current_file = None
            self.update_window_title()
            self.output.clear_output()
            self.file_info_label.setText("Новый документ")
            self.show_temp_message("Создан новый документ")
    
    def open_file(self):
        if self.maybe_save():
            file_path, selected_filter = QFileDialog.getOpenFileName(
                self, 
                "Открыть файл", 
                "",
                "Текстовые файлы (*.txt);;Python файлы (*.py);;Все файлы (*.*)"
            )
            
            if file_path:
                try:
                    encodings = ['utf-8', 'cp1251', 'koi8-r', 'latin-1']
                    text = None
                    
                    for encoding in encodings:
                        try:
                            with open(file_path, 'r', encoding=encoding) as file:
                                text = file.read()
                            break
                        except UnicodeDecodeError:
                            continue
                    
                    if text is None:
                        with open(file_path, 'rb') as file:
                            text = file.read().decode('latin-1')
                    
                    self.editor.set_text(text)
                    self.current_file = file_path
                    self.update_window_title()
                    self.output.clear_output()
                    self.output.append_message(f"Файл открыт: {file_path}")
                    self.file_info_label.setText(f"Открыт: {os.path.basename(file_path)}")
                    self.show_temp_message(f"Файл загружен: {os.path.basename(file_path)}")
                    self.update_file_size()
                    
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл:\n{str(e)}")
                    self.show_temp_message("Ошибка открытия файла", "error")
    
    def save_file(self):
        if self.current_file:
            success = self.save_file_to_path(self.current_file)
        else:
            success = self.save_file_as()
        
        if success:
            self.show_temp_message("Файл сохранен")
        return success
    
    def save_file_as(self):
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, 
            "Сохранить файл", 
            "",
            "Текстовые файлы (*.txt);;Python файлы (*.py);;Все файлы (*.*)"
        )
        
        if file_path:
            if '.' not in os.path.basename(file_path):
                if selected_filter == "Текстовые файлы (*.txt)":
                    file_path += '.txt'
                elif selected_filter == "Python файлы (*.py)":
                    file_path += '.py'
            
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
            self.update_file_size()
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
            self.show_temp_message("Ошибка сохранения файла", "error")
            return False
    
    def autosave(self):
        if self.current_file and self.editor.is_modified():
            self.save_file_to_path(self.current_file)
            self.show_temp_message("Автосохранение выполнено", "info")
    
    def maybe_save(self):
        if not self.editor.is_modified():
            return True
        
        reply = QMessageBox.question(
            self, 
            "Сохранение",
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
        info_texts = {
            "Постановка задачи": "Разработать языковой процессор для обработки текстов на основе формальной грамматики.",
            "Грамматика": "G = (N, T, P, S), где N - нетерминалы, T - терминалы, P - правила вывода, S - начальный символ.",
            "Классификация грамматики": "Контекстно-свободная грамматика (тип 2 по иерархии Хомского).",
            "Метод анализа": "Метод рекурсивного спуска с предварительным построением множеств FIRST и FOLLOW.",
            "Тестовый пример": "Пример входной строки: 'a + b * c'. Ожидаемый результат: успешный разбор.",
            "Список литературы": "1. Ахо А., Сети Р., Ульман Д. Компиляторы: принципы, технологии и инструменты.\n2. Хопкрофт Д., Мотвани Р., Ульман Д. Введение в теорию автоматов, языков и вычислений.",
            "Исходный код программы": "Исходный код программы находится в файлах:\n- main.py\n- main_window.py\n- editor_widget.py\n- output_widget.py"
        }
        
        text = info_texts.get(item_name, f"Информация по пункту '{item_name}'")
        
        QMessageBox.information(
            self, 
            item_name,
            f"<h3>{item_name}</h3><p>{text}</p>"
        )
    
    def run_analyzer(self):
        text = self.editor.get_text()
        
        if not text.strip():
            self.output.append_message("Текст для анализа пуст", "warning")
            self.show_temp_message("Текст пуст", "warning")
            return
        
        self.output.clear_output()
        self.output.append_message("=" * 50, "info")
        self.output.append_message("ЗАПУСК АНАЛИЗАТОРА", "info")
        self.output.append_message("=" * 50, "info")
        
        self.output.append_message(f"Анализ текста...", "info")
        
        lines = text.split('\n')
        total_chars = len(text)
        words = len(text.split())
        
        self.output.append_message("", "info")
        self.output.append_message("📊 СТАТИСТИКА:", "info")
        self.output.append_message(f"   Строк: {len(lines)}", "info")
        self.output.append_message(f"   Слов: {words}", "info")
        self.output.append_message(f"   Символов: {total_chars}", "info")
        self.output.append_message("", "info")
        
        self.output.append_message("🔍 РЕЗУЛЬТАТЫ АНАЛИЗА:", "info")
        
        error_found = False
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                self.output.append_message(f"⚠️ Предупреждение в строке {i}: Строка слишком длинная (>100 символов)", "warning")
                error_found = True
            if "TODO" in line:
                self.output.append_message(f"ℹ️ Заметка в строке {i}: Найдено TODO", "info")
            if "error" in line.lower() or "ошибка" in line.lower():
                self.output.append_message(f"❌ Error at line {i}: Найдена синтаксическая ошибка", "error")
                error_found = True
            if line.strip() and not line.strip().endswith(('.', '!', '?', ';', '}')):
                # Имитация ошибки пунктуации для последней строки
                if i == len(lines) and i > 3:
                    self.output.append_message(f"❌ Error at line {i}: Отсутствует точка в конце предложения", "error")
                    error_found = True
        
        self.output.append_message("", "info")
        self.output.append_message("=" * 50, "info")
        
        if error_found:
            self.output.append_message("❌ АНАЛИЗ ЗАВЕРШЕН: Обнаружены ошибки", "error")
            self.show_temp_message("Анализ завершен: обнаружены ошибки", "error")
        else:
            self.output.append_message("✅ АНАЛИЗ ЗАВЕРШЕН: Ошибок не обнаружено", "success")
            self.show_temp_message("Анализ завершен успешно", "success")
    
    def goto_error_line(self, line_number):
        self.editor.goto_line(line_number)
        self.show_temp_message(f"Переход к строке {line_number}", "info")
    
    def show_help(self):
        help_text = """
        <h2>📚 Руководство пользователя</h2>
        
        <h3>📁 Меню Файл:</h3>
        <table border='1' cellpadding='5'>
        <tr><th>Команда</th><th>Горячая клавиша</th><th>Описание</th></tr>
        <tr><td>Создать</td><td>Ctrl+N</td><td>Создает новый документ</td></tr>
        <tr><td>Открыть</td><td>Ctrl+O</td><td>Открывает существующий файл</td></tr>
        <tr><td>Сохранить</td><td>Ctrl+S</td><td>Сохраняет текущий документ</td></tr>
        <tr><td>Сохранить как</td><td>Ctrl+Shift+S</td><td>Сохраняет документ под новым именем</td></tr>
        <tr><td>Выход</td><td>Ctrl+Q</td><td>Закрывает приложение</td></tr>
        </table>
        
        <h3>✏️ Меню Правка:</h3>
        <table border='1' cellpadding='5'>
        <tr><th>Команда</th><th>Горячая клавиша</th><th>Описание</th></tr>
        <tr><td>Отменить</td><td>Ctrl+Z</td><td>Отменяет последнее действие</td></tr>
        <tr><td>Повторить</td><td>Ctrl+Y</td><td>Повторяет отмененное действие</td></tr>
        <tr><td>Вырезать</td><td>Ctrl+X</td><td>Вырезает выделенный текст</td></tr>
        <tr><td>Копировать</td><td>Ctrl+C</td><td>Копирует выделенный текст</td></tr>
        <tr><td>Вставить</td><td>Ctrl+V</td><td>Вставляет текст из буфера обмена</td></tr>
        <tr><td>Удалить</td><td>Del</td><td>Удаляет выделенный текст</td></tr>
        <tr><td>Выделить все</td><td>Ctrl+A</td><td>Выделяет весь текст</td></tr>
        </table>
        
        <h3>📊 Меню Текст:</h3>
        <p>Содержит информационные пункты для будущей реализации языкового процессора.</p>
        
        <h3>▶️ Меню Пуск (F5):</h3>
        <p>Запускает анализ текста с выводом статистики и поиском потенциальных ошибок.</p>
        
        <h3>🎯 Особенности:</h3>
        <ul>
            <li><b>Подсветка синтаксиса</b> - ключевые слова Python подсвечиваются синим цветом</li>
            <li><b>Переход к ошибкам</b> - кликните на сообщение об ошибке в области вывода, чтобы перейти к соответствующей строке</li>
            <li><b>Индикация изменений</b> - звездочка (*) в заголовке показывает несохраненные изменения</li>
            <li><b>Строка состояния</b> - показывает позицию курсора, размер файла и режим вставки</li>
            <li><b>Автоопределение кодировки</b> - при открытии файлов пробуются разные кодировки</li>
        </ul>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Справка")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(help_text)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        msg_box.exec()
    
    def show_about(self):
        """Показывает информацию о программе"""
        about_text = f"""
        <h2>📝 Текстовый редактор</h2>
        <p><b>Версия:</b> 1.0.1</p>
        <p><b>Лабораторная работа №1:</b> Разработка пользовательского интерфейса</p>
        
        <h3>👨‍💻 Автор:</h3>
        <p>kokunov Andrey group 313</p>
        
        <h3>🔧 Технологии:</h3>
        <ul>
            <li>Python {sys.version.split()[0]}</li>
            <li>PySide6 (Qt for Python)</li>
        </ul>
        
        <h3>📋 Описание:</h3>
        <p>Текстовый редактор с поддержкой подсветки синтаксиса<br>
        и возможностью интеграции языкового процессора.</p>
        
        <h3>✅ Реализованные функции:</h3>
        <ul>
            <li>Работа с файлами (создание, открытие, сохранение)</li>
            <li>Редактирование текста (отмена/повтор, копирование/вставка)</li>
            <li>Подсветка синтаксиса Python</li>
            <li>Область вывода с переходом к ошибкам</li>
            <li>Панель инструментов и строка состояния</li>
            <li>Справочная система</li>
        </ul>
        
        <p><i>© 2026.</i></p>
        """
        
        QMessageBox.about(self, "О программе", about_text)