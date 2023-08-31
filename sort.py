import argparse
import os
import shutil
from pathlib import Path
from threading import Semaphore, Thread

from normalize import normalize

parser = argparse.ArgumentParser(description="Sorting files in folder")
parser.add_argument("--source", "-s", required=True, help="Source folder")
parser.add_argument("--output", "-o", default="result", help="Output folder")
args = vars(parser.parse_args())
source = args.get("source")
output_name = args.get("output")
output_folder = Path(output_name)

def collect_files(directory: Path):
    file_list = []
    for path in directory.rglob('*'):
        if path.is_file():
            file_list.append(path)
    return file_list

def check_file_type(directory):
    known_types = {
        'images': ['JPEG', 'PNG', 'JPG', 'SVG'],
        'videos': ['AVI', 'MP4', 'MOV', 'MKV'],
        'documents': ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'],
        'audio': ['MP3', 'OGG', 'WAV', 'AMR'],
        'archives': ['ZIP', 'GZ', 'TAR']
    }

    file_types = set()
    unknown_types = set()

    files_by_type = {
        'images': [],
        'videos': [],
        'documents': [],
        'audio': [],
        'archives': [],
        'other': []
    }

    for file_path in collect_files(directory):
        extension = str(file_path).split('.')[-1].upper()

        found = False
        for file_type, extensions in known_types.items():
            if extension in extensions:
                files_by_type[file_type].append(file_path)
                file_types.add(extension)
                found = True
                break
        
        if not found:
            files_by_type['other'].append(file_path)
            unknown_types.add(extension)
    
    return files_by_type, file_types, unknown_types

def move_to_folder(directory, semaphore):
    with semaphore:
        files_by_type, _, _ = check_file_type(directory)

        for file_type, file_list in files_by_type.items():
            new_folders_path = os.path.join(directory, file_type)
            os.makedirs(new_folders_path, exist_ok=True)

            for file_path in file_list:
                normalized_file_name = normalize(os.path.basename(file_path))
                destination_path = os.path.join(new_folders_path, normalized_file_name)
                shutil.move(file_path, destination_path)

        for root, dirs, _ in os.walk(directory, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)

def print_results(files_by_type, file_types, unknown_types):
    print("{:<10} | {}".format("File Type", "File Name"))
    print("-" * 50)
    
    for file_type, file_list in files_by_type.items():
        file_names = set(normalize(os.path.basename(name)) for name in file_list)
        if len(file_list) > 0: 
            print("{:<10} | {}".format(file_type, (", ".join(sorted(name for name in file_names)))))
    
    print("\nKnown Extensions: {}".format(", ".join(sorted(file_types))))
    
    if len(unknown_types) > 0:
        print("Unknown Extensions: {}".format(", ".join(sorted(unknown_types))))
    else:
        print("Unknown Extensions: None\n")

        
def main():
    if not Path(source).exists():
        return f'Folder with path {source} does not exist. Usage: py sort.py -s <folder_path>'
    
    semaphore = Semaphore(8)

    threads = []
    for file_path in collect_files(Path(source)):
        thread = Thread(target=move_to_folder, args=(file_path, semaphore))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    files_by_type, file_types, unknown_types = check_file_type(Path(source))
    print_results(files_by_type, file_types, unknown_types)

if __name__ == '__main__':
    main()
