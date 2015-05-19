import os
import unittest
from basic import file_service as fs
from basic import python_basic as pyb


class TestPythonBasic(unittest.TestCase):
    FILE_PATH = os.path.join(os.path.dirname(__file__), "../../data/address.txt")
    OUT_DIR = os.path.dirname(__file__)
    DISPLAY_LIMIT = 10

    def test_assignment1(self):
        line_count = pyb.count_lines(self.FILE_PATH)
        file_name = os.path.basename(self.FILE_PATH)
        print("1. line count of {0} is {1}".format(file_name, line_count))

    def test_assignment2(self):
        __file_name = "2_tab_to_space.txt"
        __file_path = os.path.join(self.OUT_DIR, __file_name)

        replaced = pyb.tab_to_space(self.FILE_PATH)
        fs.write_file(__file_path, replaced)

        # confirmation
        replaced_file = fs.read_file(__file_path)
        self.assertTrue(sum(["\t" in ln for ln in replaced_file]) == 0)
        print("2. replaced tab to space")

    def test_assignment3_4(self):
        file_names = pyb.columns_to_file(self.FILE_PATH, self.OUT_DIR)
        file_paths = [os.path.join(self.OUT_DIR, fn) for fn in file_names]
        print("3. split columns and save these to file")

        # confirmation (compare with original file)
        original = fs.read_file(self.FILE_PATH)
        restored = pyb.merge_column_files(file_paths)

        self.assertEqual(len(original), len(restored))
        for i, t in enumerate(original):
            self.assertEqual(t, restored[i])

        print("4. merge column files")

    def test_assignment5(self):
        print("5. show head n lines")
        pyb.show_head(self.FILE_PATH, self.DISPLAY_LIMIT)

    def test_assignment6(self):
        print("6. show tail n lines")
        pyb.show_tail(self.FILE_PATH, self.DISPLAY_LIMIT)

    def test_assignment7(self):
        print("7.aggregate first column")
        pyb.show_first_column_aggregation(self.FILE_PATH, self.DISPLAY_LIMIT)

    def test_assignment8(self):
        order_by_first = pyb.sort_lines(self.FILE_PATH)
        print("8. order by first columns")
        for ln in order_by_first[:self.DISPLAY_LIMIT]:
            print(ln)

    def test_assignment9(self):
        order_by_second_and_first = pyb.sort_lines(self.FILE_PATH, order_indexes=(1, 0))
        print("9. order by second and first")
        for ln in order_by_second_and_first[:self.DISPLAY_LIMIT]:
            print(ln)

    def test_assignment10(self):
        target_file = os.path.join(self.OUT_DIR, "col2.txt")
        if os.path.isfile(target_file):
            print("10. aggregate col2.txt")
            pyb.show_aggregation(target_file, self.DISPLAY_LIMIT)
        else:
            print("col2.txt is not exist")
