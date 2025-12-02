#!/usr/bin/env python3
import sys
import re
import yaml


class ParseError(Exception):
    pass


TOKEN_REGEX = re.compile(
    r"""
    (?P<STRING>q\([^)]*\)) |
    (?P<NUMBER>\d+) |
    (?P<NAME>[a-zA-Z0-9]+) |
    (?P<LBRACE>\{) |
    (?P<RBRACE>\}) |
    (?P<ARROW>->) |
    (?P<EQ>=) |
    (?P<SEMICOLON>;) |
    (?P<CONST>\^\[[a-zA-Z]+\]) |
    (?P<DOT>\.)
    """,
    re.VERBOSE,
)


class Lexer:
    def __init__(self, text):
        self.tokens = []
        self.pos = 0
        # удалить все пробелы
        text = re.sub(r'\s+', '', text)
        for match in TOKEN_REGEX.finditer(text):
            kind = match.lastgroup
            value = match.group()
            self.tokens.append((kind, value))
        self.tokens.append(("EOF", None))

    def peek(self):
        return self.tokens[self.pos]

    def next(self):
        token = self.tokens[self.pos]
        self.pos += 1
        return token


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.constants = {}

    def expect(self, kind):
        token = self.lexer.next()
        if token[0] != kind:
            raise ParseError(f"Ожидалось {kind}, найдено {token}")
        return token

    def parse(self):
        result = {}
        while True:
            token = self.lexer.peek()
            if token[0] == "EOF":
                break
            name, value = self.parse_const_or_dict_item()
            result[name] = value
        return result

    def parse_const_or_dict_item(self):
        token = self.lexer.peek()
        if token[0] == "NAME":
            name = self.lexer.next()[1]
            next_token = self.lexer.peek()

            if next_token[0] == "EQ":
                self.lexer.next()
                value = self.parse_value()
                self.expect("SEMICOLON")
                self.constants[name] = value
                return name, value

            elif next_token[0] == "ARROW":
                self.lexer.next()
                value = self.parse_value()
                self.expect("DOT")
                return name, value

        raise ParseError(f"Неожиданная конструкция возле {token}")

    def parse_value(self):
        token = self.lexer.peek()

        if token[0] == "NUMBER":
            return int(self.lexer.next()[1])

        if token[0] == "STRING":
            text = self.lexer.next()[1]
            return text[2:-1]

        if token[0] == "CONST":
            const_name = token[1][2:-1]
            self.lexer.next()
            if const_name not in self.constants:
                raise ParseError(f"Неизвестная константа {const_name}")
            return self.constants[const_name]

        if token[0] == "LBRACE":
            return self.parse_dict()

        raise ParseError(f"Недопустимое значение: {token}")

    def parse_dict(self):
        self.expect("LBRACE")
        result = {}
        while True:
            token = self.lexer.peek()
            if token[0] == "RBRACE":
                self.lexer.next()
                break
            if token[0] != "NAME":
                raise ParseError("Ожидалось имя в словаре")

            key = self.lexer.next()[1]
            self.expect("ARROW")
            value = self.parse_value()
            self.expect("DOT")
            result[key] = value
        return result


def main():
    text = sys.stdin.read()
    lexer = Lexer(text)
    parser = Parser(lexer)

    try:
        data = parser.parse()
    except ParseError as e:
        print(f"Синтаксическая ошибка: {e}", file=sys.stderr)
        sys.exit(1)

    print(yaml.dump(data, allow_unicode=True, sort_keys=False))

# Get-Content input.txt -Raw | python main.py > output.yml
if __name__ == "__main__":
    main()
