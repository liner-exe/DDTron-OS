from parser import parse
from pathlib import Path
import time
import xml.etree.ElementTree as ET
import base64

from exceptions import UnknownCommand, BrokenFormat
from utils import tprint, format_duration
from vfs_node import VFSNode

class OperatingSystem:
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
        self.startup_time = time.time()

        self.startup()

        if self.debug:
            self._debug_print()

        if self.vfs_path:
            self.filesystem_support = self.load_vfs(self.vfs_path)
            self.current_node = self.vfs_root
        
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
        elif command == "uptime":
            self.process_uptime()
        elif command == "pwd":
            self.process_pwd()
        elif command == "exit":
            self.process_exit()
            return False
        else:
            raise UnknownCommand(f"Error: Unknown command {command}")
        
        return True

    def process_cd(self, args: list) -> None:
        if len(args) == 0:
            self.current_node = self.vfs_root
            return

        if len(args) > 1:
            tprint("Error: cd requires only 1 arguement.")
            return
        
        path: str = args[0].strip()
        target_node = None

        if path.startswith('"') and path.endswith('"'):
                path = path.strip('"')

        if path == "/" or path == "root":
            target_node = self.vfs_root  
        elif path.startswith('/'):
            target_node = self._parse_path(path.lstrip('/'), start_node=self.vfs_root)
        else:
            target_node = self._parse_path(path, start_node=self.current_node)

        if target_node:
            if target_node.is_dir:
                self.current_node = target_node
            else:
                tprint(f"Error: {path} is not a directory.")
        else:
            tprint("System can't find specified path.")

    def process_ls(self, args) -> None:
        if len(args) == 0:
            tprint(self.current_node.name)

            for directory in self.current_node.get_directories():
                print(f"- {directory.name}/")

            for file in self.current_node.get_files():
                print(f"- {file.name}")
        else:
            tprint("Error: Unexpected arguements: {0}".format(' '.join(args[0:])))

    def process_uptime(self) -> None:
        uptime = time.time() - self.startup_time
        tprint(f"Current uptime {format_duration(uptime)}")

    def process_pwd(self) -> None:
        tprint(self._get_absolute_path())

    def process_exit(self) -> None:
        tprint("Shutting down...")

    def _run_start_script(self, path: Path) -> None:
        if not path.exists():
            tprint("Error: Start script path does not exist.")
            return
        
        tprint(f"=== Running start script: {path} ===")
        with_error = False

        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                tprint(f"{self.Meta.USERNAME}@{self.Meta.NAME} OS [{self._get_absolute_path()}] ~ {line}")

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
                user_input = input(f"{self.Meta.USERNAME}@{self.Meta.NAME} OS [{self._get_absolute_path()}] ~ ")
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
        
    def _parse_vfs_element(self, element: ET.Element, parent_node = None):
        if element is None:
            raise BrokenFormat("Error: VFS element is None")
        
        name = element.attrib.get("name")
        if not name:
            raise BrokenFormat(f'Error: VFS element <{element.tag}> is missing "name" attribute.')

        if element.tag == 'dir':
            node = VFSNode(element.attrib["name"], is_dir=True, parent=parent_node)
            for child in element:
                child_node = self._parse_vfs_element(child, parent_node=node)
                node.add_child(child_node)
            return node
        elif element.tag == 'file':
            encoding = element.get('encoding')
            data = element.text.strip() or ''

            if encoding == 'base64':
                try:
                    data = base64.b64decode(data).decode(errors="ignore")
                except:
                    data = f"Failed to decode data: {data}"
            
            return VFSNode(element.attrib["name"], content=data, parent=parent_node)
        else:
            raise BrokenFormat(f"Error: Unknown VFS element tag: <{element.tag}>")
        
    def _get_absolute_path(self):
        current_node = self.current_node

        if not current_node.get_parent():
            return "root"
        
        path = ""
        while (current_node.get_parent() != None):
            path = "/" + current_node.name + path
            current_node = current_node.get_parent()

        return "root" + path
    
    def _parse_path(self, path: str, start_node: VFSNode):
        if not path:
            return start_node
        
        components = [char for char in path.split('/') if char]
        current = start_node

        for component in components:
            if component == '.':
                continue
            elif component == '..':
                if current.get_parent():
                    current = current.get_parent()
                continue

            found = None
            for child in current.get_directories():
                if child.name == component:
                    found = child
                    break
            
            if found:
                current = found
            else:
                return None
        
        return current