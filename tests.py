import unittest
import os
import xml.etree.ElementTree as ET
from emulator import ShellEmulator  # импортируем класс эмулятора


class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        # указываем путь к config.xml
        self.emulator = ShellEmulator("C:/Users/gnil/Python project/osPomyatun/resources/config.xml")
        # устанавливаем начальную директорию в корень виртуальной файловой системы
        self.emulator.current_dir = self.emulator.vfs

    def test_ls(self):
        output = self.emulator.ls()
        self.assertIsInstance(output, str)  # проверяем, что вывод строка
        self.assertTrue(output)  # вывод не должен быть пустым

    def test_cd(self):
        # создадим тестовую директорию
        test_dir = os.path.join(self.emulator.vfs, "subdir")
        os.makedirs(test_dir, exist_ok=True)  # создаем директорию
        self.emulator.cd("subdir")  # переход в директорию
        self.assertEqual(self.emulator.current_dir, test_dir)  # текущая директория должна обновиться

    def test_tree(self):
        # создаем структуру каталогов для тестирования
        test_dir = os.path.join(self.emulator.vfs, "subdir")
        os.makedirs(test_dir, exist_ok=True)
        output = self.emulator.tree()
        self.assertIn("subdir/", output)  # проверяем, что директория отображается в дереве

    def test_tac(self):
        test_file_path = os.path.join(self.emulator.vfs, "testfile.txt")
        with open(test_file_path, 'w') as f:
            f.write("Line1\nLine2\nLine3")

        output = self.emulator.tac("testfile.txt")
        self.assertEqual(output, "Line3\nLine2\nLine1")  # строки должны выводиться в обратном порядке

    def test_exit(self):
        self.emulator.log_action("ls", "testfile.txt\nsubdir")
        self.emulator.exit(testing=True)

        # проверяем, что лог-файл был записан
        log_tree = ET.parse(self.emulator.log_path)
        root = log_tree.getroot()
        last_action = root.find("action")
        self.assertIsNotNone(last_action)  # должно быть записано хотя бы одно действие
        self.assertEqual(last_action.find("command").text, "ls")  # проверяем, что команда записана
        self.assertEqual(last_action.find("output").text, "testfile.txt\nsubdir")  # проверяем результат команды

if __name__ == '__main__':
    unittest.main()
