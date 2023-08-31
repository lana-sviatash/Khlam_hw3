import argparse
import concurrent.futures
import os
import shutil
from pathlib import Path

from normalize import normalize


parser = argparse.ArgumentParser(description="Sorting files in folder")
parser.add_argument("--source", "-s", required=True, help="Source folder")
parser.add_argument("--output", "-o", default="result", help="Output folder")
args = vars(parser.parse_args())
source = args.get("source")
output_name = args.get("output")
output_folder = Path(output_name)

known_types = {
    "images": ["JPEG", "PNG", "JPG", "SVG"],
    "videos": ["AVI", "MP4", "MOV", "MKV"],
    "documents": ["DOC", "DOCX", "TXT", "PDF", "XLSX", "PPTX"],
    "audio": ["MP3", "OGG", "WAV", "AMR"],
    "archives": ["ZIP", "GZ", "TAR"],
}


def collect_files(directory):
    file_list = []
    directory_path = Path(directory)
    for path in directory_path.rglob("*"):
        if path.is_file():
            file_list.append(path)
    return file_list


def check_file_type(directory):
    global known_types

    file_types = set()
    unknown_types = set()

    files_by_type = {
        "images": [],
        "videos": [],
        "documents": [],
        "audio": [],
        "archives": [],
        "other": [],
    }

    for file_path in collect_files(directory):
        extension = str(file_path).split(".")[-1].upper()

        found = False
        for file_type, extensions in known_types.items():
            if extension in extensions:
                files_by_type[file_type].append(file_path)
                file_types.add(extension)
                found = True
                break

        if not found:
            files_by_type["other"].append(file_path)
            unknown_types.add(extension)

    return files_by_type, file_types, unknown_types


def move_file(file_path, files_by_type):
    global known_types
    normalized_file_name = normalize(os.path.basename(file_path))
    extension = str(file_path).split(".")[-1].upper()

    # Determine the file type folder
    file_type = None
    for type_name, extensions in known_types.items():
        if extension in extensions:
            file_type = type_name
            break

    if file_type is None:
        file_type = "other"

    destination_folder = output_folder / file_type
    destination_path = os.path.join(destination_folder, normalized_file_name)
    shutil.copyfile(file_path, destination_path)


def process_directory(directory):
    files_by_type, _, _ = check_file_type(directory)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for file_type, file_paths in files_by_type.items():
            if file_type == "other":
                continue

            destination_folder = output_folder / file_type
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)

            for file_path in file_paths:
                executor.submit(move_file, file_path, files_by_type)


def print_results(files_by_type, file_types, unknown_types):
    print("\nKnown Extensions: {}".format(", ".join(sorted(file_types))))

    if len(unknown_types) > 0:
        print("Unknown Extensions: {}".format(", ".join(sorted(unknown_types))))
    else:
        print("Unknown Extensions: None\n")


def main():
    if not Path(source).exists():
        return f"Folder with path {source} does not exist. Usage: py sort.py -s <folder_path>"

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for root, dirs, _ in os.walk(source, topdown=True):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                executor.submit(process_directory, dir_path)

    files_by_type, file_types, unknown_types = check_file_type(output_folder)
    print_results(files_by_type, file_types, unknown_types)
    print("Finished")


if __name__ == "__main__":
    main()
