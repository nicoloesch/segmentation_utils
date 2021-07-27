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
   
## Functionality
### To-Do
- [ ] tight SQL integration
- [ ] efficient labeling with polygon, circle and outline tracking
- [ ] export options
- [ ] adapted context menu

### Implemented
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
```
####Note for Linux Users
The repository requires both `PyQt5` and `opencv-python`. There might be a conflict within the base version of `PyQt5`
and its binaries that ship with Linux leading to the following error
```bash
QObject::moveToThread: Current thread (0x557c88f2ec90) is not the object's thread (0x557c8970c830).
Cannot move to target thread (0x557c88f2ec90)
```

This can be fixed by building `opencv-python` from source as described [here](https://stackoverflow.com/questions/52337870/python-opencv-error-current-thread-is-not-the-objects-thread)
```bash
conda activate <your_env_name>
pip install --no-binary opencv-python opencv-python
```


## Development
## Building standalone application
```bash
# navigate to the base folder seg_utils containing setup.py
pip install .
pip install pyinstaller
pyinstaller labelme.spec
```
This creates a folder `dist`, where an executable can be found.


### Working with UI Files (deprecated)
```bash
# conda environment needs to be active otherwise there will not be a pyuic5 command
pyuic5 --from-imports=<Package_Name> -x <UI_File>.ui -o <UI_File>.py  # specifiy the name given by <UI_File>
# and the import statement <Package_Name> as one would in Python with the full path to the package 
# e.g. seg_utils.src
pyrcc5 <Resource_File>.qrc -o <Resource_File>_rc.py
```


## Acknowledgement

This repo is an alteration of [labelme](https://github.com/wkentaro/labelme "Labelme Github")
