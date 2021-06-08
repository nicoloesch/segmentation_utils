import ffmpeg

frames = [20,30,40]
original_path = "/home/nico/isys/data/converted/video0001.mp4"

out, err = (ffmpeg.input(original_path).filter_('select', f'gte(n,{frames[0]})')
            .output("home/nico/Desktop/test.png", vframes=1, )
            .run(capture_stdout=True, quiet=False))
