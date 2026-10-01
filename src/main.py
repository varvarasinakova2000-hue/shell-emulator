"""Эмулятор UNIX-оболочки с графическим интерфейсом."""

import argparse
import getpass
import socket
import sys
import tkinter as tk

BG_COLOR = "#1e1e1e"
TEXT_COLOR = "#ffffff"
ACCENT_COLOR = "#fe14ee"
FONT = ("Courier", 12)


def get_user_and_host():
    """Возвращает имя пользователя и имя компьютера из реальной ОС."""
    try:
        username = getpass.getuser()
    except Exception:
        username = "user"
    try:
        hostname = socket.gethostname()
    except Exception:
        hostname = "localhost"
    return username, hostname


def parse_args(argv=None):
    """Разбирает параметры командной строки эмулятора."""
    parser = argparse.ArgumentParser(description="Эмулятор UNIX-оболочки")
    parser.add_argument("--vfs", help="путь к физическому расположению VFS")
    parser.add_argument("--script", help="путь к стартовому скрипту")
    return parser.parse_args(argv)


def read_script(path):
    """Читает стартовый скрипт и возвращает список команд.

    Пустые строки и комментарии (начинаются с #) пропускаются.
    """
    with open(path, encoding="utf-8") as file:
        lines = [line.strip() for line in file]
    return [line for line in lines if line and not line.startswith("#")]


def parse_command(line):
    """Разделяет строку ввода на команду и аргументы по пробелам."""
    tokens = line.split()
    return tokens[0], tokens[1:]


def execute(command, args):
    """Выполняет команду и возвращает текст вывода.

    Для команды exit без аргументов возвращает None — сигнал к выходу.
    """
    if command == "exit":
        if args:
            return "shell-emulator: exit: too many arguments\n"
        return None
    if command in ["ls", "cd"]:
        args_str = " ".join(args) if args else "[нет аргументов]"
        return (
            f"Вызвана заглушка команды: {command}\n"
            f"Переданные аргументы: {args_str}\n"
        )
    return f"shell-emulator: command not found: {command}\n"


class TerminalEmulator:
    """Окно эмулятора: область вывода, поле ввода и кнопка Enter."""

    def __init__(self, root, vfs_path=None, script_path=None):
        """Создаёт окно с заголовком вида Эмулятор - [user@host].

        Если задан стартовый скрипт, он выполняется сразу после запуска.
        """
        self.root = root
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.username, self.hostname = get_user_and_host()

        self.root.title(f"Эмулятор - [{self.username}@{self.hostname}]")
        self.root.geometry("750x450")
        self.root.configure(bg=BG_COLOR)

        self.build_output_area()
        self.build_input_area()

        self.print_to_console(
            "Имитатор UNIX-оболочки загружен.\n"
            f"Система: {sys.platform}\n"
            "Введите 'exit' для выхода.\n\n"
        )
        self.print_settings()
        if script_path:
            # запуск после старта главного цикла, чтобы exit в скрипте
            # корректно закрывал окно
            self.root.after_idle(self.run_script, script_path)

    def build_output_area(self):
        """Создаёт область для отображения команд и их вывода."""
        self.text_area = tk.Text(
            self.root,
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            insertbackground="white",
            font=FONT,
            wrap="word",
        )
        self.text_area.pack(expand=True, fill="both", padx=10, pady=(10, 5))
        self.text_area.bind("<Key>", lambda e: "break")

    def build_input_area(self):
        """Создаёт поле ввода команды и кнопку Enter."""
        bottom_frame = tk.Frame(self.root, bg=BG_COLOR)
        bottom_frame.pack(fill="x", padx=10, pady=(0, 10))
        bottom_frame.columnconfigure(0, weight=1)

        self.entry = tk.Entry(
            bottom_frame,
            bg="#2d2d2d",
            fg=TEXT_COLOR,
            insertbackground="white",
            font=FONT,
            bd=0,
            highlightthickness=1,
            highlightbackground="#555555",
            highlightcolor=ACCENT_COLOR,
        )
        self.entry.grid(row=0, column=0, sticky="ew", ipady=6, padx=(0, 10))
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda event: self.process_command())

        enter_button = tk.Button(
            bottom_frame,
            text="Enter",
            bg="#3a3a3a",
            fg=ACCENT_COLOR,
            activebackground=ACCENT_COLOR,
            activeforeground=BG_COLOR,
            font=("Courier", 11, "bold"),
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.process_command,
        )
        enter_button.grid(row=0, column=1, sticky="ns", ipadx=20)

    def print_to_console(self, text):
        """Добавляет текст в конец области вывода."""
        self.text_area.configure(state="normal")
        self.text_area.insert(tk.END, text)
        self.text_area.configure(state="disabled")
        self.text_area.see(tk.END)

    def print_settings(self):
        """Отладочный вывод параметров, заданных при запуске."""
        self.print_to_console(
            "Параметры запуска:\n"
            f"  VFS: {self.vfs_path or 'не задан'}\n"
            f"  Стартовый скрипт: {self.script_path or 'не задан'}\n\n"
        )

    def run_script(self, path):
        """Выполняет команды стартового скрипта по очереди.

        Ошибочные строки выводят сообщение об ошибке и пропускаются,
        выполнение продолжается со следующей строки.
        """
        try:
            lines = read_script(path)
        except FileNotFoundError:
            self.print_script_error(path, "файл не найден")
            return
        except UnicodeDecodeError:
            self.print_script_error(path, "файл не в кодировке UTF-8")
            return
        except OSError as error:
            self.print_script_error(path, error.strerror)
            return
        for line in lines:
            if not self.run_line(line):
                return

    def print_script_error(self, path, reason):
        """Выводит сообщение о том, что стартовый скрипт не прочитан."""
        self.print_to_console(
            f"shell-emulator: не удалось прочитать скрипт {path}: "
            f"{reason}\n\n"
        )

    def run_line(self, line):
        """Выводит команду с приглашением и выполняет её.

        Возвращает False, если была выполнена команда exit.
        """
        self.print_to_console(f"{self.username}@{self.hostname}:~$ {line}\n")
        if not line:
            return True

        command, args = parse_command(line)
        output = execute(command, args)
        if output is None:
            self.root.destroy()
            return False
        self.print_to_console(output + "\n")
        return True

    def process_command(self):
        """Считывает команду из поля ввода и выполняет её."""
        line = self.entry.get().strip()
        self.entry.delete(0, tk.END)
        self.run_line(line)


if __name__ == "__main__":
    params = parse_args()
    main_window = tk.Tk()
    TerminalEmulator(main_window, params.vfs, params.script)
    main_window.mainloop()
