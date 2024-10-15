import argparse
import sys
import os
import shutil
from os.path import split
import re


def init_command(args):
    path = args.root

    if os.path.isfile(path):
        print(f"Error: A file already exists along this path {path}")
        return


    elif os.path.isdir(path):
        file_path = os.path.join(path, '.se')
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                if f.read().strip() == "IT'S SEARCH ENGINE":
                    if args.drop_existing:
                        ind = os.path.join(path, 'index')
                        if os.path.isdir(ind):
                            shutil.rmtree(ind)
                        print("Existing directory has been dropped and reinitialized.")
                        return

                    else:
                        print("No changes will be made")
                        return

        else:
            print(f"Error: Our directory is not located on this path {path}")
            return

    else:
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, '.se'), 'w') as text_file:
            text_file.write("IT'S SEARCH ENGINE")

        os.makedirs(os.path.join(path, 'index'), exist_ok=True)
        files_dir = os.path.join(path, 'files')
        os.makedirs(files_dir, exist_ok=True)

        with open(os.path.join(files_dir, '.splits'), 'w') as splits_file:
            splits_file.write("0 0")

        with open(os.path.join(files_dir, '0_files'), 'w') as files_0:
            pass


def change_text(text):
    def change_word(w):
        w = re.sub(r"[^\w'-]", '', w)
        if w.endswith("'s"):
            w = w[:-2]
        return w.strip()

    lines = text.split('\n')
    change_lines = []

    for line in lines:
        line = re.sub(r'\s*-\s*', '-', line)
        words = line.split()
        changed_words = [change_word(word) for word in words]
        change_lines.append(' '.join(changed_words))

    return '\n'.join(change_lines)



def transform_file(file_path, num):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(os.path.join(os.getcwd(), 'copy_file.txt'), 'w') as copy_file:
        for i, line in enumerate(lines):
            if i != num:
                copy_file.write(line)

            else:
                line_data = line.split()
                line_data[1] = str(int(line_data[1]) + 1)
                copy_file.write(' '.join(line_data) + '\n')

    os.replace('copy_file.txt', file_path)


def add_command(args):
    path = args.root
    file_names = args.file_names
    dir_ind = os.path.join(path, 'index')

    dir_path = os.path.join(path, 'files')
    path0 = os.path.join(dir_path, '0_files')

    files = []
    if os.path.isfile(path0):
        with open(path0, 'r') as f:
            lines = f.readlines()
        files = [l.split()[1].strip() for l in lines]

    splits_path = os.path.join(dir_path, '.splits')
    with open(splits_path, 'r') as f:
        lst_l = f.readlines()
        iden = 1
        for l in lst_l:
            iden += int(l.split()[1])

    index = {}
    for f in file_names:
        new_path = os.path.abspath(f)
        new_path = os.path.normpath(new_path)

        if new_path in files:
            print(f"File {f} is already added.")
            continue

        with open(path0, 'a') as fl:
            fl.write(f"{iden} {new_path}\n")

        with open(new_path, 'r') as file:
            text = file.read().lower()
            text = change_text(text)
            words = text.split()

        for word in words:
            if word not in index:
                index[word] = []
            if iden not in index[word]:
                index[word].append(iden)
        iden += 1

    transform_file(splits_path, 0)
    new_index(index, dir_ind)



def new_index(w_ind, dir_ind):
    index = {}
    for w, iden in w_ind.items():
        ind = ord(w[0]) - ord('a')
        file = f"{ind:02d}"
        if file not in index:
            index[file] = {}

        if w in index[file]:
            index[file][w].update(iden)
        else:
            index[file][w] = set(iden)

    for file_name, words in index.items():
        file_path = os.path.join(dir_ind, file_name)

        data = {}
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                for line in f:
                    word, ids = line.strip().split(": ")
                    data[word] = set(ids.split(','))

        for word, ide in words.items():
            if word in data:
                data[word].update(ide)
            else:
                data[word] = ide

        with open(file_path, 'w') as f:
            for word in sorted(data.keys()):
                f.write(f"{word}: {','.join(sorted(data[word]))}\n")



def main():
    parser = argparse.ArgumentParser(description='Parsing command-line')

    parser.add_argument('--root', help='Need root directory')

    subparsers = parser.add_subparsers(dest='command', required=True, title='commands', help='Input command')

    init_parser = subparsers.add_parser('init', help='init help')
    init_parser.add_argument('--root', required=True, help='Need root directory')
    init_parser.add_argument('--drop-existing', action='store_true', help='Drop existing files')

    info_parser = subparsers.add_parser('info', help='info help')
    info_parser.add_argument('--root', required=True, help='Need root directory')

    add_parser = subparsers.add_parser('add', help='add help')
    add_parser.add_argument('--root', required=True, help='Need root directory')
    add_parser.add_argument('file_names', nargs='+', help='Need a file name')

    find_parser = subparsers.add_parser('find', help='find help')
    find_parser.add_argument('--root', required=True, help='Need root directory')
    find_parser.add_argument('words', nargs='+', help='Input some words')
    find_parser.add_argument('--limit', type=int, help="Input limit")

    args = parser.parse_args()

    # Check if root parameter is provided only once
    if args.root and args.root.count('--root') > 1:
        parser.error("The --root can't be more than once.")

    if args.command not in ["init", 'info', 'add', 'find']:
        parser.error("A command is required.")

    print(f"command: {args.command}")

    if args.command == 'init':
        if args.drop_existing:
            print("drop-existing: True")
        else:
            print("drop-existing: False")

    elif args.command == 'add':
        if args.file_name:
            print(f"file_name: {args.file_name}")

    elif args.command == 'find':
        for i, x in enumerate(args.words):
            print(f"word{i + 1}: {x}")

        limit = args.limit if args.limit is not None else 100
        print(f"limit: {limit}")



main()


