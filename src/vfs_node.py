class VFSNode():
    def __init__(self, name, is_dir = False, content = None):
        self.name = name
        self.is_dir = is_dir
        self.content = content if not is_dir else {}

    def add_child(self, node):
        if self.is_dir and node.name not in self.content:
            self.content[node.name] = node
        else:
            raise ValueError(f"Unable to add {node.name} to {self.name}")