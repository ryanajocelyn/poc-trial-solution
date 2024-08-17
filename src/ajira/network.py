"""
Network

"""

from node import Node


class Network:
    node_map = {}

    def add_node(self, node_name, node_type='COMPUTER'):
        node = Node(node_name, node_type)
        self.node_map[node_name] = node

    def connect_node(self, node_name1, node_name2):
        node1 = self.node_map[node_name1]
        node2 = self.node_map[node_name2]

        node1.add(node2)
        node2.add(node1)

    def info_route(self, node_name1, node_name2):
        node1 = self.node_map[node_name1]
        node2 = self.node_map[node_name2]

        path_route = []
        visited_nodes = set()
        path = self.node_traverse(path_route, visited_nodes, node1, node2)
        print(path_route)

    def node_traverse(self, path_route, visited_nodes, curr_node, end_node):
        path_route.append(curr_node)
        visited_nodes.add(curr_node)

        if curr_node == end_node:
            return ""

        if curr_node.children:
            for child in curr_node.children:
                if child not in visited_nodes:
                    self.node_traverse(path_route, visited_nodes, child, end_node)

            if path_route[-1] != end_node:
                path_route.pop()

        return ""
