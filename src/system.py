from parser import parse
from pathlib import Path
import time
import xml.etree.ElementTree as ET
import base64

from exceptions import UnknownCommand, BrokenFormat
from utils import tprint

class OperatingSystem:
    current_path = "root"

    art = r"""
     ____  ____  _____                _____ _____ 
    |    \|    \|_   _|___ ___ ___   |     |   __|
    |  |  |  |  | | | |  _| . |   |  |  |  |__   |
    |____/|____/  |_| |_| |___|_|_|  |_____|_____|
    """

    class Meta:
        NAME: str = "DDTRon"
        VERSION_MAJOR: int = 1
        VERSION_MINOR: int = 0
        SYSTEM_TYPE: str = "x86_64"
        USERNAME: str = "user"

    def __init__(self) -> None:
        pass

    def __init__(self, vfs_path: str = None, start_script: str = None, debug: bool = True) -> None:
        self.vfs_path = Path(vfs_path) if vfs_path else None
        self.start_script = Path(start_script) if start_script else None
        self.debug = debug

        if self.debug:
            self._debug_print()

        if self.vfs_path:
            self.load_vfs(self.vfs_path)

        self.startup()

    def startup(self) -> None:
        tprint(self.art, delay=0.001)
        tprint(f"{self.Meta.NAME} OS v{self.Meta.VERSION_MAJOR}.{self.Meta.VERSION_MINOR} ({self.Meta.SYSTEM_TYPE})")
        tprint(f"Kernel {self.Meta.VERSION_MAJOR}.{self.Meta.VERSION_MINOR}-{self.Meta.NAME} on VM\n")
        tprint(f"Welcome to {self.Meta.NAME} OS!")

    def _debug_print(self) -> None:
        tprint("=== Emulator Config (Debug) ===")
        tprint(f"VFS path: {self.vfs_path.resolve() if self.vfs_path else 'none'}")
        tprint(f"Start script: {self.start_script if self.start_script else 'none'}")
        tprint(f"Debug: {self.debug}")
        tprint("===============================")

    def process(self, command: str, args: list) -> bool:
        if command is None:
            raise UnknownCommand("Error: No command provided")

        if command == "cd":
            self.process_cd(args)
        elif command == "ls":
            self.process_ls(args)
        elif command == "exit":
            self.process_exit()
            return False
        else:
            raise UnknownCommand(f"Error: Unknown command {command}")
        
        return True

    def process_cd(self, args: list) -> None:
        tprint("cd " + ' '.join(args))

    def process_ls(self, args: list) -> None:
        tprint("ls " + ' '.join(args))

    def process_exit(self) -> None:
        tprint("Shutting down")

    def _run_start_script(self, path: Path) -> None:
        if not path.exists():
            tprint("Error: Start script path does not exist.")
            return
        
        tprint(f"=== Running start script: {path} ===")
        with_error = False

        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                tprint(f"{self.Meta.USERNAME}@{self.Meta.NAME} OS [{self.current_path}] ~ {line}")

                try:
                    command, args = parse(line)

                    self.process(command, args)
                except UnknownCommand as e:
                    tprint(str(e))
                    with_error = True
                    break
                
                time.sleep(1)
                
            tprint(f"=== Start script execution completed {'with error' if with_error else 'successfuly'} ===\n")

    def _mainloop(self) -> None:
        while True:
            try:
                user_input = input(f"{self.Meta.USERNAME}@{self.Meta.NAME} OS [{self.current_path}] ~ ")
            except (EOFError, KeyboardInterrupt):
                tprint("\nShutting down...")
                return

            command, args = parse(user_input)

            try:
                if not self.process(command, args):
                    break
            except UnknownCommand as e:
                tprint(str(e))

    def run(self) -> None:
        if self.start_script:
            self._run_start_script(self.start_script)

        self._mainloop()

    def load_vfs(self, path: Path) -> None:
        try:
            tprint("loading vfs")

            tree = ET.parse(path)
            root = tree.getroot()

            if root.tag != "vfs":
                tprint("Error: Invalid VFS file format.")
                return
            
            root_dir = root.find('dir', namespaces={'name': 'root'})

            if root_dir.attrib.get('name') != 'root':
                tprint("Error: VFS root directory not found.")
                return
            
            try:
                self.vfs_root = self._parse_vfs_element(root_dir)
            except Exception as e:
                tprint(f"Error parsing VFS: {e}")
                return
            
            if self.vfs_root == {}:
                tprint("Error: VFS root directory is empty or malformed.")
                return

            print(self.vfs_root)

        except FileNotFoundError:
            tprint("Error: VFS file not found.")
            return
        
    def _parse_vfs_element(self, element: ET.Element):
        if element is None:
            raise BrokenFormat("Error: VFS element is None")
        
        name = element.get('name', 'unknown')
        item = {'type': element.tag, 'name': name, 'content': {}}

        if name == 'unknown':
            raise BrokenFormat("Error: VFS element missing 'name' attribute.")

        if element.tag == 'dir':
            for child in element:
                child_data = self._parse_vfs_element(child)
                item['content'][child_data['name']] = child_data
        elif element.tag == 'file':
            data = element.text or ''
            encoding = element.get('encoding')

            if encoding == 'base64':
                try:
                    item['content']= base64.b64decode(data).decode('utf-8', errors='ignore')
                except Exception as e:
                    print(e)
            else:
                item['content'] = data

        return item