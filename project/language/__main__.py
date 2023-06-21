import sys
from interpreter import interpret
from project.language.FL_utils import parse
from pathlib import Path


def read_file(file: Path) -> str:
    text = file.open()
    return "".join(text.readlines())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Not enough arguments")
    if len(sys.argv) == 2:
        file = Path(sys.argv[1])
        if not file.is_file():
            print("Cannot find file ", file)
        if not file.name.endswith(".flp"):
            print("Invalid file format")
        interpret(parse(read_file(file)))
    if len(sys.argv) > 2:
        program = " ".join(sys.argv[1:]) + ";"
        interpret(parse(program))
