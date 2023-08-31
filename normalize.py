def normalize(name):
    translit_table = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e', 'є': 'ie', 'ж': 'zh', 'з': 'z',
        'и': 'y', 'і': 'i', 'ї': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
        'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ь': '', 'ю': 'iu', 'я': 'ia', 'ы': 'y', 'ъ': '', 'э': 'e', 'ё': 'io', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'H',
        'Ґ': 'G', 'Д': 'D', 'Е': 'E', 'Є': 'Ye', 'Ж': 'Zh', 'З': 'Z', 'И': 'Y', 'І': 'I', 'Ї': 'Yi', 'Й': 'Y', 'К': 'K',
        'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh',
        'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch', 'Ь': '', 'Ю': 'Yu', 'Я': 'Ya', 'Ы': 'Y', 'Ъ': '', 'Э': 'E',
        'Ё': 'Io'
    }

    normalized_name = ''
    for char in name:
        if char in translit_table:
            normalized_name += translit_table[char]
        elif char.isalnum() and char.isascii() or char == '.':
            normalized_name += char
        else:
            normalized_name += '_'

    return normalized_name





import argparse
import sys
import os
from pathlib import Path
from shutil import copyfile
from threading import Pool, cpu_count
import logging

# from normalize import normalize


parser = argparse.ArgumentParser(description="Sorting files in folder")
parser.add_argument("--source", "-s", required=True, help="Source folder")
parser.add_argument("--output", "-o", default="result", help="Output folder")
args = vars(parser.parse_args())
source = args.get("source")
output_name = args.get("output")
output_folder = Path(output_name)
folders = []

def collect_folders_path(directory: Path) -> None:
    # folders = []
    for el in directory:
        if el.is_dir():
            folders.append(el)
            res = collect_folders_path(el)
            if len(res):
                folders = folders + res
        else:
            pass
    return folders


def copy_file(file: Path) -> None:
    for el in dir.iterdir():
        if el.is_file():
            ext = file.suffix
            new_path = output_folder / ext
            new_path.mkdir(exist_ok=True, parents=True)
            copyfile(el, new_path / el.name)

if __name__ == "__main__":
    with Pool(cpu_count()) as pool:
        pool.map(copy_file, collect_folders_path(Path(source)))
        pool.close()
        pool.join()
    print("Finished")

