"""
Delete the node at a given position in a linked list and return a reference to the head node.
The head is at position 0.
The list may be empty after you delete the node. In that case, return a null value.

Example
list = 0 -> 1 -> 2 -> 3
position = 2

After removing the node at position 2
list = 0 -> 1 -> 3

"""

from .linked_list import SinglyLinkedListNode;


def delete_node(head, position):
    head.data


if __name__ == '__main__':

    linked_list = SinglyLinkedListNode()
    linked_list.append(1)
    linked_list.append(2)
    linked_list.append(3)

    delete_node(linked_list, 2)
