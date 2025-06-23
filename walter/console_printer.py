import termcolor

class Printer:
    def __init__(self):
        pass

    def suggest_command(self, command: str):
        print(f"Command: {termcolor.colored(command, 'green')}")

    def ask_user(self) -> str:
        return input(">> ").strip()
    
    def print_possible_instructions(self):
        print("[Enter] to execute, [e]dit, [r]egenerate, [q]uit, refine instruction")