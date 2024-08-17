"""
Find the merge point in a linked list

  1
    \
     2 -- 4 -- 5
    /
  3

  Merge Point = 2
"""

from linked_list import SinglyLinkedList


def merge_point(head1, head2):

    if head1 == head2:
        return head1

    if head1.next is None:
        head1 = head2

    if head2.next is None:
        head2 = head1

    return merge_point(head1.next, head2.next)


if __name__ == '__main__':
    linked_list1 = SinglyLinkedList()
    linked_list1.insert_node(1)
    linked_list1.insert_node(2)
    linked_list1.insert_node(4)
    linked_list1.insert_node(5)

    linked_list2 = SinglyLinkedList()
    linked_list2.insert_node(3)

    node1 = linked_list1.head
    node2 = linked_list2.head

    node2.next = node1.next

    merge_node = merge_point(node1, node2)
    print (merge_node.data)
