import argparse
import PyInstaller.__main__

parser = argparse.ArgumentParser("Build the application.")
parser.add_argument("--clean", action="store_true", help="build release package")
args = parser.parse_args()

options = ["src/gui.py", "--name", "Remote Qira", "--windowed", "--onefile"]

if args.clean:
    options.append("--clean")

PyInstaller.__main__.run(options)
