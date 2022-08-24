# Enhanced trampoline for INSQ

This program is intended to work with Eurotramp's Qira software. It aims to
enable control Qira using a Bluetooth remote, synchronize video recording with
Qira and extract relevant information from the generated ".dat" files.

## Installing

First download or clone this repository.

### Configure Remote Qira

You should first configure properly the program in `src/config.py`
beforehand as this config was used for testing on the dev computer.
Mainly, you should make sure that in

* QiraConfig:
   * `exe_path` points to Qira's executable
   * `window_title` matches your version of Qira
   * all the "`position`s" point what they are supposed to
* CameraConfig:
   * increment `camera_index` if you are having trouble with the camera
* ServerConfig:
   * all the "`directory`s" point the the correct locations and exists

To find the various positions, you can run
```
python -i -c 'import pyautogui'
```
and use `pyautogui.position()` directly to get the position of the mouse pointer.

### Configure Qira

While you are configuring stuff, you should also configure Qira.

#### Configure the filename template

In Qira, press the menu "Config" -> "Autosave config". Under "File system" tick
"Enable autosave to file". Then, select the path you configured for
`ServerConfig["qira_data_directory"]`. Finally, make sure that
"Filename template" matches the one configured in `ServerConfig["filename_spec"]`.
Press "Ok" and you are done.

#### Enable the network server

In Qira, press the menu "Config" -> "Network". Under "Server settings" tick
"Enable server" and press "Ok". This is how Remote Qira sends meta information
about the routine.

### Building

To run or build this program, it is recommended to use Anaconda (or miniconda).
The specifications for the environment are provided in `trampo-env.yml`.
To create the environment, run
```
conda env create trampo-env.yml
```
in the shell of choice (`cd`ed in this directory).

Once the environment created and activated, you can build the executable by
running:
```
python build.py
```
The executable name "Remote Qira" should be in the `dist` directory.
Copy-paste it wherever you like. Double click to launch, like any other program.

Have fun!
