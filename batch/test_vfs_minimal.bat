@echo off
title vfs_minimal

cd ..
cd src

python main.py --vfs="./vfs/vfs.xml" --no-debug

pause