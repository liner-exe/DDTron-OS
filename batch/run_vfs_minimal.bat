@echo off
title vfs_minimal

cd ..
cd src

python main.py --vfs="./vfs/minimal.xml" --no-debug

pause