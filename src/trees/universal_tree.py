"""
Print the number of universal trees
        3
      /   \
     3     3
     
"""


class Node:
    data = 0
    left = None
    right = None


def unival(node):
    if node.left is None and node.right is None:
        return 1

    u_cnt = unival(node.left) + unival(node.right)
    if node.left is not None and node.right is not None:
        if node.data == node.left.data and node.data == node.right.data:
            u_cnt += 1

    return u_cnt


if __name__ == '__main__':
    head = Node()
    head.left = Node()
    head.left.data = 1

    head.right = Node()

    head.right.right = Node()

    head.right.right.left = Node()
    head.right.right.right = Node()

    head.right.left = Node()
    head.right.left.data = 1

    head.right.left.left = Node()
    head.right.left.left.data = 1

    head.right.left.right = Node()
    head.right.left.right.data = 1

    un_cnt = unival(head)
    print (un_cnt)
