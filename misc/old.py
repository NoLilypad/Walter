import os
import sys
import requests
import subprocess
import tempfile
import termcolor

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"

def get_system_info():
    os_name = os.uname().sysname
    cwd = os.getcwd()
    files = os.listdir(cwd)
    return os_name, cwd, files

def ask_ollama(prompt, history=None):
    data = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
    }
    if history:
        data["context"] = history
    response = requests.post(OLLAMA_URL, json=data)
    response.raise_for_status()
    return response.json()["response"].strip()

def main():
    if len(sys.argv) < 2:
        print("Usage: walter <votre question en langage naturel>")
        sys.exit(1)

    user_prompt = " ".join(sys.argv[1:])
    history = None

    while True:
        os_name, cwd, files = get_system_info()
        # print(f"\nOS: {os_name}\nDossier courant: {cwd}\nContenu: {', '.join(files)}")
        # print(f"Instruction utilisateur: {user_prompt}")

        prompt = f"You are an AI agent that generates CLI commands. Based in this user demand :  {user_prompt} generate a working CLI command in bash. Not formatting, no markdown, explanation or question, the command should run natively. If multiple commands are needed, make it a one-liner with ;. The command should be the simplest possible. Additional data if needed: OS Name = {os_name}, current directory = {cwd}, files in current directory : {', '.join(files)}"
        command = ask_ollama(prompt, history)
        if not command:
            print("Impossible de générer une commande. Veuillez vérifier Ollama ou réessayer.")
            break
        print(f"\nSuggested command : " + termcolor.colored(command, "green"))

        action = input("[Enter] to execute, [e] to edit, [r] to regenerate, [q] to quit, or type again to give more instructions\n> ").strip()

        if action == "":
            print(f"Exécution : {command}")
            subprocess.run(command, shell=True)
            break
        elif action.lower() == "e":
            editor = os.environ.get("EDITOR", "nano")
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
            print(f"Exécution : {command}")
            subprocess.run(command, shell=True)
            break
        elif action.lower() == "r":
            history = None  # On peut améliorer l'historique plus tard
            continue
        elif action.lower() == "q":
            print("Bye!")
            break
        else:
            user_prompt = action
            history = None  # On peut améliorer l'historique plus tard

if __name__ == "__main__":
    main()
