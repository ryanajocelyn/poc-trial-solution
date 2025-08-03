import json
import re
from pathlib import Path

from account.utils.constants import FLAT_NOS


def get_parent_dir(file_nm):
    parent_dir = Path(file_nm).resolve().parent
    parent_dir = parent_dir.parent

    return parent_dir


def parse_house_no(desc):
    regex = [
        {"pattern": "(.*)(/A\\d{3})(.*)", "index": 2},
        {"pattern": "(A\\d{3})(.*)", "index": 1},
        {"pattern": "(.*)(\\d{3})(.*)", "index": 2},
        {"pattern": "(\\d{3})(.*)", "index": 1},
        {"pattern": "(.*)/[a-z]+(\\d{3})[a-z- /]+(.*)", "index": 2},
        {"pattern": "(.*)[- /a-z]+(\\d{3})[a-z- /]+(.*)", "index": 2},
        {"pattern": "(.*)[FLAT]+(\\d{3})[a-z- /]+(.*)", "index": 2},
    ]
    content = None
    for reg in regex:
        content = get_by_pattern(desc, reg)
        if content:
            break
    # Read the Flat and Owner name mappings
    name_mappings = get_flat_name_mappings()
    if not content:
        for name, flat in name_mappings.items():
            if name in desc.upper():
                content = flat
                break

    return content


def get_by_pattern(desc, reg):
    content = None
    pattern = re.compile(reg["pattern"], flags=re.IGNORECASE)
    match = pattern.match(desc)
    if match:
        content = match.group(reg["index"])
        content = content.replace("/A", "")
        content = content.replace("A", "")
        if content not in FLAT_NOS:
            content = None

    return content


def get_flat_name_mappings():
    parent_dir = get_parent_dir(__file__)
    name_file = f"{parent_dir}\\config\\flat_name_mappings.json"
    with open(name_file, "r", encoding="utf-8") as nf:
        name_mappings = json.loads(nf.read())
    return name_mappings


def get_vendor_expenses():
    parent_dir = get_parent_dir(__file__)
    name_file = f"{parent_dir}\\config\\vendor_debit.json"
    with open(name_file, "r", encoding="utf-8") as nf:
        name_mappings = json.loads(nf.read())
    return name_mappings
