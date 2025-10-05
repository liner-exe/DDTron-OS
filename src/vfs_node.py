class VFSNode():
    def __init__(self, name, is_dir = False, content = None, parent = None):
        self.name = name
        self.is_dir = is_dir
        self.content = content if not is_dir else {}
        self.parent = parent

    def add_child(self, node) -> None:
        if self.is_dir and node.name not in self.content:
            self.content[node.name] = node
        else:
            raise ValueError(f"Unable to add {node.name} to {self.name}")
        
    def get_parent(self):
        return self.parent
    
    def get_directories(self) -> list:
        if not self.is_dir:
            return []
        
        directories = []
        for node in self.content.values():
            if node.is_dir:
                directories.append(node)

        return directories
    
    def get_files(self) -> list:
        if not self.is_dir:
            return []
        
        files = []
        for node in self.content.values():
            if not node.is_dir:
                files.append(node)

        return files