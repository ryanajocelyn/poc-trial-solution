"""
Ajira Network Main file

"""

from network import Network


def network1():
    network = Network()

    network.add_node('C1')
    network.add_node('C2')
    network.add_node('C3')
    network.add_node('C4')
    network.add_node('C5')
    network.add_node('C6')
    network.add_node('C7')

    network.add_node('R1')

    network.connect_node('C1', 'C2')
    network.connect_node('C1', 'C3')
    network.connect_node('C3', 'R1')
    network.connect_node('R1', 'C4')
    network.connect_node('C4', 'C5')
    network.connect_node('C4', 'C6')
    network.connect_node('C6', 'C7')

    network.info_route('C1', 'C6')
    network.info_route('C7', 'C5')
    network.info_route('C7', 'C2')


def network2():
    network = Network()

    network.add_node('C1')
    network.add_node('C2')
    network.add_node('C3')
    network.add_node('C4')
    network.add_node('C5')

    network.add_node('R1')
    network.add_node('R2')

    network.connect_node('C1', 'C2')
    network.connect_node('C1', 'R1')
    network.connect_node('C2', 'R2')
    network.connect_node('R2', 'C4')
    network.connect_node('C4', 'R1')
    network.connect_node('C4', 'C5')
    network.connect_node('R1', 'C3')

    network.info_route('C1', 'C3')
    network.info_route('C3', 'C4')
    network.info_route('C5', 'C3')


if __name__ == '__main__':

    network1()

    network2()
