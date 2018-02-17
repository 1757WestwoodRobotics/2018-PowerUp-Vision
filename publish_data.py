from networktables import NetworkTables


def init_network_tables():
    NetworkTables.initialize(server='127.0.0.1')
    global table
    table = NetworkTables.getTable('Jetson')


def read_network_value(key):
    table.getEntry(key)


def publish_network_value(key, value):
    table.putValue(key, value)


# Small test script to run. Needs time to connect and publish data.
while True:
    init_network_tables()
    read_network_value('Test')
    publish_network_value('ABC', 104.5)

