import os
import sys
import json
import glob
from pathlib import Path
from database import SQLiteDatabase


def main():
    four = 4
    basedir = "/home/nico/isys/data/images"
    convert_json_to_sql(basedir)


def convert_json_to_sql(image_dir: str, database_name: str = "database.db"):
    database = SQLiteDatabase(str(Path(image_dir).parents[0]), database_name)
    database.create_labels_table()
    for idx, file in enumerate(sorted(glob.glob(os.path.join(image_dir, "*.json")))):
        try:
            _file = open(file)
            _json = json.load(_file)
            if _json['imageData']:
                del _json['imageData']
            label_list = [_label for _label in _json['shapes']]
            database.add_label("images/" + _json['imagePath'], label_list)
            print(f"Processed Label {idx+1}/{len(glob.glob(os.path.join(image_dir, '*.json')))}")
        except ValueError:
            pass


if __name__ == "__main__":
    main()