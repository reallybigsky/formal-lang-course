from enum import Enum

import pydot

from antlr4 import *
from project.language.dist.FLLexer import FLLexer
from project.language.dist.FLParser import FLParser


class FLValueType(Enum):
    StringValue = 1
    IntValue = 2
    SetValue = 3
    FiniteAutomataValue = 4
    BoolValue = 5


class FLValueHolder:
    def __init__(self, value, ctx, value_type=FLValueType.StringValue):
        self.value = value
        self.ctx = ctx
        self.value_type = value_type

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, FLValueHolder):
            return self.value_type == other.value_type and self.value == other.value
        else:
            return False


class InputType(Enum):
    TEXT = 1
    FILE = 2
    STDIN = 3


def build_parser(stream: InputStream) -> FLParser:
    """
    Create FLParser program from input stream
    :param stream: source stream
    :return: FLParser
    """
    lexer = FLLexer(stream)
    lexer.removeErrorListeners()
    stream = CommonTokenStream(lexer)
    return FLParser(stream)


def parse_stream(stream: InputStream, rule_name: str = "program"):
    """
    Parse input stream with given rule as FL program
    """
    parser = build_parser(stream)
    parser.removeErrorListeners()
    fun = getattr(parser, rule_name)
    result = fun()
    return result


def parse(
    input_string: str = None,
    rule_name: str = "program",
    input_type: InputType = InputType.TEXT,
    encoding: str = "utf-8",
):
    """
    Parse input string depending on the provided input type
    """
    if input_type is InputType.TEXT:
        stream = InputStream(input_string)
    elif input_type is InputType.FILE:
        stream = FileStream(input_string, encoding=encoding)
    else:
        stream = StdinStream(encoding=encoding)

    return parse_stream(stream, rule_name)


class FLProgConverter(ParseTreeListener):
    def __init__(self):
        self._dot = pydot.Dot("FL program")
        self._stack = []
        self._id = 1

    @classmethod
    def convert_to_dot(cls, program: str) -> pydot.Dot:
        if not is_valid_program(program):
            raise ValueError("Given program is not FL program")
        converter = FLProgConverter()
        parser = build_parser(InputStream(program))
        walker = ParseTreeWalker()
        walker.walk(converter, parser.program())
        return converter._dot

    def visitTerminal(self, node: TerminalNode):
        label = str(node).strip('"')
        label = f'"{label}"'
        new_node = pydot.Node(self._id, label=label)
        self._dot.add_node(new_node)
        self._try_connect_with_parent(new_node)
        self._id += 1

    def enterEveryRule(self, ctx: ParserRuleContext):
        new_node = pydot.Node(
            self._id, label=f"Rule[{FLParser.ruleNames[ctx.getRuleIndex()]}]"
        )
        self._dot.add_node(new_node)
        self._try_connect_with_parent(new_node)
        self._stack.append(new_node)
        self._id += 1

    def exitEveryRule(self, ctx: ParserRuleContext):
        self._stack.pop()

    def _try_connect_with_parent(self, new_node):
        if len(self._stack) > 0:
            parent = self._stack[-1]
            self._dot.add_edge(pydot.Edge(parent.get_name(), new_node.get_name()))


def is_valid_program(program: str) -> bool:
    parser = build_parser(InputStream(program))
    parser.removeErrorListeners()
    parser.program()
    return parser.getNumberOfSyntaxErrors() == 0


def program_to_dot(prog: str) -> pydot.Dot:
    return FLProgConverter.convert_to_dot(prog)


def save_FL_to_file_as_dot(prog: str, path: str):
    dot = program_to_dot(prog)
    dot.write(path)
