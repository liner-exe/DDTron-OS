import argparse

from system import OperatingSystem

def main():
    parser = argparse.ArgumentParser(description="DDTron OS Emulator")
    parser.add_argument("--vfs", help="Path to physical VFS location", default=None)
    parser.add_argument("--script", help="Path to start script to execute", default=None)
    parser.add_argument("--no-debug", action="store_true", help="Disables debug at startup")
    args = parser.parse_args()

    debug = not args.no_debug
    os = OperatingSystem(vfs_path=args.vfs, start_script=args.script, debug=debug)
    os.run()

if __name__ == "__main__":
    main()