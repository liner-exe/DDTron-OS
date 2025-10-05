from parser import parse
from pathlib import Path
import time
import xml.etree.ElementTree as ET
import base64

from exceptions import UnknownCommand, BrokenFormat
from utils import tprint
from vfs_node import VFSNode

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
        self.filesystem_support = False

        self.startup()

        if self.debug:
            self._debug_print()

        if self.vfs_path:
            self.filesystem_support = self.load_vfs(self.vfs_path)
        
    def startup(self) -> None:
        tprint(self.art, delay=0.001)
        tprint(f"{self.Meta.NAME} OS v{self.Meta.VERSION_MAJOR}.{self.Meta.VERSION_MINOR} ({self.Meta.SYSTEM_TYPE})")
        tprint(f"Kernel {self.Meta.VERSION_MAJOR}.{self.Meta.VERSION_MINOR}-{self.Meta.NAME} on VM\n")
        tprint(f"Welcome to {self.Meta.NAME} OS!\n")

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
        if not self.filesystem_support:
            tprint("Critical: System won't run without filesystem.")
            return

        if self.start_script:
            self._run_start_script(self.start_script)

        self._mainloop()

    def load_vfs(self, path: Path) -> bool:
        tprint(f"loading vfs from {path}")

        if not path.exists:
            tprint(f"Error: VFS file {path} not found.")
            return False

        try:
            tree = ET.parse(path)
            root = tree.getroot()
        except ET.ParseError as e:
            tprint(f"Error: Invalid XML format: {e}")
            return False

        if root.tag != "vfs":
            tprint("Error: VFS root element must be <vfs>.")
            return False
        
        if len(root) == 0:
            tprint('Error: <vfs> element is empty. Expected <dir name="root"> inside.')
            return False
        
        first_child = root[0]
        if first_child.tag != "dir" or first_child.attrib.get("name") != "root":
            print(first_child)
            tprint('Error: Expected <dir name="root"> directly inside <vfs> element.')
            return False
        
        try:
            self.vfs_root = self._parse_vfs_element(first_child)
        except BrokenFormat as e:
            tprint(str(e))
            return False
        except Exception as e:
            tprint(f"Error parsing VFS: {e}")
            return False
        
        if not self.vfs_root or not self.vfs_root.content:
            tprint("Error: VFS root directory is empty or malformed.")
            return False

        tprint("VFS successfully loaded.\n")
        
        return True
        
    def _parse_vfs_element(self, element: ET.Element):
        if element is None:
            raise BrokenFormat("Error: VFS element is None")

        if element.tag == 'dir':
            node = VFSNode(element.attrib["name"], is_dir=True)
            for child in element:
                node.add_child(self._parse_vfs_element(child))
            return node
        elif element.tag == 'file':
            encoding = element.get('encoding')
            data = element.text.strip() or ''

            if encoding == 'base64':
                try:
                    data = base64.b64decode(data).decode(errors="ignore")
                except:
                    data = f"Failed to decode data: {data}"
            
            return VFSNode(element.attrib["name"], content=data)
