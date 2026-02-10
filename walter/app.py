"""Walter 2.0 - Main application with modern TUI."""
import os
import sys
import subprocess
from typing import Optional

from walter.config import Config
from walter.history import History
from walter.ui import UI
from walter.providers import get_provider


class Walter:
    """Main Walter application."""
    
    def __init__(self):
        self.config = Config()
        self.history = History()
        self.ui = UI()
        self.ui.setup_signals()
        self._provider = None
        self._messages: list[dict] = []
        self._current_command: str = ""
        self._user_prompt: str = ""
    
    @property
    def provider(self):
        """Lazy load provider."""
        if self._provider is None:
            self._provider = get_provider(self.config.provider, self.config.config)
        return self._provider
    
    def run(self, args: list[str]):
        """Main entry point."""
        if not args:
            self.ui.print_help()
            return
        
        user_input = " ".join(args)
        
        # Handle special commands
        if self._handle_special_command(user_input):
            return
        
        # Normal flow: generate and interact
        self._user_prompt = user_input
        self._generate_command()
        self._interaction_loop()
    
    def _handle_special_command(self, cmd: str) -> bool:
        """Handle special commands. Returns True if handled."""
        cmd_lower = cmd.strip().lower()
        
        if cmd_lower == "config":
            self._open_config()
            return True
        elif cmd_lower == "help":
            self.ui.print_help()
            return True
        elif cmd_lower == "history":
            entries = self.history.get_recent(20)
            if entries:
                self.ui.print_history(entries)
            else:
                self.ui.print_info("No history yet.")
            return True
        elif cmd_lower == "clear-history":
            self.history.clear()
            self.ui.print_success("History cleared.")
            return True
        
        return False
    
    def _open_config(self):
        """Open config file in editor."""
        editor = self.config.editor
        try:
            subprocess.run([editor, self.config.config_path])
        except Exception as e:
            self.ui.print_error(f"Could not open config: {e}")
    
    def _generate_command(self):
        """Generate command from user prompt."""
        # Build messages
        system_prompt = self.config.build_prompt(self._user_prompt)
        self._messages = [{"role": "user", "content": system_prompt}]
        
        # Generate with streaming or not
        try:
            if self.config.stream:
                with self.ui.print_thinking():
                    pass  # Just flash the spinner
                stream = self.provider.stream(self._messages)
                self._current_command = self.ui.print_streaming(stream)
            else:
                with self.ui.print_thinking():
                    self._current_command = self.provider.ask(self._messages)
            
            # Clean command (remove markdown code blocks if any)
            self._current_command = self._clean_command(self._current_command)
            
            # Display command
            self.ui.print_command(self._current_command)
            
            # Add to history
            self.history.add(
                prompt=self._user_prompt,
                command=self._current_command,
                provider=self.config.provider
            )
            
            # Update messages
            self._messages.append({"role": "assistant", "content": self._current_command})
            
        except Exception as e:
            self.ui.print_error(f"Provider error: {e}")
            sys.exit(1)
    
    def _clean_command(self, cmd: str) -> str:
        """Clean command from markdown formatting."""
        cmd = cmd.strip()
        # Remove markdown code blocks
        if cmd.startswith("```"):
            lines = cmd.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            cmd = "\n".join(lines).strip()
        return cmd
    
    def _interaction_loop(self):
        """Main interaction loop for command actions."""
        while True:
            action = self.ui.prompt_action()
            
            if action == "" or action == "y":
                # Execute
                self.ui.execute_command(self._current_command)
                self.history.mark_executed(self._current_command)
                break
            
            elif action == "q":
                # Quit
                break
            
            elif action == "e":
                # Edit
                edited = self.ui.edit_command(self._current_command, self.config.editor)
                if edited and edited != self._current_command:
                    self._current_command = edited
                    self.ui.print_command(self._current_command)
                # Execute edited command
                self.ui.execute_command(self._current_command)
                self.history.mark_executed(self._current_command)
                break
            
            elif action == "r":
                # Regenerate
                self._messages.append({
                    "role": "user",
                    "content": "Regenerate the command. Provide a different approach if possible."
                })
                self._regenerate()
            
            elif action == "c":
                # Copy to clipboard
                if self.ui.copy_to_clipboard(self._current_command):
                    self.ui.print_success("Copied to clipboard")
                else:
                    self.ui.print_error("Could not copy (install xclip, xsel, or wl-copy)")
            
            elif action == "h":
                # Show history
                entries = self.history.get_recent(10)
                self.ui.print_history(entries)
            
            else:
                # Refine with user input
                self._messages.append({
                    "role": "user",
                    "content": f"Modify the command based on: {action}"
                })
                self._regenerate()
    
    def _regenerate(self):
        """Regenerate command based on current messages."""
        try:
            if self.config.stream:
                stream = self.provider.stream(self._messages)
                self._current_command = self.ui.print_streaming(stream)
            else:
                with self.ui.print_thinking():
                    self._current_command = self.provider.ask(self._messages)
            
            self._current_command = self._clean_command(self._current_command)
            self.ui.print_command(self._current_command)
            self._messages.append({"role": "assistant", "content": self._current_command})
            
            # Update history
            self.history.add(
                prompt=self._user_prompt,
                command=self._current_command,
                provider=self.config.provider
            )
            
        except Exception as e:
            self.ui.print_error(f"Provider error: {e}")


def main():
    """Entry point."""
    app = Walter()
    app.run(sys.argv[1:])


if __name__ == "__main__":
    main()
