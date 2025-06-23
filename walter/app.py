import sys
from walter.config import Config
from walter.asker import Asker
from walter.prompt import Prompt
from walter.console_printer import Printer
from walter.action_selector import ActionSelector


def main():
    if len(sys.argv) < 2:
        print("Usage: walter <explain your desired command>")
        sys.exit(1)

    config = Config()
    asker = Asker(config)
    printer = Printer()
    action_selector = ActionSelector()

    user_prompt = " ".join(sys.argv[1:])

    # First user input: special action?
    special_result = action_selector.handle_special_action(user_prompt, config_path=config.config_path)
    if special_result is not None:
        return

    prompt = Prompt(user_prompt, config)
    command = asker.provider_function(prompt)
    prompt.add_assistant_message(command)

    while True:
        command = prompt.get_history()[-1]["content"]
        printer.suggest_command(command)
        user_input = printer.ask_user()
        next_action = action_selector.select(user_input)
        prompt = next_action(prompt=prompt, user_input=user_input, asker=asker)

if __name__ == "__main__":
    main()
