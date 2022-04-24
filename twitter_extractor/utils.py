import functools
import gzip
from pathlib import Path

import ujson


def get_project_root_path() -> Path:
    return Path(__file__).parent.parent


def get_data_folder() -> Path:
    return get_project_root_path() / "data"


def save_json_lines(raw_data_file: Path, json_lines: list[dict]):
    json_dumper = functools.partial(ujson.dumps, ensure_ascii=False, escape_forward_slashes=False)
    with gzip.open(raw_data_file.with_suffix(".jsonl.gzip"), "wt") as f:
        for json_line in json_lines:
            f.write(json_dumper(json_line) + "\n")
