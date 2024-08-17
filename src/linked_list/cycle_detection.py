"""
A linked list is said to contain a cycle if any node is visited more
than once while traversing the list. Given a pointer to the head of a linked list,
determine if it contains a cycle. If it does, return 1. Otherwise, return 0.

Example

 head refers to the list of nodes 1 -> 2 -> 3 -> NULL

The numbers shown are the node numbers, not their data values.
There is no cycle in this list so return 0.

 head refers to the list of nodes 1 -> 2 -> 3 -> 1 -> NULL

There is a cycle where node 3 points back to node 1, so return 1.
"""


from linked_list import SinglyLinkedList


def has_cycle(head):
    slow = head
    fast = head

    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next

        if slow == fast:
            return 1

    return 0


if __name__ == '__main__':
    linked_list = SinglyLinkedList()
    linked_list.insert_node(1)
    linked_list.insert_node(2)
    linked_list.insert_node(3)
    linked_list.insert_node(4)
    linked_list.insert_node(5)
    linked_list.insert_node(linked_list.head.next, data_type="node")

    cycle_detect = has_cycle(linked_list.head)
    print(cycle_detect)
