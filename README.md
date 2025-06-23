# Walter

## Presentation
Walter is a command-line tool that generates shell commands using a local LLM (Ollama or compatible). It helps you quickly get the right CLI command for your needs, with context-awareness (current directory, files, OS, etc).

It is similar to [shell-gpt](https://github.com/TheR1D/shell_gpt), but simpler and natively compatible with local LLM using Ollama backend. 

## Installation
We recommend using [pipx](https://pypa.github.io/pipx/) for isolated installation:

```bash
pipx install git+https://github.com/NoLilypad/Walter
```

or

```bash
git clone git@github.com:NoLilypad/Walter.git
cd Walter
pipx install .
```

## Configuration
On first run, Walter creates a configuration file in your user config directory (see [platformdirs](https://pypi.org/project/platformdirs/)).

- To edit the config, run:
  ```bash
  walter config
  ```
- You can set the LLM provider, model, and other options in this file.

## Features
- Generate shell commands from natural language prompts
- Context-aware: takes into account your OS, current directory, and files
- Interactive: edit, refine, or regenerate commands before execution
- Supports local LLMs (Ollama, etc.)
- Easy configuration and extensibility

## Why Walter ?
Walter is very similar to [shell-gpt](https://github.com/TheR1D/shell_gpt) in its use, but much simpler.
One can easily compare the two tools, yet Walter has some advantages : 
- simple and unique use case : generating a command
- easy to configure
- Ollama natively integrated
- edit feature to modify a generated command
- easy to modify custom prompt in the config folder

## Helping

Any suggestion or pull request is welcom ! 