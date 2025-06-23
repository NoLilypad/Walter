import sys
import subprocess
import os
import tempfile

from walter.prompt import Prompt
from walter.asker import Asker

class ActionSelector:
    def __init__(self):
        self.actions = {
            '': self.execute,
            'e': self.edit,
            'r': self.regenerate,
            'q': self.quit
        }
        # Dictionary of special actions for the first user input
        self.special_actions = {
            "config": self.open_config,
            "help": self.show_help,
            # Add more actions here if needed
        }

    def select(self, user_input: str):
        user_input = user_input.strip().lower()
        return self.actions.get(user_input, self.refine)

    def handle_special_action(self, user_input: str, **kwargs):
        user_input = user_input.strip().lower()
        action = self.special_actions.get(user_input)
        if action:
            return action(**kwargs)
        return None

    def open_config(self, **kwargs):
        config_path = kwargs.get("config_path")
        editor = os.environ.get("EDITOR", "nano")
        if config_path:
            try:
                subprocess.run([editor, config_path])
            except Exception as e:
                print(f"[Walter] Error opening config: {e}")
                sys.exit(1)
        else:
            print("Config file path not found.")
        sys.exit(0)

    def show_help(self, **kwargs):
        print("Help:\n- config: open the configuration file\n- help: show this help\n- ...")
        sys.exit(0)

    def execute(self, **kwargs):
        prompt: Prompt = kwargs["prompt"]
        command = prompt.get_history()[-1]["content"]
        try:
            subprocess.run(command, shell=True)
        except Exception as e:
            print(f"[Walter] Error executing command: {e}")
            sys.exit(1)
        sys.exit(0)

    def quit(self, **kwargs):
        sys.exit(0)

    def edit(self, **kwargs):
        prompt: Prompt = kwargs["prompt"]
        command = prompt.get_history()[-1]["content"]
        editor = os.environ.get("EDITOR", "nano")
        try:
            with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tf:
                tf.write(command)
                tf.flush()
                tf_name = tf.name
            subprocess.run([editor, tf_name])
            with open(tf_name, "r") as tf:
                new_command = tf.read().strip()
            os.unlink(tf_name)
            if new_command and new_command != command:
                command = new_command
            print(f"Executing: {command}")
            subprocess.run(command, shell=True)
        except Exception as e:
            print(f"[Walter] Error editing or executing command: {e}")
            sys.exit(1)
        sys.exit(0)

    def regenerate(self, **kwargs):
        prompt: Prompt = kwargs["prompt"]
        asker: Asker = kwargs["asker"]
        prompt.add_user_message("Regenerate the last command, correct it to follow the instructions")
        command = asker.provider_function(prompt)
        prompt.add_assistant_message(command)
        return prompt

    def refine(self, **kwargs):
        prompt: Prompt = kwargs["prompt"]
        asker: Asker = kwargs["asker"]
        user_input: str = kwargs["user_input"]
        prompt.add_user_message(f"Refine the command with these user instructions: {user_input}")
        command = asker.provider_function(prompt)
        prompt.add_assistant_message(command)
        return prompt
