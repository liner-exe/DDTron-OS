@echo off
title start_scripts/start1.txt

cd ..
cd src

python main.py --vfs="./vfs/few_files.xml" --script="./start_scripts/start1.txt"

pause