import os
import tarfile
import xml.etree.ElementTree as ET
from tkinter import *
from tkinter.scrolledtext import ScrolledText


class ShellEmulator:
    def __init__(self, config_path):
        self.load_config(config_path)
        self.vfs = self.load_virtual_fs(self.fs_path)
        self.current_dir = self.vfs
        self.log_tree = ET.Element("session")

    def load_config(self, config_path):
        tree = ET.parse(config_path)
        root = tree.getroot()
        self.fs_path = root.find("filesystem").text
        self.log_path = root.find("logfile").text

    def load_virtual_fs(self, fs_path):
        with tarfile.open(fs_path, "r") as tar:
            tar.extractall("C:/Users/gnil/Python project/osPomyatun/virtual_fs")  # временная директория для распаковки
        return "C:/Users/gnil/Python project/osPomyatun/virtual_fs"

    def ls(self):
        contents = os.listdir(self.current_dir)
        return "\n".join(contents)

    def cd(self, path):
        full_path = os.path.join(self.current_dir, path)
        if os.path.isdir(full_path):
            self.current_dir = full_path
            return f"Directory changed to {self.current_dir}"
        else:
            raise FileNotFoundError("Directory not found")

    def tree(self):
        result = []
        for root, dirs, files in os.walk(self.current_dir):
            level = root.replace(self.current_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            result.append(f"{indent}{os.path.basename(root)}/")
            sub_indent = ' ' * 4 * (level + 1)
            for f in files:
                result.append(f"{sub_indent}{f}")
        return "\n".join(result)

    def tac(self, file_path):
        full_path = os.path.join(self.current_dir, file_path)
        with open(full_path, 'r') as f:
            return "\n".join(line.strip() for line in reversed(f.readlines()))  # убираем лишние символы новой строки

    def exit(self, testing=False):
        tree = ET.ElementTree(self.log_tree)
        tree.write(self.log_path)
        if not testing:  # не завершать программу, если это тест
            exit()

    def log_action(self, command, output):
        action = ET.SubElement(self.log_tree, "action")
        cmd = ET.SubElement(action, "command")
        cmd.text = command
        result = ET.SubElement(action, "output")
        result.text = output

    def handle_command(self, command):
        command = command.strip()
        try:
            if command.startswith("ls"):
                output = self.ls()
            elif command.startswith("cd"):
                parts = command.split(" ", 1)
                if len(parts) > 1:
                    path = parts[1]
                    output = self.cd(path)
                else:
                    output = "No path specified for cd command"
            elif command == "tree":
                output = self.tree()
            elif command.startswith("tac"):
                parts = command.split(" ", 1)
                if len(parts) > 1:
                    file_path = parts[1]
                    output = self.tac(file_path)
                else:
                    output = "No file specified for tac command"
            elif command == "exit":
                self.exit()
            else:
                output = "Command not found"
        except Exception as e:
            output = f"Error: {str(e)}"
        self.log_action(command, output)
        return output

class EmulatorGUI:
    def __init__(self, emulator):
        self.emulator = emulator
        self.window = Tk()
        self.window.title("эмулятор командной строки")

        # вводим ScrolledText для вывода результата
        self.text_area = ScrolledText(self.window, wrap=WORD)
        self.text_area.pack(padx=10, pady=10, fill=BOTH, expand=True)

        self.command_entry = Entry(self.window)
        self.command_entry.pack(padx=10, pady=10, fill=X)
        self.command_entry.bind("<Return>", self.on_enter)
        self.command_entry.focus_set()  # устанавливаем фокус на поле ввода

    def on_enter(self, event):
        # обрабатываем ввод команды
        command = self.command_entry.get().strip()
        try:
            result = self.emulator.handle_command(command)
            # добавляем команду и результат в ScrolledText
            self.text_area.insert(END, f"$ {command}\n{result}\n\n")
            # прокручиваем текст вниз к последнему выводу
            self.text_area.see(END)
        except Exception as e:
            print(f"Error: {str(e)}")
            self.text_area.insert(END, f"Error: {str(e)}\n")
        finally:
            self.command_entry.delete(0, END)

    def start(self):
        self.window.mainloop()

if __name__ == "__main__":
    emulator = ShellEmulator("C:/Users/gnil/Python project/osPomyatun/resources/config.xml")
    gui = EmulatorGUI(emulator)
    gui.start()



