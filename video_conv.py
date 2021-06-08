import os
from database import SQLiteDatabase
import ffmpeg


def mpg_to_mp4(base_folder: str = "/home/nico/isys/Videos/source",
               output_folder: str = "/home/nico/isys/Videos/converted",
               database_dir: str = "/home/nico/isys/Videos",
               database_name: str = "database.db",
               quiet: bool = False):
    """ Convert videos in mpg format to mp4

        :param str base_folder: filepath of the base folder where the unconverted videos came from
        :param str output_folder: filepath of the converted videos
        :param str database_dir: filepath to the SQLite database base directory
        :param str database_name: name of the database file with extension
        :param bool quiet: if the frame contains a tumour
        """
    db = SQLiteDatabase(database_dir, database_name)
    db.create_videos_table()
    for element in sorted(os.listdir(base_folder)):
        counter = db.get_num_entries("videos")  # call here necessary for the recursion
        elem_path = os.path.join(base_folder, element)
        if os.path.isfile(elem_path):
            # check if it is not already included
            extensions = [".mpg", ".mp4"]
            if any(ext in element for ext in extensions):
                # string format for at least 9999 videos
                conv_filename = f"video{counter+1:04d}.mp4"
                out_file = os.path.join(output_folder, conv_filename)
                # checks if video exists already so it returns False if it does since the add didnt work
                # prevents overwrite
                if db.add_video(elem_path, out_file, element, conv_filename):
                    ffmpeg.input(elem_path).output(out_file).run(quiet=quiet)

            else:
                continue

        elif os.path.isdir(elem_path):
            mpg_to_mp4(base_folder=elem_path)
        else:
            pass


if __name__ == "__main__":
    mpg_to_mp4()
