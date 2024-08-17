"""
Swap nodes.

"""


class Node:
    data = 0
    left = None
    right = None

    def __init__(self, data):
        self.data = data


def populate_node(curr_node, indexes, depth):
    node = indexes[depth]
    if node[0] != -1:
        curr_node.left = Node(node[0])
        populate_node(curr_node.left, indexes, depth + 1)

    if node[1] != -1:
        curr_node.right = Node(node[1])
        populate_node(curr_node.right, indexes, depth + 2)


def print_node(node, visited_nodes):
    has_visited = node.data in visited_nodes
    if node.left is None:
        if has_visited is False:
            print(node.data)

        visited_nodes.append(node.data)
    else:
        print_node(node.left, visited_nodes)

    has_visited = node.data in visited_nodes
    if has_visited is False:
        visited_nodes.append(node.data)
        print(node.data)

    if node.right is not None:
        print_node(node.right, visited_nodes)


def swap_nodes_at_depth(head, queries):
    pass


def swap_nodes(indexes, queries):
    ret_path = []

    head = Node(1)
    populate_node(head, indexes, depth=0)

    swap_nodes_at_depth(head, queries)

    print_node(head, visited_nodes=[])

    return ret_path


if __name__ == '__main__':
    ind = [[2, 3], [-1, 4], [-1, 5], [-1, -1], [-1, -1]]
    query = [2]
    path = swap_nodes(ind, query)

    print(path)
