from lexer.token import Token, TokenType
from lexer.state_machine import State, CharacterClass, StateMachine

class Scanner:
    
    def __init__(self):
        self.state_machine = StateMachine()
        self.tokens = []
        self.errors = []
        self.current_line = 1
        self.current_pos = 1
        self.current_token_start = 1
    
    def reset(self):
        self.tokens = []
        self.errors = []
        self.current_line = 1
        self.current_pos = 1
        self.current_token_start = 1
    
    def scan(self, text):
        self.reset()
        
        lines = text.split('\n')
        for line_num, line in enumerate(lines, 1):
            self.current_line = line_num
            self.current_pos = 1
            self.current_token_start = 1
            self._scan_line(line)
        
        return self.tokens, self.errors
    
    def _scan_line(self, line):
        i = 0
        length = len(line)
        
        while i < length:
            ch = line[i]
            
            if ch.isspace():
                i += 1
                self.current_pos = i + 1
                continue
            
            self.current_token_start = i + 1
            
            if ch.isalpha() or ch == '_':
                i = self._scan_identifier(line, i)
            elif ch.isdigit():
                i = self._scan_number(line, i)
            elif ch == '"' or ch == "'":
                i = self._scan_string(line, i, ch)
            elif ch == '/' and i + 1 < length and line[i + 1] == '/':
                self._scan_singleline_comment(line[i:])
                break
            elif ch == '/' and i + 1 < length and line[i + 1] == '*':
                i = self._scan_multiline_comment(line, i)
                if i >= length:
                    self.errors.append({
                        'line': self.current_line,
                        'pos': self.current_token_start,
                        'message': 'Незакрытый многострочный комментарий'
                    })
            elif ch in self.state_machine.single_operators:
                i = self._scan_operator(line, i)
            elif ch in self.state_machine.separators:
                self._add_token(TokenType.SEPARATOR, ch)
                i += 1
                self.current_pos = i + 1
            else:
                self.errors.append({
                    'line': self.current_line,
                    'pos': self.current_token_start,
                    'char': ch,
                    'message': f'Недопустимый символ: {ch}'
                })
                i += 1
                self.current_pos = i + 1
    
    def _scan_identifier(self, line, start):
        i = start
        while i < len(line) and (line[i].isalnum() or line[i] == '_'):
            i += 1
        
        word = line[start:i]
        
        if self.state_machine.is_keyword(word):
            self._add_token(TokenType.KEYWORD, word)
        else:
            self._add_token(TokenType.IDENTIFIER, word)
        
        self.current_pos = i + 1
        return i
    
    def _scan_number(self, line, start):
        i = start
        is_float = False
        
        while i < len(line) and line[i].isdigit():
            i += 1
        
        if i < len(line) and line[i] == '.':
            is_float = True
            i += 1
            while i < len(line) and line[i].isdigit():
                i += 1
        
        if i < len(line) and (line[i] == 'e' or line[i] == 'E'):
            is_float = True
            i += 1
            if i < len(line) and (line[i] == '+' or line[i] == '-'):
                i += 1
            while i < len(line) and line[i].isdigit():
                i += 1
        
        number = line[start:i]
        
        if is_float:
            self._add_token(TokenType.FLOAT, number)
        else:
            self._add_token(TokenType.INTEGER, number)
        
        self.current_pos = i + 1
        return i
    
    def _scan_string(self, line, start, quote_char):
        i = start + 1
        while i < len(line) and line[i] != quote_char:
            if line[i] == '\\' and i + 1 < len(line):
                i += 2
            else:
                i += 1
        
        if i < len(line) and line[i] == quote_char:
            string_value = line[start:i + 1]
            self._add_token(TokenType.STRING, string_value)
            i += 1
        else:
            self.errors.append({
                'line': self.current_line,
                'pos': self.current_token_start,
                'message': f'Незакрытая строка'
            })
            string_value = line[start:]
            self._add_token(TokenType.STRING, string_value + " (незакрытая)")
            i = len(line)
        
        self.current_pos = i + 1
        return i
    
    def _scan_singleline_comment(self, line_part):
        self._add_token(TokenType.COMMENT, line_part)
    
    def _scan_operator(self, line, start):
        i = start
        possible_op = ''
        
        while i < len(line) and line[i] in self.state_machine.single_operators:
            possible_op += line[i]
            i += 1
        
        while possible_op:
            if possible_op in self.state_machine.operators:
                self._add_token(TokenType.OPERATOR, possible_op)
                self.current_pos = start + len(possible_op) + 1
                return start + len(possible_op)
            possible_op = possible_op[:-1]
        
        self._add_token(TokenType.OPERATOR, line[start])
        self.current_pos = start + 2
        return start + 1
    
    def _scan_multiline_comment(self, line, start):
        i = start + 2
        comment_text = line[start:start + 2]
        
        while i < len(line):
            if line[i] == '*' and i + 1 < len(line) and line[i + 1] == '/':
                comment_text += '*/'
                self._add_token(TokenType.COMMENT, comment_text)
                self.current_pos = i + 2 + 1
                return i + 2
            else:
                comment_text += line[i]
                i += 1
        
        self._add_token(TokenType.COMMENT, comment_text + " (незакрытый)")
        return len(line)
    
    def _add_token(self, token_type, value):
        token = Token(
            token_type,
            value,
            self.current_line,
            self.current_token_start,
            self.current_pos
        )
        self.tokens.append(token)