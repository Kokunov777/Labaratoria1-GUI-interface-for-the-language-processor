from enum import IntEnum

class State(IntEnum):
    START = 0
    IN_IDENTIFIER = 1
    IN_NUMBER = 2
    IN_FLOAT = 3
    IN_OPERATOR = 4
    IN_COMMENT = 5
    IN_STRING = 6
    IN_MULTILINE_COMMENT = 7
    IN_OPERATOR_AFTER = 8
    ERROR = 99

class CharacterClass(IntEnum):
    LETTER = 1
    DIGIT = 2
    OPERATOR = 3
    SEPARATOR = 4
    QUOTE = 5
    COMMENT_START = 6
    NEWLINE = 7
    WHITESPACE = 8
    UNKNOWN = 99

class StateMachine:
    
    def __init__(self):
        self.keywords = {
            'if', 'else', 'while', 'for', 'return', 'int', 'float',
            'char', 'void', 'struct', 'break', 'continue', 'switch',
            'case', 'default', 'do', 'typedef', 'sizeof', 'union',
            'enum', 'const', 'static', 'extern', 'register', 'auto',
            'volatile', 'signed', 'unsigned', 'short', 'long', 'double',
            'bool', 'true', 'false', 'NULL', 'class', 'public', 'private',
            'protected', 'virtual', 'friend', 'operator', 'template',
            'typename', 'namespace', 'using', 'throw', 'try', 'catch'
        }
        
        self.operators = {
            '+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|', '^',
            '~', '.', '?', ':', '+=', '-=', '*=', '/=', '%=', '&=', '|=',
            '^=', '<<', '>>', '<<=', '>>=', '==', '!=', '<=', '>=', '&&',
            '||', '++', '--', '->', '::'
        }
        
        self.single_operators = {'+', '-', '*', '/', '%', '=', '>', '<', '!', '&', '|', '^', '~', '.'}
        
        self.separators = {'(', ')', '{', '}', '[', ']', ',', ';', ':', '?'}
        
        self.multiline_comment_start = '/*'
        self.multiline_comment_end = '*/'
        self.singleline_comment = '//'
    
    def get_char_class(self, ch):
        if ch.isalpha() or ch == '_':
            return CharacterClass.LETTER
        elif ch.isdigit():
            return CharacterClass.DIGIT
        elif ch in self.single_operators:
            return CharacterClass.OPERATOR
        elif ch in self.separators:
            return CharacterClass.SEPARATOR
        elif ch == '"' or ch == "'":
            return CharacterClass.QUOTE
        elif ch == '/':
            return CharacterClass.COMMENT_START
        elif ch == '\n':
            return CharacterClass.NEWLINE
        elif ch.isspace():
            return CharacterClass.WHITESPACE
        else:
            return CharacterClass.UNKNOWN
    
    def is_keyword(self, word):
        return word in self.keywords
    
    def is_operator(self, op):
        return op in self.operators