import argparse
from pathlib import Path
from shutil import copyfile
from threading import Thread, Semaphore
from concurrent.futures import ThreadPoolExecutor

parser = argparse.ArgumentParser(description="Sorting files in folder")
parser.add_argument("--source", "-s", required=True, help="Source folder")
parser.add_argument("--output", "-o", default="result", help="Output folder")
args = vars(parser.parse_args())
source = args.get("source")
output_name = args.get("output")
output_folder = Path(output_name)


def collect_folders_path(directory: Path) -> list:
    folders = []
    for el in directory.iterdir():
        if el.is_dir():
            folders.append(el)
            res = collect_folders_path(el)
            if len(res):
                folders = folders + res
    return folders


def copy_file(file: Path, semaphore: Semaphore) -> None:
    with semaphore:
        for el in file.parent.iterdir():
            if el.is_file():
                ext = el.suffix
                new_path = output_folder / ext
                new_path.mkdir(exist_ok=True, parents=True)
                copyfile(el, new_path / el.name)


if __name__ == "__main__":
    thread_count = 8
    semaphore = Semaphore(thread_count)

    files_to_copy = collect_folders_path(Path(source))

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        for file in files_to_copy:
            executor.submit(copy_file, file, semaphore)

    print("Finished")
