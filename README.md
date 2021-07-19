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

# check whether pyuic5 and pyrcc5 are in the path
$PATH$ # should display the colder path/to/anaconda/<your_env_name>/bin
# otherwise add them manually as they should be included in your bin folder of your environment
```

## Development
### UI File creation
In the folder `seg_utils.ui` are multiple files ending on `.ui` created by QT Creator. If they are changed, one needs to
update the respective `.py` files with the following command
```bash
# conda environment needs to be active otherwise there will not be a pyuic5 command
pyuic5 -x <UI_File>.ui -o <UI_File>.py # specifiy the name given by <UI_File>
```

If the ui file contains additional resources like external icons, one needs to compile the resource file first by
```bash
pyrcc5 <Resource_File>.qrc -o <Resource_File>_rc.py
# important to contain the _rc in the output file
```

and change the following pyuic command to

```bash
pyuic5 --from-imports -x <UI_File>.ui -o <UI_File>.py # if the resource file is in the same folder
pyuic5 --from-imports=<Package_Name> -x <UI_File>.ui -o <UI_File>.py 
# if the resource file is in a different folder of the same project
```

This automatically imports the `<Resource_File>` by adding a line of `from . import <UI_File>` in the first case if all
files are in the same folder. **Otherwise**, the import path can be specified by the `<Package_name>` which is the xact same 
as if one imports it directly in the python file, e.g `<Package_Name> = seg_utils.ui` results in 
`from seg_utils.ui import <Resource_File>_rc` (in the case of a resource file with icons).
I assume, best practice is to include all resource files at the same place

## Acknowledgement

This repo is an alteration of [labelme](https://github.com/wkentaro/labelme "Labelme Github")
