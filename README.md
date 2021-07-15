## Description
Segmentation Utility intended for segmenting medical images with ease. The application is based on 
[PyQT 5.15](https://doc.qt.io/qtforpython/ "PyQT documentation") 
and contains two windows, where the user can pick from:

1. `ui.segViewer` shows the segmentation annotations already made side by side with a notes field to
track changes and give alteration options
   
2. `ui.segLabeler` (**EARLY ALPHA AND UNTESTED**) is an UI based on 
   [labelme](https://github.com/wkentaro/labelme "Labelme Github") with 
   reduced/altered functionality and altered appearance. It unifies the necessary functionality of labelme in a more 
   readable version for better understanding and debugging. Additionally, it contains several bug fixes and UI
   improvements to improve the workflow and efficiency of the tool 

## Requirements
- Ubuntu / macOS / Windows
- Python3
- [PyQt5](https://doc.qt.io/qtforpython/)

## Installation

### Anaconda (Python 3.8)
```bash
conda create --name=<your_env_name> python=3.8
conda activate <your_env_name>
pip install pyqt5  # pyqt5 can be installed via pip on python3
pip install seg_utils

# check whether pyuic5 and pyrcc5 are in the path
$PATH$ # should display the colder path/to/anaconda/<your_env_name>/bin
# otherwise add them manually as they should be included in your bin folder of your environment
```

## Acknowledgement

This repo is an alteration of [labelme](https://github.com/wkentaro/labelme "Labelme Github")
