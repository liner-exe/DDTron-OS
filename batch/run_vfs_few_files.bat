@echo off
title vfs_few_files

cd ..
cd src

python main.py --vfs="./vfs/few_files.xml" --no-debug

pause