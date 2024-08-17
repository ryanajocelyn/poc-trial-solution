"""
Node Class
"""


class Node:
    name = None
    type = None
    children = None

    def __init__(self, name, node_type="COMPUTER"):
        self.name = name
        self.type = node_type
        self.children = []

    def add(self, node):
        self.children.append(node)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
