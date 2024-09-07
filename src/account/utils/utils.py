from pathlib import Path


def get_parent_dir(file_nm):
    parent_dir = Path(file_nm).resolve().parent
    parent_dir = parent_dir.parent

    return parent_dir
