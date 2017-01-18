[![Blender](https://raw.githubusercontent.com/ijacquez/blender_tools/master/blender-socket.png)](https://www.blender.org/)

### About

A collection of Blender addons and Python modules for game development.

### Installation

Before the addons can be used, the Python modules in [`modules/`](https://github.com/ijacquez/blender_tools/tree/master/modules/helper_utils) need to be installed first.

#### Windows
 1. For every module, modify the absolute path to `blender.exe` in `Makefile.cygwin`
 2. Administrator privileges needed. Run `make -f Makefile.cygiwn install`
 3. Copy all files in `addons/` to `%APPDATA%\Blender Foundation\Blender\2.XX\scripts\addons\` where `XX` is your version of Blender.
 4. Open Blender, and press *Ctrl+Alt+U* to open the _Blender User Preferences_ window.
 5. Select the _Add-ons_ tab and search for _israel_
 6. Enable all addons
 7. Click on _Save User Settings_ button

#### Other (Unix)
Not yet documented.
