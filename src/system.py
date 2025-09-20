from parser import parse

class OperatingSystem():
    current_path = "root"

    art = r"""
     ____  ____  _____                _____ _____ 
    |    \|    \|_   _|___ ___ ___   |     |   __|
    |  |  |  |  | | | |  _| . |   |  |  |  |__   |
    |____/|____/  |_| |_| |___|_|_|  |_____|_____|
    """

    class Meta():
        NAME: str = "DDTRon"
        VERSION_MAJOR: int = 1
        VERSION_MINOR: int = 0
        SYSTEM_TYPE: str = "x86_64"
        USERNAME: str = "user"

    def __init__(self) -> None:
        self.startup()

    def startup(self) -> None:
        print(self.art)
        print(f"{self.Meta.NAME} OS v{self.Meta.VERSION_MAJOR}.{self.Meta.VERSION_MINOR} ({self.Meta.SYSTEM_TYPE})")
        print(f"Kernel {self.Meta.VERSION_MAJOR}.{self.Meta.VERSION_MINOR}-{self.Meta.NAME} on VM\n")
        print(f"Welcome to {self.Meta.NAME} OS!")

    def process(self, command: str, args: list) -> bool:
        if command is None:
            return True

        if command == "cd":
            self.process_cd(args)
        elif command == "ls":
            self.process_ls(args)
        elif command == "exit":
            self.process_exit()
            return False
        else:
            print(f"Error: Unknown command {command}")
        
        return True

    def process_cd(self, args: list) -> None:
        print("cd " + ' '.join(args))

    def process_ls(self, args: list) -> None:
        print("ls " + ' '.join(args))

    def process_exit(self) -> None:
        print("Shutting down")

    def run(self) -> None:
        while True:
            user_input = input(f"{self.Meta.USERNAME}@{self.Meta.NAME} OS [{self.current_path}] ~ ")
            command, args = parse(user_input)

            if not self.process(command, args):
                break