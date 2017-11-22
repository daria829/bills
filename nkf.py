# -*- encoding: utf-8 -*-
import subprocess
import hashlib
import os

def nkf(text):
    fileName = hashlib.sha1(text).hexdigest()
    with open(fileName, 'wb') as f:
        f.write(text)
    newText = subprocess.check_output("nkf -w {}".format(fileName), shell=True, universal_newlines=True)
    os.remove(fileName)
    return newText