import unittest
from main import Scanner, TokenType


class TestScanner(unittest.TestCase):
    def test_empty_source(self):
        """Test that scanner returns only EOF token for empty source"""
        scanner = Scanner("")
        tokens = scanner.scan_tokens()

        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].token_type, TokenType.EOF)
        self.assertEqual(tokens[0].lexeme, "")
        self.assertIsNone(tokens[0].literal)
        self.assertEqual(tokens[0].line, 1)

    def test_single_character_tokens(self):
        """Test scanning of single character tokens"""
        source = "(){},.-+;*=!><"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        expected_list = [
            (TokenType.LEFT_PAREN, "("),
            (TokenType.RIGHT_PAREN, ")"),
            (TokenType.LEFT_BRACE, "{"),
            (TokenType.RIGHT_BRACE, "}"),
            (TokenType.COMMA, ","),
            (TokenType.DOT, "."),
            (TokenType.MINUS, "-"),
            (TokenType.PLUS, "+"),
            (TokenType.SEMICOLON, ";"),
            (TokenType.STAR, "*"),
            (TokenType.EQUAL, "="),
            (TokenType.BANG, "!"),
            (TokenType.GREATER, ">"),
            (TokenType.LESS, "<"),
            (TokenType.EOF, ""),
        ]

        self.assertEqual(len(tokens), len(expected_list))
        for token, expected in zip(tokens, expected_list):
            self.assertEqual(token.token_type, expected[0])
            self.assertEqual(token.lexeme, expected[1])

    def test_two_character_tokens(self):
        """Test scanning of two character tokens"""
        source = "".join(["!=", "==", "<=", ">="])
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        expected_list = [
            (TokenType.BANG_EQUAL, "!="),
            (TokenType.EQUAL_EQUAL, "=="),
            (TokenType.LESS_EQUAL, "<="),
            (TokenType.GREATER_EQUAL, ">="),
            (TokenType.EOF, ""),
        ]

        self.assertEqual(len(tokens), len(expected_list))
        for token, expected in zip(tokens, expected_list):
            self.assertEqual(token.token_type, expected[0])
            self.assertEqual(token.lexeme, expected[1])

    def test_string_literal(self):
        """Test scanning of string literals"""
        source = '"Hello, World!"'
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        self.assertEqual(len(tokens), 2)  # String token + EOF
        self.assertEqual(tokens[0].token_type, TokenType.STRING)
        self.assertEqual(tokens[0].literal, "Hello, World!")
        self.assertEqual(tokens[0].lexeme, '"Hello, World!"')

    def test_number_literal(self):
        """Test scanning of number literals"""
        source = "123 123.456"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        self.assertEqual(len(tokens), 3)  # Two numbers + EOF
        self.assertEqual(tokens[0].token_type, TokenType.NUMBER)
        self.assertEqual(tokens[0].literal, 123)
        self.assertEqual(tokens[1].token_type, TokenType.NUMBER)
        self.assertEqual(tokens[1].literal, 123.456)

    def test_keywords(self):
        """Test scanning of keywords"""
        source = "and class else if while"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        expected_types = [
            TokenType.AND,
            TokenType.CLASS,
            TokenType.ELSE,
            TokenType.IF,
            TokenType.WHILE,
            TokenType.EOF,
        ]

        self.assertEqual(len(tokens), len(expected_types))
        for token, expected_type in zip(tokens, expected_types):
            self.assertEqual(token.token_type, expected_type)

    def test_identifiers(self):
        """Test scanning of identifiers"""
        source = "variable foo bar123"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        self.assertEqual(len(tokens), 4)  # Three identifiers + EOF
        for i in range(3):
            self.assertEqual(tokens[i].token_type, TokenType.IDENTIFIER)


if __name__ == "__main__":
    unittest.main()
