#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, 
    QFileDialog, QMessageBox, QApplication,
    QSplitter, QStatusBar, QLabel, QToolBar
)
from PySide6.QtGui import QAction, QKeySequence, QFont, QIcon
from PySide6.QtCore import Qt, QTimer, QSize

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
        
        self.resize(900, 700)
        self.setMinimumSize(600, 400)
        
        self.center_window()
    
    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setHandleWidth(3)
        
        self.editor = EditorWidget()
        self.editor.textChanged.connect(self.on_text_changed)
        self.editor.cursorPositionChanged.connect(self.update_cursor_position)
        self.splitter.addWidget(self.editor)
        
        self.output = OutputWidget()
        self.output.error_clicked.connect(self.goto_error_line)
        self.splitter.addWidget(self.output)
        
        self.splitter.setSizes([490, 210])
        
        layout.addWidget(self.splitter)
    
    def setup_menu(self):
        menu_font = QFont("Segoe UI", 9)
        self.menuBar().setFont(menu_font)
        
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
        delete_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(delete_action)
        
        edit_menu.addSeparator()
        
        select_all_action = QAction("Выделить все", self)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
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
        toolbar = QToolBar("Инструменты")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.addToolBar(toolbar)
        
        new_icon = QIcon.fromTheme("document-new", QIcon(":/qt-project.org/styles/commonstyle/images/new-32.png"))
        self.actions['new'].setIcon(new_icon)
        self.actions['new'].setToolTip("Создать (Ctrl+N)")
        toolbar.addAction(self.actions['new'])
        
        open_icon = QIcon.fromTheme("document-open", QIcon(":/qt-project.org/styles/commonstyle/images/open-32.png"))
        self.actions['open'].setIcon(open_icon)
        self.actions['open'].setToolTip("Открыть (Ctrl+O)")
        toolbar.addAction(self.actions['open'])
        
        save_icon = QIcon.fromTheme("document-save", QIcon(":/qt-project.org/styles/commonstyle/images/save-32.png"))
        self.actions['save'].setIcon(save_icon)
        self.actions['save'].setToolTip("Сохранить (Ctrl+S)")
        toolbar.addAction(self.actions['save'])
        
        toolbar.addSeparator()
        
        undo_icon = QIcon.fromTheme("edit-undo", QIcon(":/qt-project.org/styles/commonstyle/images/undo-32.png"))
        self.actions['undo'].setIcon(undo_icon)
        self.actions['undo'].setToolTip("Отменить (Ctrl+Z)")
        toolbar.addAction(self.actions['undo'])
        
        redo_icon = QIcon.fromTheme("edit-redo", QIcon(":/qt-project.org/styles/commonstyle/images/redo-32.png"))
        self.actions['redo'].setIcon(redo_icon)
        self.actions['redo'].setToolTip("Повторить (Ctrl+Y)")
        toolbar.addAction(self.actions['redo'])
        
        toolbar.addSeparator()
        
        copy_icon = QIcon.fromTheme("edit-copy", QIcon(":/qt-project.org/styles/commonstyle/images/copy-32.png"))
        self.actions['copy'].setIcon(copy_icon)
        self.actions['copy'].setToolTip("Копировать (Ctrl+C)")
        toolbar.addAction(self.actions['copy'])
        
        cut_icon = QIcon.fromTheme("edit-cut", QIcon(":/qt-project.org/styles/commonstyle/images/cut-32.png"))
        self.actions['cut'].setIcon(cut_icon)
        self.actions['cut'].setToolTip("Вырезать (Ctrl+X)")
        toolbar.addAction(self.actions['cut'])
        
        paste_icon = QIcon.fromTheme("edit-paste", QIcon(":/qt-project.org/styles/commonstyle/images/paste-32.png"))
        self.actions['paste'].setIcon(paste_icon)
        self.actions['paste'].setToolTip("Вставить (Ctrl+V)")
        toolbar.addAction(self.actions['paste'])
        
        toolbar.addSeparator()
        
        run_icon = QIcon.fromTheme("system-run", QIcon(":/qt-project.org/styles/commonstyle/images/execute-32.png"))
        self.actions['run'].setIcon(run_icon)
        self.actions['run'].setToolTip("Запустить анализ (F5)")
        toolbar.addAction(self.actions['run'])
        
        toolbar.addSeparator()
        
        help_icon = QIcon.fromTheme("help-contents", QIcon(":/qt-project.org/styles/commonstyle/images/help-32.png"))
        self.actions['help'].setIcon(help_icon)
        self.actions['help'].setToolTip("Справка (F1)")
        toolbar.addAction(self.actions['help'])
        
        about_icon = QIcon.fromTheme("help-about", QIcon(":/qt-project.org/styles/commonstyle/images/information-32.png"))
        self.actions['about'].setIcon(about_icon)
        self.actions['about'].setToolTip("О программе")
        toolbar.addAction(self.actions['about'])
    
    def setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        self.cursor_position_label = QLabel("Стр: 1, Стб: 1")
        self.statusbar.addPermanentWidget(self.cursor_position_label)
        
        self.file_info_label = QLabel("Новый документ")
        self.statusbar.addWidget(self.file_info_label)
    
    def update_cursor_position(self):
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.cursor_position_label.setText(f"Стр: {line}, Стб: {col}")
    
    def update_window_title(self):
        title = "Compiler"
        if self.current_file:
            title = f"{os.path.basename(self.current_file)} - {title}"
        if self.editor.is_modified():
            title = f"*{title}"
        self.setWindowTitle(title)
    
    def on_text_changed(self):
        self.update_window_title()
        
        if self.editor.is_modified():
            self.file_info_label.setText(f"✎ {os.path.basename(self.current_file) if self.current_file else 'Новый документ'}")
    
    def new_file(self):
        if self.maybe_save():
            self.editor.clear()
            self.current_file = None
            self.update_window_title()
            self.output.clear_output()
            self.file_info_label.setText("Новый документ")
    
    def open_file(self):
        if self.maybe_save():
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Открыть файл", 
                "",
                "Текстовые файлы (*.txt);;Все файлы (*.*)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        text = file.read()
                    
                    self.editor.set_text(text)
                    self.current_file = file_path
                    self.update_window_title()
                    self.output.clear_output()
                    self.file_info_label.setText(os.path.basename(file_path))
                    
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл:\n{str(e)}")
    
    def save_file(self):
        if self.current_file:
            return self.save_file_to_path(self.current_file)
        else:
            return self.save_file_as()
    
    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Сохранить файл", 
            "",
            "Текстовые файлы (*.txt);;Все файлы (*.*)"
        )
        
        if file_path:
            if '.' not in os.path.basename(file_path):
                file_path += '.txt'
            
            return self.save_file_to_path(file_path)
        
        return False
    
    def save_file_to_path(self, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.editor.get_text())
            
            self.current_file = file_path
            self.editor.set_modified(False)
            self.update_window_title()
            self.file_info_label.setText(os.path.basename(file_path))
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
            return False
    
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
        else:
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
            f"Информация по пункту '{item_name}' будет добавлена позже."
        )
    
    def run_analyzer(self):
        text = self.editor.get_text()
        lines = text.split('\n')
        
        if not text.strip():
            self.output.append_message("=" * 60)
            self.output.append_message("Текст для анализа пуст")
            self.output.append_message("=" * 60)
            return
        
        self.output.clear_output()
        self.output.append_message("=" * 60)
        self.output.append_message("РЕЗУЛЬТАТЫ АНАЛИЗА КОДА")
        self.output.append_message("=" * 60)
        
        error_count = 0
        warning_count = 0
        info_count = 0
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            if line_stripped.startswith('//') or line_stripped.startswith('#'):
                continue
            
            original_line = line
            line_for_analysis = line_stripped
            
            if ';' not in line_for_analysis and not line_for_analysis.endswith('{') and not line_for_analysis.endswith('}'):
                if not any(keyword in line_for_analysis for keyword in ['if', 'else', 'for', 'while', 'do', 'switch']):
                    self.output.append_message(f"Строка {i}: {original_line}")
                    self.output.append_message(f"         ❌ Отсутствует точка с запятой в конце")
                    self.output.append_message("")
                    error_count += 1
            
            if '(' in line_for_analysis or ')' in line_for_analysis:
                open_count = line_for_analysis.count('(')
                close_count = line_for_analysis.count(')')
                if open_count != close_count:
                    self.output.append_message(f"Строка {i}: {original_line}")
                    self.output.append_message(f"         ❌ Несбалансированные скобки (открыто: {open_count}, закрыто: {close_count})")
                    self.output.append_message("")
                    error_count += 1
            
            if '[' in line_for_analysis or ']' in line_for_analysis:
                open_count = line_for_analysis.count('[')
                close_count = line_for_analysis.count(']')
                if open_count != close_count:
                    self.output.append_message(f"Строка {i}: {original_line}")
                    self.output.append_message(f"         ❌ Несбалансированные квадратные скобки")
                    self.output.append_message("")
                    error_count += 1
            
            if '{' in line_for_analysis or '}' in line_for_analysis:
                open_count = line_for_analysis.count('{')
                close_count = line_for_analysis.count('}')
                if open_count != close_count:
                    self.output.append_message(f"Строка {i}: {original_line}")
                    self.output.append_message(f"         ❌ Несбалансированные фигурные скобки")
                    self.output.append_message("")
                    error_count += 1
            
            if '=' in line_for_analysis and '==' not in line_for_analysis and '!=' not in line_for_analysis:
                if '=' in line_for_analysis and not any(op in line_for_analysis for op in ['+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>=']):
                    if not re.search(r'\bfor\b.*\(.*;.*;.*\)', line_for_analysis):
                        self.output.append_message(f"Строка {i}: {original_line}")
                        self.output.append_message(f"         ⚠️ Возможно, вы хотели использовать '==' вместо '='")
                        self.output.append_message("")
                        warning_count += 1
            
            var_declaration = re.search(r'\b(int|float|double|char|bool|string|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[=;]', line_for_analysis)
            if var_declaration:
                var_name = var_declaration.group(2)
                found_usage = False
                for j, check_line in enumerate(lines, 1):
                    if j != i and var_name in check_line and '=' not in check_line.split(var_name)[0].strip().endswith(('int', 'float', 'double', 'char', 'bool', 'string', 'var')):
                        found_usage = True
                        break
                if not found_usage and i < len(lines):
                    self.output.append_message(f"Строка {i}: {original_line}")
                    self.output.append_message(f"         ⚠️ Переменная '{var_name}' объявлена, но не используется")
                    self.output.append_message("")
                    warning_count += 1
            
            numbers = re.findall(r'\b\d+\b', line_for_analysis)
            for num in numbers:
                if len(num) > 2 and num not in ['0', '1']:
                    context = line_for_analysis[:line_for_analysis.find(num)]
                    if not any(keyword in context for keyword in ['const', 'define', 'enum']):
                        self.output.append_message(f"Строка {i}: {original_line}")
                        self.output.append_message(f"         ℹ️ Магическое число '{num}' - лучше вынести в константу")
                        self.output.append_message("")
                        info_count += 1
            
            if len(original_line) > 100:
                self.output.append_message(f"Строка {i}: {original_line}")
                self.output.append_message(f"         ℹ️ Слишком длинная строка ({len(original_line)} символов) - рекомендуется разбить")
                self.output.append_message("")
                info_count += 1
            
            if '\t' in original_line:
                self.output.append_message(f"Строка {i}: {original_line}")
                self.output.append_message(f"         ℹ️ Используется табуляция - рекомендуется использовать пробелы")
                self.output.append_message("")
                info_count += 1
            
            if original_line.rstrip() != original_line:
                self.output.append_message(f"Строка {i}: {original_line}")
                self.output.append_message(f"         ℹ️ Есть лишние пробелы в конце строки")
                self.output.append_message("")
                info_count += 1
            
            if '{}' in line_for_analysis or '{ }' in line_for_analysis:
                self.output.append_message(f"Строка {i}: {original_line}")
                self.output.append_message(f"         ⚠️ Пустой блок кода")
                self.output.append_message("")
                warning_count += 1
            
            if 'TODO' in line_for_analysis or 'FIXME' in line_for_analysis:
                self.output.append_message(f"Строка {i}: {original_line}")
                self.output.append_message(f"         📝 Найдено: {line_for_analysis}")
                self.output.append_message("")
                info_count += 1
            
            bad_names = re.findall(r'\b([a-z]{1,2}|[A-Z]{2,})\b', line_for_analysis)
            for name in bad_names:
                if name not in ['if', 'in', 'is', 'as', 'at', 'to', 'by', 'on', 'or', 'an']:
                    context = line_for_analysis[:line_for_analysis.find(name)]
                    if 'int' in context or 'float' in context or 'string' in context or 'var' in context:
                        self.output.append_message(f"Строка {i}: {original_line}")
                        self.output.append_message(f"         ⚠️ Неоднозначное имя переменной '{name}' - используйте более описательные имена")
                        self.output.append_message("")
                        warning_count += 1
            
            hungarian = re.search(r'\b(int|float|double|char|bool|str|arr|ptr)_([a-zA-Z_][a-zA-Z0-9_]*)', line_for_analysis)
            if hungarian:
                self.output.append_message(f"Строка {i}: {original_line}")
                self.output.append_message(f"         ℹ️ Обнаружена венгерская нотация - рекомендуется использовать обычные имена")
                self.output.append_message("")
                info_count += 1
        
        full_text = text
        brackets = {
            '(': full_text.count('('),
            ')': full_text.count(')'),
            '[': full_text.count('['),
            ']': full_text.count(']'),
            '{': full_text.count('{'),
            '}': full_text.count('}')
        }
        
        if brackets['('] != brackets[')']:
            self.output.append_message(f"Глобально:")
            self.output.append_message(f"         ❌ Несбалансированные круглые скобки (открыто: {brackets['(']}, закрыто: {brackets[')']})")
            self.output.append_message("")
            error_count += 1
        
        if brackets['['] != brackets[']']:
            self.output.append_message(f"Глобально:")
            self.output.append_message(f"         ❌ Несбалансированные квадратные скобки")
            self.output.append_message("")
            error_count += 1
        
        if brackets['{'] != brackets['}']:
            self.output.append_message(f"Глобально:")
            self.output.append_message(f"         ❌ Несбалансированные фигурные скобки")
            self.output.append_message("")
            error_count += 1
        
        non_comment_lines = 0
        for line in lines:
            line_stripped = line.strip()
            if line_stripped and not line_stripped.startswith('//') and not line_stripped.startswith('#'):
                non_comment_lines += 1
        
        if non_comment_lines == 0:
            self.output.append_message(f"Глобально:")
            self.output.append_message(f"         ❌ Файл не содержит исполняемого кода (только комментарии)")
            self.output.append_message("")
            error_count += 1
        
        self.output.append_message("-" * 60)
        
        if error_count == 0 and warning_count == 0 and info_count == 0:
            self.output.append_message("✅ АНАЛИЗ ЗАВЕРШЕН: Ошибок не найдено. Код соответствует стандартам!")
        else:
            self.output.append_message(f"📊 ИТОГИ:")
            self.output.append_message(f"   Найдено ошибок: {error_count}")
            self.output.append_message(f"   Найдено предупреждений: {warning_count}")
            self.output.append_message(f"   Найдено замечаний: {info_count}")
            self.output.append_message("")
            
            if error_count > 0:
                self.output.append_message("❌ Требуется исправление ошибок")
            elif warning_count > 0:
                self.output.append_message("⚠️ Рекомендуется исправить предупреждения")
            else:
                self.output.append_message("ℹ️ Есть рекомендации по улучшению кода")
        
        self.output.append_message("=" * 60)
    
    def goto_error_line(self, line_number):
        self.editor.goto_line(line_number)
    
    def show_help(self):
        help_text = """
        <h2>Справка</h2>
        
        <h3>Меню Файл:</h3>
        <ul>
            <li><b>Создать (Ctrl+N)</b> - новый документ</li>
            <li><b>Открыть (Ctrl+O)</b> - открыть файл</li>
            <li><b>Сохранить (Ctrl+S)</b> - сохранить</li>
            <li><b>Сохранить как (Ctrl+Shift+S)</b> - сохранить как</li>
            <li><b>Выход (Ctrl+Q)</b> - выход</li>
        </ul>
        
        <h3>Меню Правка:</h3>
        <ul>
            <li><b>Отменить (Ctrl+Z)</b> - отмена</li>
            <li><b>Повторить (Ctrl+Y)</b> - повтор</li>
            <li><b>Вырезать (Ctrl+X)</b> - вырезать</li>
            <li><b>Копировать (Ctrl+C)</b> - копировать</li>
            <li><b>Вставить (Ctrl+V)</b> - вставить</li>
            <li><b>Удалить (Del)</b> - удалить</li>
            <li><b>Выделить все (Ctrl+A)</b> - выделить все</li>
        </ul>
        
        <h3>Меню Текст:</h3>
        <ul>
            <li>Информационные пункты для языкового процессора</li>
        </ul>
        
        <h3>Меню Пуск (F5):</h3>
        <ul>
            <li>Запуск универсального анализатора кода</li>
            <li>Показывает код с ошибкой и отступом для наглядности</li>
            <li>Проверяет: точки с запятой, скобки, операторы, переменные</li>
            <li>Находит: магические числа, длинные строки, TODO/FIXME</li>
        </ul>
        
        <h3>Особенности:</h3>
        <ul>
            <li>При клике на номер строки в области вывода курсор переходит к этой строке</li>
            <li>Подсветка синтаксиса Python</li>
            <li>Универсальный анализатор подходит для C, C++, Java, C#, JavaScript</li>
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
            "<h2>Compiler</h2>"
            "<p>Версия: 2.0</p>"
            "<p>Лабораторная работа №1</p>"
            "<p>языковый процессор</p>"
            "<p>Поддерживает: C, C++, Java, C#, JavaScript, Python</p>"
            "<p>© 2026</p>"
        )
