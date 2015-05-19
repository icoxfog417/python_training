import sys
import os
from collections import Counter
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from basic import file_service as fs


def count_lines(file_path):
    """
    assignment1: count lines in file
    :param file_path:
    :return:
    """
    lines = fs.read_file(file_path)
    return len(lines)


def tab_to_space(file_path):
    """
    assignment2: replace the tab to space
    :param file_path:
    :return:
    """
    lines = fs.read_file(file_path)
    replaced = [ln.replace("\t", " ") for ln in lines]
    return replaced


def split_columns(file_path, separator="\t"):
    """
    split file vertically by separator
    :param file_path:
    :return:
    """
    lines = fs.read_file(file_path)
    splitted = [ln.split(separator) for ln in lines]
    columns = zip(*splitted)

    return columns


def columns_to_file(file_path, target_dir):
    """
    assignment3: split columns and save these to file
    :param file_path:
    :param target_dir:
    :return: file_names
    """
    columns = split_columns(file_path)
    file_names = []
    for i, c in enumerate(columns):
        fn = "col{0}.txt".format(i + 1)
        path = os.path.join(target_dir, fn)
        fs.write_file(path, c)
        file_names.append(fn)

    return file_names


def merge_column_files(file_paths):
    """
    assignment4: merge column files
    :param file_paths:
    :return: file_names
    """

    columns = []
    for p in file_paths:
        c = fs.read_file(p)
        columns.append(c)

    rows = zip(*columns)
    lines = []
    for i, r in enumerate(rows):
        lines.append("\t".join(r))

    return lines


def __show_partial_lines(file_path, limit, cut_method):
    """
    show partial lines of file
    :param file_path:
    :param limit:
    :param cut_method:
    :return:
    """

    lines = fs.read_file(file_path)
    if limit > len(lines):
        raise Exception("Index out of bound. {0} is greater than lines in file ({1} lines)".format(limit, len(lines)))
    for ln in cut_method(lines, limit):
        print(ln)


def show_head(file_path, limit):
    """
    assignment5: show head n lines
    :param file_path:
    :param limit:
    :return:
    """
    cut_head = lambda lines, c: lines[:c]
    __show_partial_lines(file_path, limit, cut_head)


def show_tail(file_path, limit):
    """
    assignment6: show head n lines
    :param file_path:
    :param limit:
    :return:
    """
    cut_tail = lambda lines, c: lines[-c:]
    __show_partial_lines(file_path, limit, cut_tail)


def __show_aggregation(column, limit):
    """
    aggregate rows
    :param column:
    :param limit:
    :return:
    """
    counter = Counter()
    for r in column:
        counter[r] += 1

    for rank in counter.most_common(limit):
        print("{0}\t:{1}".format(*rank))


def show_first_column_aggregation(file_path, limit):
    """
    assignment7: aggregate first column
    :param file_path:
    :return:
    """
    first_column = next(split_columns(file_path))
    __show_aggregation(first_column, limit)


def sort_lines(file_path, order_indexes=(0,), separator="\t"):
    """
    assignment8/9: order the file lines by aggregate first column
    :param file_path:
    :param orders:
    :return:
    """
    lines = fs.read_file(file_path)
    rows = [ln.split(separator) for ln in lines]

    sorted_rows = sorted(rows, key=lambda r: "__".join([r[i] for i in order_indexes]))
    sorted_lines = [separator.join(r) for r in sorted_rows]

    return sorted_lines


def show_aggregation(file_path, limit):
    """
    assignment10: aggregate from file
    :param file_path:
    :return:
    """
    lines = fs.read_file(file_path)
    __show_aggregation(lines, limit)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="show partial lines of file")
    parser.add_argument("file", type=str, nargs=1, help="file path")
    parser.add_argument("limit", type=int, nargs=1, help="display limit of lines")
    parser.add_argument('--part', default="h", help="set head(h) or tail(t)")
    args = parser.parse_args()

    show_func = None
    if args.part == "h":
        show_func = show_head
    else:
        show_func = show_tail

    show_func(args.file[0], args.limit[0])
