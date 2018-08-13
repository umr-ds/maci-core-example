### NOTE: MAKE SURE iperf IS INSTALLED FOR THIS EXAMPLE

import framework

from core.emulator.coreemu import CoreEmu
from core.emulator.emudata import IpPrefixes
from core.enumerations import NodeTypes, EventTypes

if __name__ == '__main__':
    framework.start()

    # ip generator for example
    prefixes = IpPrefixes(ip4_prefix="10.83.0.0/16")

    # create emulator instance for creating sessions and utility methods
    coreemu = CoreEmu()
    session = coreemu.create_session()

    # must be in configuration state for nodes to start, when using "node_add" below
    session.set_state(EventTypes.CONFIGURATION_STATE)

    # create switch network node
    switch = session.add_node(_type=NodeTypes.SWITCH)

    # create nodes
    for _ in xrange(2):
        node = session.add_node()
        interface = prefixes.create_interface(node)
        session.add_link(node.objid, switch.objid, interface_one=interface)

    # instantiate session
    session.instantiate()

    # get nodes to run example
    first_node = session.get_object(2)
    last_node = session.get_object(3)

    print "starting iperf server on node: %s" % first_node.name
    first_node.cmd(["iperf", "-s", "-D"])
    first_node_address = prefixes.ip4_address(first_node)
    print "node %s connecting to %s" % (last_node.name, first_node_address)
    last_node.client.icmd(["iperf", "-t", str(10), "-c", first_node_address])
    first_node.cmd(["killall", "-9", "iperf"])

    # shutdown session
    coreemu.shutdown()
    
    framework.stop()
