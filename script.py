### ENV int mean_bw "The mean bandwidth at the bottleneck"
### ENV int delay "The delay per link"

import framework

from core.emulator.coreemu import CoreEmu
from core.emulator.emudata import IpPrefixes, LinkOptions
from core.enumerations import NodeTypes, EventTypes

def iperf(source, destination):
    dst_address = prefixes.ip4_address(first_node)
    print "Starting iperf to %s" % str(dst_address)
    
    destination.cmd('iperf -s -i 1 -y C > server.log &')
    source.client.icmd('iperf -c ' + str(dst_address) + ' -t 10 > client.log')
    framework.addLogfile("server.log")
    framework.addLogfile("client.log")

    print "Done. Parsing log now."
    
    server = open('server.log', 'r')
    bwsamples = []
    minTimestamp = None
    for line in server:
        # 20160622002425,10.0.0.2,5001,10.0.0.1,39345,4,0.0-1.0,14280,114240
        matchObj = re.match(r'(.*),(.*),(.*),(.*),(.*),(.*),(.*),(.*),(.*)', line, re.M)
        if matchObj:
            timestamp = float(matchObj.group(1))
            bwsample = float(matchObj.group(9)) / 1000.0 / 1000.0 # bits per second -> MBit
            bwsamples.append(bwsample)
            if minTimestamp is None:
                minTimestamp = timestamp
            framework.record("iperf_mbit_over_time", bwsample, timestamp - minTimestamp)
    framework.record("iperf_mbit_avg", sum(bwsamples) / len(bwsamples), offset=5)

if __name__ == '__main__':
    framework.start()

    print "Starting Experiment"

    # ip generator for example
    prefixes = IpPrefixes(ip4_prefix="10.83.0.0/16")

    # create emulator instance for creating sessions and utility methods
    coreemu = CoreEmu()
    session = coreemu.create_session()

    # must be in configuration state for nodes to start, when using "node_add" below
    session.set_state(EventTypes.CONFIGURATION_STATE)

    # create switch network node
    switch = session.add_node(_type=NodeTypes.SWITCH)

    print "Everything is set up now."

    # create nodes
    for _ in xrange(2):
        node = session.add_node()
        interface = prefixes.create_interface(node)
        link_opts = LinkOptions()
        link_opts.delay = {{delay}}
        link_opts.bandwidth = {{mean_bw}}
        session.add_link(node.objid,
            switch.objid,
            interface_one=interface,
            link_options=link_opts)

    print "Links are set up."

    # instantiate session
    session.instantiate()

    # get nodes to run example
    first_node = session.get_object(2)
    last_node = session.get_object(3)

    iperf(first_node, last_node)

    # shutdown session
    coreemu.shutdown()

    print "Done. Stopping simulation."
    
    framework.stop()
