from subprocess import Popen
from os import path
from platform import system

base_dir = path.dirname(path.abspath(__file__))

python_bin = path.join(base_dir, "Scripts", "python.exe") if system() == 'Windows' \
        else path.join(base_dir, "bin", "python")

script_file = path.join(base_dir, "src", "init.py")

Popen([python_bin, script_file])
