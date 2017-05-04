#!/usr/bin/python

"""
Example network of Quagga routers
(QuaggaTopo + QuaggaService)
"""

import sys
import atexit

# patch isShellBuiltin
import mininet.util
import mininext.util
mininet.util.isShellBuiltin = mininext.util.isShellBuiltin
sys.modules['mininet.util'] = mininet.util

from mininet.util import dumpNodeConnections
from mininet.node import OVSController
from mininet.log import setLogLevel, info

from mininext.cli import CLI
from mininext.net import MiniNExT

from topo import QuaggaTopo

net = None

def startNetwork():
    "instantiates a topo, then starts the network and prints debug information"
    cmdFile = open('./cmd.log','r')
    info('** Creating Quagga network topology\n')
    topo = QuaggaTopo()

    info('** Starting the network\n')
    global net
    net = MiniNExT(topo, controller=OVSController)
    net.start()

    info('** Dumping host connections\n')
    dumpNodeConnections(net.hosts)
    
    H1 = net.get('H1')
    H2 = net.get('H2')
    R1 = net.get('R1')
    R2 = net.get('R2')
    R3 = net.get('R3')
    R4 = net.get('R4')
    for mycmd in cmdFile:
	print mycmd[8:mycmd.rfind('\'')]
	if 'H1.' in mycmd:
	    H1.cmd(mycmd[8:mycmd.rfind('\'')])	
	if 'H2.' in mycmd:
	    H2.cmd(mycmd[8:mycmd.rfind('\'')])	
	if 'R1.' in mycmd:
	    R1.cmd(mycmd[8:mycmd.rfind('\'')])	
	if 'R2.' in mycmd:
	    R2.cmd(mycmd[8:mycmd.rfind('\'')])	
	if 'R3.' in mycmd:
	    R3.cmd(mycmd[8:mycmd.rfind('\'')])	
	if 'R4.' in mycmd:
	    R4.cmd(mycmd[8:mycmd.rfind('\'')])	

    info('** Dumping host processes\n')
    for host in net.hosts:
        host.cmdPrint("ps aux")

    info('** Running CLI\n')
    CLI(net)


def stopNetwork():
    "stops a network (only called on a forced cleanup)"

    if net is not None:
        info('** Tearing down Quagga network\n')
        net.stop()

if __name__ == '__main__':
    # Force cleanup on exit by registering a cleanup function
    atexit.register(stopNetwork)

    # Tell mininet to print useful information
    setLogLevel('info')
    startNetwork()
