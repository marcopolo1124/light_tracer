class Node:
    def __init__(self, data=None):
        self.data = data
        self.pointer_1 = None
        self.pointer_2 = None

    def add_point(self, node_1=None, node_2=None):
        self.pointer_1 = node_1
        self.pointer_2 = node_2
    
    def __repr__(self):
        return f"data: {self.data}"


class BinTree:
    def __init__(self, head_node):
        self.head_node = head_node
    
    def traverse(self, node=0):
        if node == 0:
            node = self.head_node
        if node is None:
            return []
        
        left_node = node.pointer_1
        right_node = node.pointer_2

        tree = [node]
        tree += self.traverse(left_node)
        tree += self.traverse(right_node)
        return tree
    
    def get_data_list(self):
        tree = self.traverse()
        data_list = [node.data if node is not None else None for node in tree]
        return data_list
    
    def search_generation(self, generation=0):
        if generation == 0:
            return self.head_node

        current_generation_list = [self.head_node]
        next_generation_list = []
        for i in range(generation):
            for node in current_generation_list:
                if node is not None:
                    next_generation_list.append(node.pointer_1)
                    next_generation_list.append(node.pointer_2)
            current_generation_list = next_generation_list.copy()
            next_generation_list = []
        generation_list = [node.data if node is not None else None for node in current_generation_list]
        return generation_list
