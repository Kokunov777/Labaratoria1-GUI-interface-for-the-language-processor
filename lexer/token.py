from enum import IntEnum

class TokenType(IntEnum):
    KEYWORD = 1
    IDENTIFIER = 2
    INTEGER = 3
    FLOAT = 4
    OPERATOR = 5
    SEPARATOR = 6
    COMMENT = 7
    STRING = 8
    UNKNOWN = 99

class Token:
    def __init__(self, token_type, value, line, start_pos, end_pos):
        self.type = token_type
        self.value = value
        self.line = line
        self.start_pos = start_pos
        self.end_pos = end_pos
    
    def get_type_name(self):
        names = {
            TokenType.KEYWORD: "Ключевое слово",
            TokenType.IDENTIFIER: "Идентификатор",
            TokenType.INTEGER: "Целое число",
            TokenType.FLOAT: "Вещественное число",
            TokenType.OPERATOR: "Оператор",
            TokenType.SEPARATOR: "Разделитель",
            TokenType.COMMENT: "Комментарий",
            TokenType.STRING: "Строка",
            TokenType.UNKNOWN: "Ошибка"
        }
        return names.get(self.type, "Неизвестно")
    
    def __str__(self):
        return f"[{self.line}:{self.start_pos}-{self.end_pos}] {self.get_type_name()}: '{self.value}'"