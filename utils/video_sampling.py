from typing import List
import ffmpeg
import os
from database import SQLiteDatabase, ImageSample
import subprocess

def get_frame(fps: int,
              h: int,
              m: int,
              s: int,
              ms: int,
              first_frame: int = 80) -> int:
    """ Convert the timestamp to a the respective frame number

        :param int fps: frames per second of video
        :param int h: hours
        :param int m: minutes
        :param int s: seconds
        :param int ms: milliseconds
        :param int first_frame: first frame ms of avidemux.
        :returns: frame number as int
        """
    frame_duration = (1 / fps) * 1000
    total_duration = ((((h * 60) + m) * 60) + s) * 1000 + ms - first_frame
    return int(total_duration / frame_duration)


def extract_frames(frame_dict: dict,
                   base_path: str = "/home/nico/isys/data",
                   database_name: str = "database.db",
                   output_folder: str = "images"):
    """ Convert a list of frames of one video to the respective images

        :param List frame_dict: dictionary containing video name as key and the list of frames as values
        :param str database_name: name of the SQLite database file
        :param str base_path: path to the base folder where to extract to
        :param str output_folder: name of the output folder where the images are saved to
        """
    for video_name, frames in frame_dict.items():
        # sort the video list based on the frame number
        # TODO: include a database entry and saving
        frame_list = sorted(frames)
        # check for filetype
        if os.path.splitext(video_name)[-1] == ".mp4":
            video_name_without_filetype = os.path.splitext(video_name)[0]
        elif not os.path.splitext(video_name)[-1]:
            # empty file type specifier
            video_name_without_filetype = video_name
            video_name = video_name + ".mp4"
        else:
            raise AttributeError(f"{os.path.splitext(video_name)[-1]} format unsupported")

        # combine to relative path
        video_name = os.path.join("converted", video_name)
        original_path = os.path.join(base_path, video_name)
        database = SQLiteDatabase(base_path, database_name)
        database.create_images_table()
        for idx, frame in enumerate(frame_list):
            num = database.get_num_entries_specific(table_name="images",
                                                    column_name="video_path",
                                                    entry_name=video_name)
            filename = os.path.join(output_folder, f"{video_name_without_filetype}_{num + 1:04d}.png")

            if os.path.isfile(original_path):
                # TODO: extract one frame before and after current one?
                if database.add_image(video_name, filename, frame):
                    out, err = (ffmpeg.input(original_path).filter_('select', 'gte(n,{})'.format(frame))
                                .output(os.path.join(base_path, filename), vframes=1, )
                                .run(capture_stdout=True, quiet=True))
                    print(f"Processed Image {idx + 1}/{len(frame_list)}")
            else:
                raise ValueError(f"{original_path} is not a valid file. Check paths and video name")
            four = 4


def add_duration_to_sql(base_path: str = "/home/nico/isys/data",
                        database_name: str = "database.db"):
    db = SQLiteDatabase(base_path, database_name)

    for video in os.listdir(os.path.join(base_path, "converted")):
        duration = get_duration(os.path.join(base_path, "converted", video)) * 1000.0
        db.update_entry('videos', 'dest', "converted/" + str(video), 'duration', duration)


def get_duration(file):
    """Get the duration of a video using ffprobe."""
    cmd = 'ffprobe -i {} -show_entries format=duration -v quiet -of csv="p=0"'.format(file)
    output = subprocess.check_output(
        cmd,
        shell=True,  # Let this run in the shell
        stderr=subprocess.STDOUT
    )
    # return round(float(output))  # ugly, but rounds your seconds up or down
    return float(output)

frame_dictionary = \
    {
        "video0001.mp4": [get_frame(fps=25, h=0, m=0, s=1, ms=880),
                          get_frame(fps=25, h=0, m=0, s=19, ms=520),
                          get_frame(fps=25, h=0, m=0, s=24, ms=640),
                          get_frame(fps=25, h=0, m=0, s=40, ms=200),
                          get_frame(fps=25, h=0, m=0, s=48, ms=440),
                          get_frame(fps=25, h=0, m=0, s=50, ms=80),
                          get_frame(fps=25, h=0, m=0, s=59, ms=920),
                          get_frame(fps=25, h=0, m=1, s=1, ms=840),
                          get_frame(fps=25, h=0, m=1, s=4, ms=80),
                          get_frame(fps=25, h=0, m=1, s=6, ms=40),
                          get_frame(fps=25, h=0, m=1, s=12, ms=400),
                          get_frame(fps=25, h=0, m=1, s=18, ms=40),
                          get_frame(fps=25, h=0, m=1, s=25, ms=240),
                          get_frame(fps=25, h=0, m=1, s=28, ms=640),
                          get_frame(fps=25, h=0, m=1, s=32, ms=680),
                          get_frame(fps=25, h=0, m=1, s=36, ms=240),
                          get_frame(fps=25, h=0, m=0, s=12, ms=640)],
        "video0002.mp4": [get_frame(fps=25, h=0, m=0, s=0, ms=240),
                          get_frame(fps=25, h=0, m=0, s=5, ms=720),
                          get_frame(fps=25, h=0, m=0, s=11, ms=120),
                          get_frame(fps=25, h=0, m=0, s=19, ms=800),
                          get_frame(fps=25, h=0, m=0, s=26, ms=440),
                          get_frame(fps=25, h=0, m=0, s=39, ms=0),
                          get_frame(fps=25, h=0, m=0, s=44, ms=920),
                          get_frame(fps=25, h=0, m=0, s=49, ms=400),
                          get_frame(fps=25, h=0, m=0, s=52, ms=120),
                          get_frame(fps=25, h=0, m=1, s=14, ms=120),
                          get_frame(fps=25, h=0, m=1, s=25, ms=240),
                          ],
        "video0003.mp4": [get_frame(fps=25, h=0, m=0, s=1, ms=120),
                          get_frame(fps=25, h=0, m=0, s=10, ms=480),
                          get_frame(fps=25, h=0, m=0, s=12, ms=880),
                          get_frame(fps=25, h=0, m=0, s=15, ms=440),
                          get_frame(fps=25, h=0, m=0, s=21, ms=600),
                          get_frame(fps=25, h=0, m=0, s=26, ms=320),
                          get_frame(fps=25, h=0, m=0, s=36, ms=600),
                          get_frame(fps=25, h=0, m=0, s=37, ms=80),
                          get_frame(fps=25, h=0, m=0, s=43, ms=600),
                          get_frame(fps=25, h=0, m=0, s=51, ms=960),
                          get_frame(fps=25, h=0, m=0, s=55, ms=840),
                          get_frame(fps=25, h=0, m=1, s=1, ms=440),
                          get_frame(fps=25, h=0, m=1, s=3, ms=760),
                          get_frame(fps=25, h=0, m=1, s=6, ms=440),
                          get_frame(fps=25, h=0, m=1, s=24, ms=880)],
        "video0004.mp4": [get_frame(fps=25, h=0, m=0, s=0, ms=400),
                          get_frame(fps=25, h=0, m=0, s=14, ms=800),
                          get_frame(fps=25, h=0, m=0, s=20, ms=280),
                          get_frame(fps=25, h=0, m=0, s=22, ms=440),
                          get_frame(fps=25, h=0, m=0, s=30, ms=480),
                          get_frame(fps=25, h=0, m=0, s=40, ms=520),
                          get_frame(fps=25, h=0, m=0, s=43, ms=120),
                          get_frame(fps=25, h=0, m=0, s=51, ms=40),
                          get_frame(fps=25, h=0, m=1, s=0, ms=40),
                          get_frame(fps=25, h=0, m=1, s=6, ms=440),
                          get_frame(fps=25, h=0, m=1, s=7, ms=720),
                          get_frame(fps=25, h=0, m=1, s=15, ms=960),
                          get_frame(fps=25, h=0, m=1, s=26, ms=360),

                          ],
        "video0005.mp4": [get_frame(fps=25, h=0, m=0, s=4, ms=640),
                          get_frame(fps=25, h=0, m=0, s=10, ms=0),
                          get_frame(fps=25, h=0, m=0, s=21, ms=960),
                          get_frame(fps=25, h=0, m=1, s=0, ms=560)],
        "video0006.mp4": [get_frame(fps=25, h=0, m=0, s=0, ms=0),
                          get_frame(fps=25, h=0, m=0, s=5, ms=280),
                          get_frame(fps=25, h=0, m=0, s=9, ms=320),
                          get_frame(fps=25, h=0, m=0, s=14, ms=280),
                          get_frame(fps=25, h=0, m=0, s=36, ms=520),
                          get_frame(fps=25, h=0, m=0, s=45, ms=80),
                          get_frame(fps=25, h=0, m=0, s=57, ms=360),
                          get_frame(fps=25, h=0, m=0, s=59, ms=880),
                          get_frame(fps=25, h=0, m=1, s=5, ms=960),
                          get_frame(fps=25, h=0, m=1, s=7, ms=0),
                          get_frame(fps=25, h=0, m=0, s=4, ms=640),
                          get_frame(fps=25, h=0, m=2, s=1, ms=80),
                          get_frame(fps=25, h=0, m=2, s=10, ms=360),
                          get_frame(fps=25, h=0, m=2, s=18, ms=480),
                          get_frame(fps=25, h=0, m=2, s=26, ms=800),
                          get_frame(fps=25, h=0, m=2, s=29, ms=960),
                          get_frame(fps=25, h=0, m=2, s=33, ms=560),
                          get_frame(fps=25, h=0, m=2, s=41, ms=480),
                          get_frame(fps=25, h=0, m=2, s=52, ms=120),
                          get_frame(fps=25, h=0, m=2, s=59, ms=400),
                          get_frame(fps=25, h=0, m=3, s=6, ms=640),
                          get_frame(fps=25, h=0, m=3, s=10, ms=480),
                          get_frame(fps=25, h=0, m=3, s=21, ms=600),
                          get_frame(fps=25, h=0, m=3, s=27, ms=520),
                          get_frame(fps=25, h=0, m=3, s=35, ms=800),
                          get_frame(fps=25, h=0, m=3, s=42, ms=240),
                          get_frame(fps=25, h=0, m=3, s=58, ms=920),
                          get_frame(fps=25, h=0, m=4, s=5, ms=80),
                          get_frame(fps=25, h=0, m=4, s=32, ms=40),
                          get_frame(fps=25, h=0, m=4, s=35, ms=320),
                          get_frame(fps=25, h=0, m=4, s=39, ms=880),
                          get_frame(fps=25, h=0, m=4, s=43, ms=0),
                          get_frame(fps=25, h=0, m=4, s=54, ms=560),
                          get_frame(fps=25, h=0, m=4, s=59, ms=840),
                          get_frame(fps=25, h=0, m=5, s=9, ms=80),
                          get_frame(fps=25, h=0, m=6, s=37, ms=800),
                          get_frame(fps=25, h=0, m=6, s=56, ms=240),
                          get_frame(fps=25, h=0, m=7, s=0, ms=120),
                          get_frame(fps=25, h=0, m=7, s=6, ms=0),
                          get_frame(fps=25, h=0, m=7, s=7, ms=200),
                          get_frame(fps=25, h=0, m=9, s=13, ms=880),
                          get_frame(fps=25, h=0, m=9, s=16, ms=40),
                          get_frame(fps=25, h=0, m=9, s=19, ms=840),
                          get_frame(fps=25, h=0, m=9, s=28, ms=120),
                          get_frame(fps=25, h=0, m=9, s=37, ms=320),
                          get_frame(fps=25, h=0, m=9, s=43, ms=560),
                          get_frame(fps=25, h=0, m=9, s=57, ms=200),
                          get_frame(fps=25, h=0, m=10, s=4, ms=640),
                          get_frame(fps=25, h=0, m=10, s=17, ms=520),
                          get_frame(fps=25, h=0, m=10, s=37, ms=400),
                          get_frame(fps=25, h=0, m=10, s=40, ms=320),
                          get_frame(fps=25, h=0, m=10, s=47, ms=320),
                          get_frame(fps=25, h=0, m=10, s=58, ms=720),
                          get_frame(fps=25, h=0, m=11, s=7, ms=400),
                          get_frame(fps=25, h=0, m=11, s=17, ms=40),
                          get_frame(fps=25, h=0, m=11, s=33, ms=960),
                          get_frame(fps=25, h=0, m=12, s=0, ms=440),
                          get_frame(fps=25, h=0, m=12, s=33, ms=840),
                          get_frame(fps=25, h=0, m=12, s=42, ms=880),
                          get_frame(fps=25, h=0, m=0, s=5, ms=280),
                          ],
        "video0007.mp4": [get_frame(fps=25, h=0, m=0, s=7, ms=440),
                          get_frame(fps=25, h=0, m=0, s=13, ms=360),
                          get_frame(fps=25, h=0, m=0, s=16, ms=80),
                          get_frame(fps=25, h=0, m=0, s=27, ms=760),
                          get_frame(fps=25, h=0, m=1, s=13, ms=960),
                          get_frame(fps=25, h=0, m=1, s=26, ms=320),
                          get_frame(fps=25, h=0, m=1, s=39, ms=0),
                          get_frame(fps=25, h=0, m=1, s=54, ms=200),
                          get_frame(fps=25, h=0, m=2, s=2, ms=840),
                          get_frame(fps=25, h=0, m=2, s=13, ms=360),
                          get_frame(fps=25, h=0, m=2, s=36, ms=720),
                          ],
        "video0008.mp4": [get_frame(fps=25, h=0, m=0, s=0, ms=0),
                          get_frame(fps=25, h=0, m=0, s=6, ms=40),
                          get_frame(fps=25, h=0, m=0, s=20, ms=160),
                          get_frame(fps=25, h=0, m=0, s=30, ms=920),
                          get_frame(fps=25, h=0, m=0, s=33, ms=440),
                          get_frame(fps=25, h=0, m=0, s=38, ms=880),
                          get_frame(fps=25, h=0, m=0, s=41, ms=40),
                          get_frame(fps=25, h=0, m=0, s=47, ms=760),
                          get_frame(fps=25, h=0, m=0, s=49, ms=600),
                          get_frame(fps=25, h=0, m=0, s=52, ms=680),
                          get_frame(fps=25, h=0, m=1, s=3, ms=400),
                          get_frame(fps=25, h=0, m=1, s=20, ms=200),
                          get_frame(fps=25, h=0, m=1, s=43, ms=0),
                          get_frame(fps=25, h=0, m=1, s=45, ms=320),
                          get_frame(fps=25, h=0, m=1, s=47, ms=400),
                          get_frame(fps=25, h=0, m=1, s=51, ms=640),
                          get_frame(fps=25, h=0, m=1, s=54, ms=560),
                          get_frame(fps=25, h=0, m=1, s=57, ms=440),
                          ],
        "video0009.mp4": [get_frame(fps=25, h=0, m=0, s=3, ms=480),
                          get_frame(fps=25, h=0, m=0, s=10, ms=400),
                          get_frame(fps=25, h=0, m=0, s=15, ms=80),
                          get_frame(fps=25, h=0, m=0, s=22, ms=800),
                          get_frame(fps=25, h=0, m=0, s=34, ms=40),
                          get_frame(fps=25, h=0, m=0, s=43, ms=160),
                          get_frame(fps=25, h=0, m=1, s=1, ms=960),
                          get_frame(fps=25, h=0, m=1, s=3, ms=160),
                          get_frame(fps=25, h=0, m=1, s=8, ms=200),
                          get_frame(fps=25, h=0, m=1, s=40, ms=160),
                          get_frame(fps=25, h=0, m=1, s=44, ms=840),
                          get_frame(fps=25, h=0, m=1, s=54, ms=720),
                          get_frame(fps=25, h=0, m=1, s=58, ms=0),
                          get_frame(fps=25, h=0, m=2, s=16, ms=920),
                          ],
        "video0010.mp4": [get_frame(fps=25, h=0, m=0, s=0, ms=0),
                          get_frame(fps=25, h=0, m=0, s=7, ms=600),
                          get_frame(fps=25, h=0, m=0, s=10, ms=880),
                          get_frame(fps=25, h=0, m=0, s=13, ms=160),
                          get_frame(fps=25, h=0, m=0, s=25, ms=760),
                          get_frame(fps=25, h=0, m=0, s=30, ms=280),
                          get_frame(fps=25, h=0, m=0, s=36, ms=160),
                          get_frame(fps=25, h=0, m=0, s=38, ms=880),
                          get_frame(fps=25, h=0, m=0, s=43, ms=40),
                          get_frame(fps=25, h=0, m=0, s=47, ms=480),
                          get_frame(fps=25, h=0, m=0, s=54, ms=480),
                          get_frame(fps=25, h=0, m=0, s=55, ms=960),
                          get_frame(fps=25, h=0, m=1, s=0, ms=920),
                          ],
        "video0011.mp4": [get_frame(fps=25, h=0, m=0, s=3, ms=400),
                          get_frame(fps=25, h=0, m=0, s=8, ms=920),
                          get_frame(fps=25, h=0, m=0, s=18, ms=680),
                          get_frame(fps=25, h=0, m=0, s=22, ms=240),
                          get_frame(fps=25, h=0, m=0, s=26, ms=200),
                          get_frame(fps=25, h=0, m=0, s=36, ms=520),
                          get_frame(fps=25, h=0, m=0, s=44, ms=360),
                          get_frame(fps=25, h=0, m=0, s=54, ms=960),
                          get_frame(fps=25, h=0, m=1, s=4, ms=160),
                          get_frame(fps=25, h=0, m=1, s=7, ms=240),
                          get_frame(fps=25, h=0, m=1, s=10, ms=280),
                          get_frame(fps=25, h=0, m=1, s=15, ms=120),
                          get_frame(fps=25, h=0, m=1, s=23, ms=680),
                          get_frame(fps=25, h=0, m=1, s=44, ms=80),
                          get_frame(fps=25, h=0, m=1, s=45, ms=600),
                          ],
        "video0012.mp4": [get_frame(fps=25, h=0, m=0, s=5, ms=400),
                          get_frame(fps=25, h=0, m=0, s=7, ms=360),
                          get_frame(fps=25, h=0, m=0, s=13, ms=360),
                          get_frame(fps=25, h=0, m=0, s=28, ms=160),
                          get_frame(fps=25, h=0, m=0, s=32, ms=640),
                          ],
        "video0013.mp4": [get_frame(fps=25, h=0, m=0, s=1, ms=120),
                          get_frame(fps=25, h=0, m=0, s=8, ms=320),
                          get_frame(fps=25, h=0, m=0, s=13, ms=800),
                          get_frame(fps=25, h=0, m=0, s=20, ms=240),
                          get_frame(fps=25, h=0, m=0, s=25, ms=760),
                          get_frame(fps=25, h=0, m=0, s=36, ms=320),
                          get_frame(fps=25, h=0, m=0, s=40, ms=120),
                          get_frame(fps=25, h=0, m=0, s=47, ms=640),
                          get_frame(fps=25, h=0, m=1, s=2, ms=400),
                          get_frame(fps=25, h=0, m=1, s=9, ms=80),
                          get_frame(fps=25, h=0, m=1, s=11, ms=200),
                          get_frame(fps=25, h=0, m=1, s=16, ms=440),
                          get_frame(fps=25, h=0, m=1, s=32, ms=160),
                          get_frame(fps=25, h=0, m=1, s=37, ms=160),
                          get_frame(fps=25, h=0, m=1, s=42, ms=680),
                          get_frame(fps=25, h=0, m=1, s=51, ms=800),
                          get_frame(fps=25, h=0, m=2, s=17, ms=600),
                          get_frame(fps=25, h=0, m=2, s=30, ms=960),
                          get_frame(fps=25, h=0, m=2, s=41, ms=600),
                          get_frame(fps=25, h=0, m=2, s=53, ms=680),
                          get_frame(fps=25, h=0, m=3, s=18, ms=600),
                          get_frame(fps=25, h=0, m=3, s=33, ms=960),
                          get_frame(fps=25, h=0, m=3, s=45, ms=320),
                          get_frame(fps=25, h=0, m=3, s=54, ms=480),
                          get_frame(fps=25, h=0, m=4, s=7, ms=200),
                          get_frame(fps=25, h=0, m=4, s=32, ms=720),
                          get_frame(fps=25, h=0, m=4, s=40, ms=520),
                          get_frame(fps=25, h=0, m=5, s=0, ms=120),],
        "video0014.mp4": [get_frame(fps=25, h=0, m=0, s=8, ms=800),
                          get_frame(fps=25, h=0, m=0, s=11, ms=920),
                          get_frame(fps=25, h=0, m=0, s=19, ms=0),
                          get_frame(fps=25, h=0, m=0, s=25, ms=960),
                          get_frame(fps=25, h=0, m=0, s=34, ms=800),
                          get_frame(fps=25, h=0, m=0, s=45, ms=320),
                          get_frame(fps=25, h=0, m=0, s=49, ms=480),
                          get_frame(fps=25, h=0, m=1, s=4, ms=560),
                          get_frame(fps=25, h=0, m=1, s=12, ms=120),
                          get_frame(fps=25, h=0, m=1, s=45, ms=280),
                          get_frame(fps=25, h=0, m=1, s=52, ms=400),
                          get_frame(fps=25, h=0, m=2, s=5, ms=280),
                          get_frame(fps=25, h=0, m=2, s=34, ms=120),
                          get_frame(fps=25, h=0, m=3, s=4, ms=920),
                          get_frame(fps=25, h=0, m=3, s=13, ms=960),
                          get_frame(fps=25, h=0, m=3, s=20, ms=880),
                          get_frame(fps=25, h=0, m=3, s=27, ms=200),
                          get_frame(fps=25, h=0, m=3, s=40, ms=880),
                          get_frame(fps=25, h=0, m=3, s=59, ms=120),
                          get_frame(fps=25, h=0, m=4, s=18, ms=520),
                          get_frame(fps=25, h=0, m=4, s=40, ms=440),
                          get_frame(fps=25, h=0, m=4, s=46, ms=960),
                          get_frame(fps=25, h=0, m=4, s=59, ms=120),
                          get_frame(fps=25, h=0, m=5, s=31, ms=920),
                          get_frame(fps=25, h=0, m=5, s=40, ms=40),
                          get_frame(fps=25, h=0, m=5, s=48, ms=320),
                          get_frame(fps=25, h=0, m=5, s=52, ms=560),
                          get_frame(fps=25, h=0, m=5, s=55, ms=600),
                          get_frame(fps=25, h=0, m=5, s=58, ms=640),
                          get_frame(fps=25, h=0, m=6, s=4, ms=480),
                          get_frame(fps=25, h=0, m=6, s=6, ms=80),
                          get_frame(fps=25, h=0, m=6, s=21, ms=440),
                          get_frame(fps=25, h=0, m=6, s=33, ms=160),
                          get_frame(fps=25, h=0, m=6, s=44, ms=0),
                          get_frame(fps=25, h=0, m=6, s=50, ms=400),
                          get_frame(fps=25, h=0, m=6, s=57, ms=680),],
        "video0015.mp4": [get_frame(fps=25, h=0, m=0, s=1, ms=760),
                          get_frame(fps=25, h=0, m=0, s=7, ms=600),
                          get_frame(fps=25, h=0, m=0, s=13, ms=360),
                          get_frame(fps=25, h=0, m=0, s=23, ms=400),
                          get_frame(fps=25, h=0, m=0, s=29, ms=160),
                          get_frame(fps=25, h=0, m=0, s=35, ms=880),
                          get_frame(fps=25, h=0, m=0, s=42, ms=80),
                          get_frame(fps=25, h=0, m=0, s=52, ms=800),
                          get_frame(fps=25, h=0, m=0, s=56, ms=560),
                          get_frame(fps=25, h=0, m=1, s=0, ms=680),
                          get_frame(fps=25, h=0, m=1, s=10, ms=0),
                          get_frame(fps=25, h=0, m=1, s=18, ms=400),
                          get_frame(fps=25, h=0, m=1, s=38, ms=760),
                          get_frame(fps=25, h=0, m=1, s=50, ms=560),
                          get_frame(fps=25, h=0, m=1, s=59, ms=280),
                          ],
        "video0016.mp4": [get_frame(fps=25, h=0, m=0, s=0, ms=80),
                          get_frame(fps=25, h=0, m=0, s=4, ms=440),
                          get_frame(fps=25, h=0, m=0, s=11, ms=560),
                          get_frame(fps=25, h=0, m=0, s=14, ms=680),
                          get_frame(fps=25, h=0, m=0, s=17, ms=360),
                          get_frame(fps=25, h=0, m=0, s=22, ms=680),
                          get_frame(fps=25, h=0, m=0, s=51, ms=680),
                          get_frame(fps=25, h=0, m=0, s=59, ms=160),
                          get_frame(fps=25, h=0, m=1, s=8, ms=360),
                          get_frame(fps=25, h=0, m=1, s=11, ms=880),
                          get_frame(fps=25, h=0, m=1, s=17, ms=440),
                          get_frame(fps=25, h=0, m=1, s=28, ms=280),
                          get_frame(fps=25, h=0, m=1, s=41, ms=720),
                          get_frame(fps=25, h=0, m=3, s=1, ms=760),
                          get_frame(fps=25, h=0, m=3, s=6, ms=960),
                          get_frame(fps=25, h=0, m=3, s=17, ms=120),
                          get_frame(fps=25, h=0, m=3, s=23, ms=600),
                          get_frame(fps=25, h=0, m=4, s=23, ms=880),
                          get_frame(fps=25, h=0, m=4, s=34, ms=200),
                          get_frame(fps=25, h=0, m=4, s=48, ms=680),
                          ],
        "video0017.mp4": [get_frame(fps=25, h=0, m=0, s=6, ms=160),
                          get_frame(fps=25, h=0, m=0, s=17, ms=40),
                          get_frame(fps=25, h=0, m=0, s=0, ms=0),
                          ],
        "video0018.mp4": [get_frame(fps=25, h=0, m=0, s=1, ms=800),
                          get_frame(fps=25, h=0, m=0, s=7, ms=520),
                          get_frame(fps=25, h=0, m=0, s=29, ms=480),
                          get_frame(fps=25, h=0, m=0, s=42, ms=880),
                          get_frame(fps=25, h=0, m=1, s=7, ms=680),
                          get_frame(fps=25, h=0, m=1, s=13, ms=640),

                          ],
        "video0019.mp4": [get_frame(fps=25, h=0, m=0, s=2, ms=520),
                          get_frame(fps=25, h=0, m=0, s=19, ms=440),
                          get_frame(fps=25, h=0, m=0, s=35, ms=800),
                          get_frame(fps=25, h=0, m=1, s=3, ms=280),
                          get_frame(fps=25, h=0, m=1, s=25, ms=760),
                          get_frame(fps=25, h=0, m=1, s=40, ms=240),
                          get_frame(fps=25, h=0, m=2, s=6, ms=520),
                          get_frame(fps=25, h=0, m=2, s=13, ms=440),
                          get_frame(fps=25, h=0, m=2, s=21, ms=560),
                          get_frame(fps=25, h=0, m=2, s=34, ms=720),
                          get_frame(fps=25, h=0, m=2, s=50, ms=400),
                          get_frame(fps=25, h=0, m=2, s=59, ms=400),
                          get_frame(fps=25, h=0, m=3, s=20, ms=400),
                          get_frame(fps=25, h=0, m=4, s=24, ms=40),
                          ],
        "video0020.mp4": [get_frame(fps=25, h=0, m=0, s=3, ms=520),
                          get_frame(fps=25, h=0, m=0, s=16, ms=0),
                          ],
        "video0021.mp4": [get_frame(fps=25, h=0, m=0, s=3, ms=720),
                          get_frame(fps=25, h=0, m=0, s=10, ms=840),
                          get_frame(fps=25, h=0, m=0, s=14, ms=600),
                          get_frame(fps=25, h=0, m=0, s=36, ms=40),
                          ],
        "video0022.mp4": [get_frame(fps=25, h=0, m=0, s=31, ms=360),
                          get_frame(fps=25, h=0, m=2, s=24, ms=640),
                          get_frame(fps=25, h=0, m=3, s=35, ms=200),
                          get_frame(fps=25, h=0, m=4, s=19, ms=680),
                          get_frame(fps=25, h=0, m=4, s=39, ms=80),
                          ],
        "video0023.mp4": [get_frame(fps=25, h=0, m=0, s=13, ms=840),
                          get_frame(fps=25, h=0, m=0, s=52, ms=160),
                          get_frame(fps=25, h=0, m=1, s=5, ms=760),
                          get_frame(fps=25, h=0, m=1, s=26, ms=520),
                          ],
     }

add_duration_to_sql()

