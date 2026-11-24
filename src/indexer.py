from pathlib import Path
from typing import Any


def ingest() -> dict[str, Any]:
    source: Path = Path('./data/raw/')
    md_files = list(source.glob('**/*.md'))
    py_files = list(source.glob('**/*.py'))
    txt_files = list(source.glob('**/*.txt'))

    print(md_files)
    print(py_files)
    print(txt_files)


def main() -> None:
    ingest()


if __name__ == "__main__":
    main()
