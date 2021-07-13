import sqlite3
import os
import numpy as np
from typing import Union, List
import pickle
import sys

# NOTE: it is not best practice with the with statements and directly use a connection but it is also not forbidden and
# makes the code nice and clean as the with statement terminates the connection to the database after execution

# NOTE: so far only two tables with specific names are created (videos and images). if put in function, it can be
# altered
import numpy as np

CREATE_VIDEOS_TABLE = """
    CREATE TABLE IF NOT EXISTS videos (
    id INTEGER PRIMARY KEY,
    origin TEXT NOT NULL,
    dest TEXT NOT NULL,
    duration INTEGER NOT NULL,
    UNIQUE (origin));"""
INSERT_VIDEO = "INSERT INTO videos (origin, dest, duration) VALUES (?, ?, ?);"

CREATE_IMAGES_TABLE = """
    CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY,
    video_path TEXT NOT NULL,
    image_path TEXT NOT NULL,
    frame_num INTEGER NOT NULL,
    UNIQUE (video_path, frame_num));"""
INSERT_IMAGE = """
    INSERT INTO images (video_path, image_path, frame_num) 
    VALUES (?, ?, ?);"""

CREATE_LABEL_TABLE = """
    CREATE TABLE IF NOT EXISTS labels (
    id INTEGER PRIMARY KEY,
    image_path TEXT NOT NULL,
    label_list BLOB NOT NULL,
    UNIQUE (image_path));"""


class ImageSample:
    """ Class for the storage of video frames for sampling
            """
    def __init__(self,
                 video_name: str,
                 video_path: str,
                 frame_num: int,
                 tumour: int,
                 bubbles: int,
                 bladder_entrance: int,
                 burnt_tissue: int,
                 instrument: int,
                 scar: int,
                 urine: int,
                 light: str,
                 other: str = ""):
        self.video_name = video_name
        self.video_path = video_path
        self.frame_num = frame_num
        self.tumour = tumour
        self.bubbles = bubbles
        self.bladder_entrance = bladder_entrance
        self.burnt_tissue = burnt_tissue
        self.instrument = instrument
        self.scar = scar
        self.urine = urine
        self.light = light
        self.other = other

    def __repr__(self):
        rep = f"Frame {self.frame_num}"
        return rep


class LabelStruct:
    """Struct to store all necessary information within the sqlite database.
    Can only be pickle but needs further stuff for json. Json is more secure but requires
    inheritance and own function.
    https://stackoverflow.com/questions/3768895/how-to-make-a-class-json-serializable
    https://stackoverflow.com/questions/6578986/how-to-convert-json-data-into-a-python-object
    """
    def __init__(self,
                 label_name: str,
                 points: np.array,
                 group_id: None,
                 shape_type: str,
                 flags: None):
        self.label_name = label_name
        self.shape_type = shape_type
        self.points = points
        self.group_id = group_id
        self.flags = flags

    def __repr__(self):
        rep = f"{self.label_name} ({self.shape_type.capitalize()}, {self.points.shape[0]} vertices)"
        return rep

    @staticmethod
    def from_json(json_list):
        """Create Labelstruct from JSON dictionary.
        """
        return [LabelStruct(label_name=json_dict['label'],
                            points=json_dict['points'],
                            group_id=json_dict['group_id'],
                            shape_type=json_dict['shape_type'],
                            flags=json_dict['flags']) for json_dict in json_list]

    def to_json(self):
        return {'label': self.label_name,
                'points': self.points,
                'group_id': self.group_id,
                'shape_type': self.shape_type,
                'flags': self.flags}


class SQLiteDatabase:
    def __init__(self, database_path: str):
        """Connect to database as initialization

            :param database_path: path to the database
            """
        self.connection = sqlite3.connect(database_path)

    def create_videos_table(self):
        """ Create a table within a connected database with columns\n
            id, origin, destination, name
            """
        with self.connection:
            self.connection.execute(CREATE_VIDEOS_TABLE)

    def create_images_table(self):
        """ Create a table for images """
        with self.connection:
            self.connection.execute(CREATE_IMAGES_TABLE)

    def create_labels_table(self):
        """ Create a table for labels """
        with self.connection:
            self.connection.execute(CREATE_LABEL_TABLE)

    def add_label(self, image_path_rel: str, list_labels: List[dict]) -> bool:
        """ Add a label to existing label table

            :param str image_path_rel: relative path of the image
            :param str list_labels: list of LabelStruct data types
            :return bool: True if successful, false otherwise
        """
        raise NotImplementedError("Function add_label needs to be adapted to the new table")
        try:
            with self.connection:
                self.connection.execute("""
                INSERT INTO labels (image_path, label_list) VALUES (?, ?);""", (image_path_rel, pickle.dumps(list_labels)))
            return True

        # could be prevented by making the statement INSERT_VIDEO to INSERT OR REPLACE
        # but this increases the unique file id in the beginning and i dont want that
        except sqlite3.OperationalError:
            print(f"Duplicate video with same origin ({image_path_rel}) found. Skipping file")
            return False

    def add_video(self, origin_rel: str, dest_rel: str, duration: int) -> bool:
        """ Add a video entry to existing table if the origin_name is not already included in the database

            :param str origin_rel: relative origin of video
            :param str dest_rel: relative destination
            :param int duration: duration of the video necessary for PyQT
            :return bool: True if successful, false otherwise
        """
        try:
            with self.connection:
                self.connection.execute(INSERT_VIDEO, (origin_rel, dest_rel, duration))
            return True

        # could be prevented by making the statement INSERT_VIDEO to INSERT OR REPLACE
        # but this increases the unique file id in the beginning and i dont want that
        except sqlite3.OperationalError:
            print(f"Duplicate video with same origin ({origin_rel}) found. Skipping file")
            return False

    def add_image(self, video_path_rel: str, image_path_rel: str, frame_num: str) -> bool:
        """ Add a video entry to existing table if the origin_name is not already included in the database

            :param str video_path_rel: relative path of the video where the frames are extracted from
            :param str image_path_rel: relative path of the image where it is stored to
            :param int frame_num: Frame Number of the image within the video
            :returns bool: True if successful, false otherwise
        """
        try:
            with self.connection:
                self.connection.execute(INSERT_IMAGE, (video_path_rel, image_path_rel, frame_num))
            return True

        # could be prevented by making the statement INSERT_VIDEO to INSERT OR REPLACE
        # but this increases the unique file id in the beginning and i dont want that
        except sqlite3.OperationalError:
            print(f"({video_path_rel}, {frame_num}) already converted. Skipping file")
            return False

    def add_column(self, table_name: str, column_name: str, datatype: str) -> bool:
        """ Add a column to an existing table

            :param str table_name: name of the existing table
            :param str column_name: name of the new column
            :param str datatype: datatype supported by SQLite
            :returns bool: True if successful, false otherwise
        """
        try:
            data_types = ["NULL", "INTEGER", "REAL", "TEXT", "BLOB"]
            if datatype not in data_types:
                print(f"Specified data type {datatype} is not allowed. Allowed data types are {data_types}")
                return False
            else:
                with self.connection:
                    self.connection.execute(f"""ALTER TABLE {table_name} ADD {column_name} {datatype};""")
                return True

        # could be prevented by making the statement INSERT_VIDEO to INSERT OR REPLACE
        # but this increases the unique file id in the beginning and i dont want that
        except sqlite3.OperationalError as error:
            print(error)
            return False

    def update_label(self, image_name: str, label_class_dict: dict) -> bool:
        """Update one single label with the new label_list and the respective classes present. Every key in the
        label_class_dict will be used to update one column specified by the key. The columns of the table are dynamic"""
        try:
            with self.connection:
                columns = self.get_column_names("labels")
                classes = self.get_label_classes()
                for key, entry in label_class_dict.items():
                    if key in columns:
                        if key == 'label_list':
                            self.connection.execute(f"""UPDATE labels SET {key} = ? WHERE image_path = ?;""",
                                                    (pickle.dumps(entry), image_name))
                        else:
                            self.connection.execute(f"""UPDATE labels SET {key} = ? WHERE image_path = ?;""",
                                                    (entry, image_name))
                    elif key in classes:
                        self.connection.execute(f"""UPDATE labels SET {"class_"+key} = ? WHERE image_path = ?;""",
                                                (entry, image_name))
                    else:
                        print(f"Key {key} not in table. Skipping")
                        continue
                return True
        except sqlite3.OperationalError as error:
            print(error)
            return False

    def update_labels(self) -> bool:
        """Temporary function to update the columns with the label_list of each entry"""
        try:
            with self.connection:
                entries = self.get_entries_all("labels")
                classes = self.get_label_classes()
                for _entry in entries:
                    _classes_dict = {i:0 for i in classes}
                    _label_classes = []
                    for _label in _entry[2]:
                        if _label['label'] not in _label_classes:
                            _label_classes.append(_label['label'])
                            _classes_dict[_label['label']] = 1 # here one can also obtain the number of instances if the if condition is removed and += 1 instead of =1
                    self.update_label(_entry[1], _classes_dict)
        except sqlite3.OperationalError as error:
            print(error)
            return False

    def get_column_names(self, table_name):
        try:
            with self.connection:
                columns = self.connection.execute(f"""PRAGMA table_info(labels)""").fetchall()
            return [col[1] for col in columns]
        except sqlite3.OperationalError as error:
            print(error)
            return False

    def get_label_classes(self) -> List[str]:
        r"""Returns the classes present in the labels table"""
        try:
            with self.connection:
                columns = self.connection.execute(f"""PRAGMA table_info(labels)""").fetchall()
            column_list = []
            for col in columns:
                if 'class_' in col[1]:
                    column_list.append(col[1].replace('class_', ''))
                else:
                    continue
            return column_list
        except sqlite3.OperationalError as error:
            print(error)
            return False

    def get_table_names(self):
        """ Get all tables within one database

            :returns List: List of all tables within the database
        """
        try:
            with self.connection:
                return self.connection.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()

        # could be prevented by making the statement INSERT_VIDEO to INSERT OR REPLACE
        # but this increases the unique file id in the beginning and i dont want that
        except sqlite3.OperationalError:
            print("Error")
            return False

    def get_entries_all(self, table_name: str) -> List[list]:
        """ Get all the entries within the specified table

            :param str table_name: name of the table from which to get entries
            :returns: List of tuples with all columns and rows of the table
            """
        try:
            with self.connection:
                ret = self.connection.execute(f"SELECT * FROM {table_name};").fetchall()
                return check_for_bytes(ret)
        except sqlite3.OperationalError:
            print(f"Accessing wrong table {table_name}."
                  f"Available tables are {[tab[0] for tab in self.get_table_names()]}")

    def get_entries_specific(self, table_name: str, column_name: str, entry_name: str):
        """ Get all the entries where the entry_name is in the column specified by column_name

            :param str entry_name: exact (?) string of the elements which are searched for. I.e "video" would give all
            rows with "video" as entry of the specified column
            :param str table_name: name of the table from which to get entries
            :param str column_name: name of the column in which to search for the entry_name
            :returns: List of tuples with all columns and rows of the table
            """
        if table_name == "labels" and column_name == "label_list":
            raise AttributeError("Entries are stored as bytes and can't be searched")
        try:
            with self.connection:
                ret = self.connection.execute(f"SELECT * FROM {table_name} WHERE {column_name} = ?;", (entry_name,)).fetchall()
                return check_for_bytes(ret)
        except sqlite3.OperationalError as err:
            print(err)

    def get_label_from_imagepath(self, imagepath: str):
        ret = self.connection.execute(f"SELECT label_list FROM labels WHERE image_path = ?;", (imagepath,)).fetchall()
        return check_for_bytes(ret)

    def get_entries_of_column(self, table_name: str, column_name: str):
        """ Get all the entries within the table by the specifier of the column

            :param str table_name: name of the table from which to get entries
            :param str column_name: name of the column in which to search for the entry_name
            :returns: List of tuples with all columns and rows of the table
            """
        try:
            with self.connection:
                ret = self.connection.execute(f"SELECT {column_name} FROM {table_name};").fetchall()
                return check_for_bytes(ret)
        except sqlite3.OperationalError:
            print(f"Accessing wrong table {table_name}."
                  f"Available tables are {[tab[0] for tab in self.get_table_names()]}")

    def get_num_entries(self, table_name: str):
        """ Get the total number of entries

            :param str table_name: name of the table from which to get entries
            :returns: Number of total entries
            """
        try:
            with self.connection:
                return self.connection.execute(f"SELECT COUNT(*) FROM {table_name};").fetchone()[0]
        except sqlite3.OperationalError:
            print(f"Accessing wrong table {table_name}."
                  f"Available tables are {[tab[0] for tab in self.get_table_names()]}")

    def get_num_entries_specific(self, table_name: str, column_name: str, entry_name: str) -> int:
        """ Returns number of entries which match the specifier entry_name of the column

            :param str entry_name: name of the video one wants
            :param str table_name: name of the table from which to get entries
            :param str column_name: name of the column in which to search for the entry_name
            :returns: List of tuples with all columns and rows of the table
            """
        if table_name == "labels" and column_name == "label_list":
            raise AttributeError("Entries are stored as bytes and can't be searched")
        try:
            with self.connection:
                return self.connection.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} = ?;", (entry_name,)).fetchone()[0]
        except sqlite3.OperationalError:
            print(f"Accessing wrong table {table_name}."
                  f"Available tables are {[tab[0] for tab in self.get_table_names()]}")

    def delete_table(self, table_name: str):
        """ Delete entire table

            :param str table_name: name of the table where to delete
            """
        try:
            with self.connection:
                return self.connection.execute(f"DROP TABLE IF EXISTS {table_name};")
        except sqlite3.OperationalError:
            print(f"Accessing wrong table {table_name}."
                  f"Available tables are {[tab[0] for tab in self.get_table_names()]}")

    def rename_column(self, table_name, old_column_name, new_column_name):
        """ Change all entries within a table and column that contain a certain string

            :param str table_name: name of the table where to alter the entry
            :param str old_column_name: name of the old column
            :param str new_column_name: name of the new column
            """
        try:
            with self.connection:
                # NOTE: pure f string formatting didnt work so its a mixture. Don't know why
                self.connection.execute(
                    f"""ALTER TABLE {table_name} RENAME COLUMN {old_column_name} TO {new_column_name};""")
        except sqlite3.OperationalError as err:
            print(err)

    def rename_table(self, old: str, new: str):
        """Alters the name of an existing table

            :param str old: old table name
            :param str new: new table name
            """
        # TODO: error catching with table names if they do not exist
        with self.connection:
            self.connection.execute(f"""ALTER TABLE {old} RENAME TO {new}""")

    def get_video_from_image(self, image_name: str):
        try:
            with self.connection:
                ret = self.connection.execute(f"SELECT * FROM images WHERE image_path = ?;", (image_name,)).fetchone()
                duration = self.get_entries_specific('videos', 'dest', ret[1])[3]
                return ret[1], ret[3], duration
        except sqlite3.OperationalError as err:
            print(err)

    def update_entry(self, table_name: str, column_name_search: str, keyword: str, column_name_replace: str, value_new: str):
        """ Update a single entry based on the old value in the column. Is most likely similar to
        replace_specific and change specific entry

            :param str table_name: name of the table where to alter the entry
            :param int keyword: keyword to search in column_name_search
            :param str column_name_search: name of the column the searched keyword is in
            :param str column_name_replace: column where it should be replaced
            :param str value_new: new value to replace the old with
            """
        try:
            with self.connection:
                # NOTE: pure f string formatting didnt work so its a mixture. Don't know why
                self.connection.execute(f"""UPDATE {table_name} SET {column_name_replace} = ? WHERE {column_name_search} = ?;""",
                                        (value_new, keyword))
        except sqlite3.OperationalError as err:
            print(err)


# TODO: generate @staticmethod within the class if not necessary somewhere else
def get_filename_from_path(path: str):
    """ Get the Filename of a Path object stored as a string

        :param str path: path to get the filename of
        """
    return os.path.basename(path)


def check_for_bytes(lst: List[tuple]) -> Union[List[list], list]:
    """ Iterates over a list of tuples and depickles byte objects. The output is converted depending on how many entries
    the initial list contains. If its just one per sub-list, each of them is removed

        :param tuple lst: tuple to be searched for
        :returns: Either a List of Lists or just a List depending on how many entries are put in
    """
    lst = convert_to_list(lst)
    for _list_idx, _list_entry in enumerate(lst):

        # this replaces lists with only one entry
        if len(_list_entry) == 1:
            if isinstance(_list_entry[0], bytes):
                lst[_list_idx] = pickle.loads(_list_entry[0])
            else:
                lst[_list_idx] = _list_entry[0]
        else:
            for _tuple_idx, _value in enumerate(list(_list_entry)):
                if isinstance(_value, bytes):
                    lst[_list_idx][_tuple_idx] = pickle.loads(_value)
                else:
                    continue
    if len(lst) == 1:
        lst = lst[0]
    return lst


def convert_to_list(lst: List[tuple]) -> List[list]:
    return [list(elem) for elem in lst]


if __name__ == "__main__":
    database_path = "/home/nico/isys/data/test/database.db"
    database = SQLiteDatabase(database_path)
    database.update_labels()
