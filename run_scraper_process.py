import subprocess
import os
import platform

base_dir = os.path.dirname(os.path.abspath(__file__))
if platform.system() == 'Windows':
    python_bin = os.path.join(base_dir, "Scripts", "python.exe")
else:
    python_bin = os.path.join(base_dir, "bin", "python")
script_file = os.path.join(base_dir, "src", "init.py")

subprocess.Popen([python_bin, script_file])
