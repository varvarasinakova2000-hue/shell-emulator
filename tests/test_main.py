"""Тесты парсера и команд эмулятора."""

import contextlib
import io
import os
import tempfile
import unittest

from src.main import execute, parse_args, parse_command, read_script


class TestArgs(unittest.TestCase):
    """Проверка параметров командной строки."""

    def test_no_params(self):
        """Без параметров оба значения не заданы."""
        params = parse_args([])
        self.assertIsNone(params.vfs)
        self.assertIsNone(params.script)

    def test_all_params(self):
        """Путь к VFS и к стартовому скрипту."""
        params = parse_args(["--vfs", "my_vfs", "--script", "start.txt"])
        self.assertEqual(params.vfs, "my_vfs")
        self.assertEqual(params.script, "start.txt")

    def test_unknown_param(self):
        """Неизвестный параметр — ошибка argparse."""
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit):
                parse_args(["--unknown", "x"])
        self.assertIn("unrecognized arguments: --unknown x", stderr.getvalue())


class TestScript(unittest.TestCase):
    """Проверка чтения стартового скрипта."""

    def test_skips_comments_and_empty_lines(self):
        """Комментарии и пустые строки не попадают в список команд."""
        with tempfile.NamedTemporaryFile(
            "w", suffix=".txt", delete=False, encoding="utf-8"
        ) as file:
            file.write("# комментарий\nls -l\n\n  cd /home  \n")
        try:
            self.assertEqual(read_script(file.name), ["ls -l", "cd /home"])
        finally:
            os.remove(file.name)

    def test_missing_script(self):
        """Несуществующий скрипт — ошибка OSError."""
        with self.assertRaises(OSError):
            read_script("not_found.txt")


class TestParser(unittest.TestCase):
    """Проверка разделения ввода на команду и аргументы."""

    def test_command_without_args(self):
        """Команда без аргументов."""
        self.assertEqual(parse_command("ls"), ("ls", []))

    def test_command_with_args(self):
        """Аргументы разделяются по пробелам, лишние пробелы игнорируются."""
        self.assertEqual(
            parse_command("cd   /home  user"), ("cd", ["/home", "user"])
        )


class TestCommands(unittest.TestCase):
    """Проверка команд-заглушек, exit и обработки ошибок."""

    def test_stub_prints_name_and_args(self):
        """Заглушка выводит своё имя и аргументы."""
        output = execute("ls", ["-l", "/home"])
        self.assertIn("ls", output)
        self.assertIn("-l /home", output)

    def test_stub_without_args(self):
        """Заглушка без аргументов."""
        self.assertIn("[нет аргументов]", execute("cd", []))

    def test_unknown_command(self):
        """Неизвестная команда — ошибка command not found."""
        self.assertIn("command not found: foo", execute("foo", []))

    def test_exit(self):
        """exit без аргументов — сигнал к выходу."""
        self.assertIsNone(execute("exit", []))

    def test_exit_with_args(self):
        """exit с аргументами — ошибка."""
        self.assertIn("too many arguments", execute("exit", ["1"]))


if __name__ == "__main__":
    unittest.main()
