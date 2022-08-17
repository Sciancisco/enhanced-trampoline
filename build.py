import argparse
import PyInstaller.__main__

parser = argparse.ArgumentParser("Build the application.")
parser.add_argument("--release", action="store_true", help="build release package")
args = parser.parse_args()

options = ["gui.py", "--clean", "--windowed"]

if args.release:
    options.append("--name 'Remote Qira'")
    options.append("--onefile")
else:
    options.append("--name 'Remote Qira DEV'")

PyInstaller.__main__.run(options)
