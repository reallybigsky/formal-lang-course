import pydot

from antlr4 import (
    InputStream,
    CommonTokenStream,
    ParseTreeWalker,
    ParseTreeListener,
    TerminalNode,
    ParserRuleContext,
)

from project.language.dist.FLLexer import FLLexer
from project.language.dist.FLParser import FLParser


def get_parser(prog: str) -> FLParser:
    return FLParser(CommonTokenStream(FLLexer(InputStream(prog))))


class FLProgConverter(ParseTreeListener):
    def __init__(self):
        self._dot = pydot.Dot("FL program")
        self._stack = []
        self._id = 1

    @classmethod
    def convert_to_dot(cls, prog: str) -> pydot.Dot:
        if not is_FL_prog(prog):
            raise ValueError("Given program is not in FL language")
        converter = FLProgConverter()
        parser = get_parser(prog)
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


def is_FL_prog(prog: str) -> bool:
    parser = get_parser(prog)
    parser.removeErrorListeners()
    parser.program()
    return parser.getNumberOfSyntaxErrors() == 0


def FL_prog_to_dot(prog: str) -> pydot.Dot:
    return FLProgConverter.convert_to_dot(prog)


def save_FL_to_file_as_dot(prog: str, path: str):
    dot = FL_prog_to_dot(prog)
    dot.write(path)
