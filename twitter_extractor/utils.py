from pathlib import Path


def get_project_root_path() -> Path:
    return Path(__file__).parent.parent


def get_data_folder() -> Path:
    return get_project_root_path() / "data"
