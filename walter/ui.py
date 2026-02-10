"""Modern TUI components using Rich and prompt_toolkit."""
import os
import signal
import subprocess
import sys
from typing import Optional, Callable, Generator

# Lazy imports
_rich_console = None
_rich_panel = None
_rich_text = None
_rich_live = None
_rich_spinner = None
_rich_syntax = None
_rich_table = None
_prompt_toolkit = None


def get_console():
    """Lazy load Rich console."""
    global _rich_console
    if _rich_console is None:
        from rich.console import Console
        _rich_console = Console()
    return _rich_console


def get_panel():
    """Lazy load Rich Panel."""
    global _rich_panel
    if _rich_panel is None:
        from rich.panel import Panel
        _rich_panel = Panel
    return _rich_panel


def get_text():
    """Lazy load Rich Text."""
    global _rich_text
    if _rich_text is None:
        from rich.text import Text
        _rich_text = Text
    return _rich_text


def get_live():
    """Lazy load Rich Live."""
    global _rich_live
    if _rich_live is None:
        from rich.live import Live
        _rich_live = Live
    return _rich_live


def get_spinner():
    """Lazy load Rich Spinner."""
    global _rich_spinner
    if _rich_spinner is None:
        from rich.spinner import Spinner
        _rich_spinner = Spinner
    return _rich_spinner


def get_syntax():
    """Lazy load Rich Syntax."""
    global _rich_syntax
    if _rich_syntax is None:
        from rich.syntax import Syntax
        _rich_syntax = Syntax
    return _rich_syntax


def get_table():
    """Lazy load Rich Table."""
    global _rich_table
    if _rich_table is None:
        from rich.table import Table
        _rich_table = Table
    return _rich_table


class UI:
    """Terminal UI manager."""
    
    def __init__(self):
        self.console = get_console()
        self._interrupted = False
    
    def setup_signals(self):
        """Setup signal handlers for clean interruption."""
        def handler(signum, frame):
            self._interrupted = True
            self.console.print("\n[dim]Interrupted[/dim]")
            sys.exit(0)
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)
    
    def clear(self):
        """Clear terminal."""
        self.console.clear()
    
    def print_header(self, text: str):
        """Print styled header."""
        Text = get_text()
        self.console.print(Text(f"◆ {text}", style="bold cyan"))
    
    def print_command(self, command: str):
        """Display command in styled panel."""
        Panel = get_panel()
        Syntax = get_syntax()
        syntax = Syntax(command, "bash", theme="monokai", word_wrap=True)
        panel = Panel(syntax, title="[bold green]Command[/bold green]", border_style="green", padding=(0, 1))
        self.console.print(panel)
    
    def print_streaming(self, stream: Generator[str, None, None]) -> str:
        """Display streaming response with live update."""
        Live = get_live()
        Text = get_text()
        
        full_response = ""
        text = Text()
        
        with Live(text, console=self.console, refresh_per_second=15, transient=True) as live:
            for chunk in stream:
                if self._interrupted:
                    break
                full_response += chunk
                text = Text(full_response, style="green")
                live.update(text)
        
        return full_response.strip()
    
    def print_thinking(self, message: str = "Thinking"):
        """Show thinking spinner."""
        Spinner = get_spinner()
        return get_live()(Spinner("dots", text=f"[cyan]{message}...[/cyan]"), console=self.console, transient=True)
    
    def print_error(self, message: str):
        """Print error message."""
        self.console.print(f"[bold red]Error:[/bold red] {message}")
    
    def print_success(self, message: str):
        """Print success message."""
        self.console.print(f"[bold green]✓[/bold green] {message}")
    
    def print_info(self, message: str):
        """Print info message."""
        self.console.print(f"[dim]{message}[/dim]")
    
    def print_help(self):
        """Display help information."""
        Table = get_table()
        table = Table(title="Walter Commands", show_header=True, header_style="bold cyan")
        table.add_column("Key", style="green")
        table.add_column("Action")
        table.add_row("Enter", "Execute command")
        table.add_row("e", "Edit command before executing")
        table.add_row("r", "Regenerate command")
        table.add_row("c", "Copy to clipboard")
        table.add_row("h", "Show history")
        table.add_row("q", "Quit")
        table.add_row("text", "Refine with instructions")
        self.console.print(table)
        self.console.print()
        self.console.print("[dim]Special commands: walter config | walter help | walter history[/dim]")
    
    def print_history(self, entries: list[dict]):
        """Display history entries."""
        Table = get_table()
        table = Table(title="Recent History", show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Prompt", max_width=40)
        table.add_column("Command", style="green", max_width=50)
        table.add_column("Executed", width=8)
        
        for i, entry in enumerate(entries[:20], 1):
            executed = "✓" if entry.get("executed") else ""
            prompt = entry.get("prompt", "")[:40]
            command = entry.get("command", "")[:50]
            table.add_row(str(i), prompt, command, executed)
        
        self.console.print(table)
    
    def prompt(self, message: str = ">> ") -> str:
        """Get user input with prompt."""
        try:
            from prompt_toolkit import prompt as pt_prompt
            from prompt_toolkit.styles import Style
            style = Style.from_dict({'': '#00aa00'})
            return pt_prompt(message, style=style).strip()
        except (ImportError, EOFError, KeyboardInterrupt):
            # Fallback to basic input
            try:
                return input(message).strip()
            except (EOFError, KeyboardInterrupt):
                return "q"
    
    def prompt_action(self) -> str:
        """Prompt for action with hints."""
        self.console.print("[dim]Enter=run, e=edit, r=regenerate, c=copy, q=quit, or refine:[/dim]")
        return self.prompt("❯ ")
    
    def edit_command(self, command: str, editor: str = "nano") -> str:
        """Open command in editor and return edited version."""
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".sh", delete=False) as tf:
            tf.write(command)
            tf.flush()
            tf_name = tf.name
        
        try:
            subprocess.run([editor, tf_name])
            with open(tf_name, "r") as f:
                return f.read().strip()
        finally:
            os.unlink(tf_name)
    
    def execute_command(self, command: str) -> int:
        """Execute command and return exit code."""
        self.console.print()
        self.print_info(f"Executing: {command}")
        self.console.print()
        
        try:
            result = subprocess.run(command, shell=True)
            return result.returncode
        except KeyboardInterrupt:
            self.console.print("\n[dim]Command interrupted[/dim]")
            return 130
    
    def copy_to_clipboard(self, text: str) -> bool:
        """Copy text to clipboard."""
        try:
            # Try xclip first (Linux)
            subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            try:
                # Try xsel
                subprocess.run(["xsel", "--clipboard", "--input"], input=text.encode(), check=True)
                return True
            except (FileNotFoundError, subprocess.CalledProcessError):
                try:
                    # Try wl-copy (Wayland)
                    subprocess.run(["wl-copy"], input=text.encode(), check=True)
                    return True
                except (FileNotFoundError, subprocess.CalledProcessError):
                    return False
