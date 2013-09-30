FileListTool
============

urwid based console application for easy filelist creation with dq2


## Description

Commanline application for easy creating filelists on the localgroupdisc using dq2 and rucio.

**Dependencies:**
+ python 2.6 or above
+ dq2-tool ready
+ urwid library (included)

Since the urwid package is not available on mogon it is included in this repository


## Installation
Check out this repository with

    git clone https://github.com/weinshec/FileListTool

If you don't have the dq2-tools already setup execute the included script, that sources all the necessary PATH and scripts

    source setupDQ2.sh

Finally you can run the tool via

    ./FileListTool.py


## Usage
Simply run the tool and select your datasets by pressing `ENTER`. You can use the positive/negative list tags to filter the list of available samples.

Command overview:

| Key     | Function                              |
| :-----: | ------------------------------------- |
| `ENTER` | (un)select sample                     |
| `Tab`   | switch between available/selected list|
| `c`     | Create file list                      |
| `p`/`n` | Set positive/negative tags list       |
| `f`     | Change filename of filelist           |
| `d`     | Toggle usage of default output folder |

The default output folder is read from your *ganga_mogon* config file
