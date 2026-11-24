from pathlib import Path
from typing import Any


def file_organizer(files: list[Any]) -> dict[str, str]:
    stringafied = [str(file) for file in files]
    result = {}

    for file in stringafied:
        with open(file, 'r', encoding='utf-8') as text:
            temp = text.read()
        result[file] = temp

    return result


def ingest() -> dict[str, Any]:
    results = {}
    source: Path = Path('./data/raw/')
    md_files = list(source.glob('**/*.md'))
    py_files = list(source.glob('**/*.py'))
    txt_files = list(source.glob('**/*.txt'))

    results['md'] = file_organizer(md_files)
    results['py'] = file_organizer(py_files)
    results['txt'] = file_organizer(txt_files)

    for file_type in results:
        temp = {location: content[:25] for location, content in results[file_type].items()}
        for file in temp:
            print(file, " - ", temp[file][:10])


def main() -> None:
    ingest()


if __name__ == "__main__":
    main()
