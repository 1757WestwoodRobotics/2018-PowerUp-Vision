from networktables import NetworkTables

##############################################################################################################

def init_network_tables():
    NetworkTables.initialize(server='127.0.0.1')    # Use 127.0.0.1 for local testing, 10.17.57.2 for roboRIO
    global table
    table = NetworkTables.getTable('Jetson')


##############################################################################################################

def read_network_value(key):

    return table.getEntry(key)


##############################################################################################################
# from command prompt enter the "outline viewer" directory type "gradlew run"

def publish_network_value(key, value):
    table.putValue(key, value)

##############################################################################################################

# Small test script to run. Needs time to connect and publish data.
while True:
    init_network_tables()
    read_network_value('Test')
    publish_network_value('ABC', 104.5)

