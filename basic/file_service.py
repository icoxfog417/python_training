import os


def read_file(path):
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        lines = [ln.strip(os.linesep) for ln in lines]

    return lines


def write_file(path, rows, separator="\t"):
    with open(path, "wb") as outfile:
        for row in rows:
            line = ""
            if isinstance(row, list) or isinstance(row, tuple):
                line = separator.join(row) + os.linesep
            else:
                line = row + os.linesep
            outfile.write(line.encode("utf-8"))
