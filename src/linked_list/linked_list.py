"""
Linked List Data Structure
"""


class SinglyLinkedList:
    head = None

    def insert_node(self, node_data, data_type="data"):
        if data_type == 'data':
            new_node = SinglyLinkedListNode()
            new_node.data = node_data
        else:
            new_node = node_data

        if self.head is None:
            self.head = new_node
        else:
            node = self.head
            while node.next is not None:
                node = node.next

            node.next = new_node

    def get_node(self, node_index):
        index = 0

        node = self.head
        while index < node_index:
            if node is None:
                break

            node = node.next
            index += 1

        return node


class SinglyLinkedListNode:
    data = 0
    next = None
