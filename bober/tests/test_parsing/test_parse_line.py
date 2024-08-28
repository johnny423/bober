from bober.src.parsing.line_parser import parse_line


class TestParseLine:
    def test_simple_line(self):
        line = "This is a simple line"
        result = parse_line(line, 0)
        assert result.text == "This is a simple line"
        assert result.indentation == 0
        assert len(result.tokens) == 5
        assert result.tokens[0].word == "this"
        assert result.tokens[0].start == 0

    def test_indented_line(self):
        line = "    Indented line"
        result = parse_line(line, 0)
        assert result.text == "Indented line"
        assert result.indentation == 4
        assert len(result.tokens) == 2

    def test_line_with_punctuation(self):
        line = "Hello, world! How are you?"
        result = parse_line(line, 0)
        assert len(result.tokens) == 5
        assert result.tokens[1].word == "world"
        assert result.tokens[1].start == 7

    def test_line_with_numbers(self):
        line = "There are 3 apples and 2 oranges"
        result = parse_line(line, 0)
        assert len(result.tokens) == 7
        assert result.tokens[2].word == "3"
        assert result.tokens[5].word == "2"

    def test_line_with_multiple_spaces(self):
        line = "Multiple   spaces    between     words"
        result = parse_line(line, 0)
        assert len(result.tokens) == 4
        assert result.tokens[1].start == 11

    def test_line_with_tabs(self):
        line = "\t\tTabbed\tline"
        result = parse_line(line, 0)
        assert result.text == "Tabbed\tline"
        assert result.indentation == 2
        assert len(result.tokens) == 2

    def test_empty_line(self):
        line = ""
        result = parse_line(line, 0)
        assert result.text == ""
        assert result.indentation == 0
        assert len(result.tokens) == 0

    def test_line_with_only_whitespace(self):
        line = "   \t   "
        result = parse_line(line, 0)
        assert result.text == ""
        assert result.indentation == 7
        assert len(result.tokens) == 0

    def test_line_with_special_characters(self):
        line = "Special chars_lala: @#$%^&*()+"
        result = parse_line(line, 0)
        assert len(result.tokens) == 2
        assert result.tokens[0].word == "special"
        assert result.tokens[1].word == "chars_lala"

    def test_line_with_mixed_case(self):
        line = "MixEd CaSe WoRdS"
        result = parse_line(line, 0)
        assert len(result.tokens) == 3
        assert result.tokens[0].word == "mixed"
        assert result.tokens[1].word == "case"
        assert result.tokens[2].word == "words"
