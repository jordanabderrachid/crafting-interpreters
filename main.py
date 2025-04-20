from main import hadError
import sys

had_error = False

def error(line: int, message: str):
    global had_error
    had_error = True
    report(line, "", message)

def report(line: int, where: str, message: str):
    global had_error
    had_error = True
    print(f"[line {line}] Error {where}: {message}")

class Token:
    def __init__(self):
        pass

class Scanner:
    def __init__(self, source):
        self.source = source

    def scan_tokens(self) -> list[Token]:
        return []

def run_file(filepath: str):
    global had_error
    with open(filepath, 'rb') as file:
        data = file.read()
        run(data.decode("utf-8"))
        if (had_error):
            sys.exit(65)

def run(script: str):
    scanner = Scanner(script)
    for token in scanner.scan_tokens():
        print(token)

def run_prompt():
    global had_error
    while True:
        print("> ", end="")
        try:
            input_str = input()
        except EOFError:
            print("\n")
            break
        if input_str == "exit" or input_str == "" :
            break
        run(input_str)
        had_error = False

def main():
    args = sys.argv
    if len(args) > 2:
        print("usage: plox [script]")
        sys.exit(64)
    elif len(args) == 2:
        run_file(args[1])
    elif len(args) == 1:
        run_prompt()


if __name__ == "__main__":
     main()
