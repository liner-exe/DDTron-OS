@echo off
title start_scripts/start1.txt

cd ..
cd src

python main.py --vfs="./vfs/3_levels.xml" --script="./start_scripts/start1.txt"

pause