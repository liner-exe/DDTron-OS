@echo off
title start_scripts/start2.txt

cd ..
cd src

python main.py --vfs="./vfs/minimal.xml" --script="./start_scripts/start2.txt"

pause