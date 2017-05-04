"""
Example topology of Quagga routers
"""

import inspect
import os
from mininext.topo import Topo
from mininext.services.quagga import QuaggaService

from collections import namedtuple

QuaggaHost = namedtuple("QuaggaHost", "name ip loIP")
net = None


class QuaggaTopo(Topo):

    "Creates a topology of Quagga routers"

    def __init__(self):
        """Initialize a Quagga topology with 5 routers, configure their IP
           addresses, loop back interfaces, and paths to their private
           configuration directories."""
        Topo.__init__(self)

        # Directory where this file / script is located"
        selfPath = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe())))  # script directory

        # Initialize a service helper for Quagga with default options
        quaggaSvc = QuaggaService(autoStop=False)

        # Path configurations for mounts
        quaggaBaseConfigPath = selfPath + '/configs/'

        # List of Quagga host configs
        quaggaHosts = []
        quaggaHosts.append(QuaggaHost(name='R1', ip='172.0.1.1/16',
                                      loIP='10.0.1.1/24'))
        quaggaHosts.append(QuaggaHost(name='R2', ip='172.0.2.1/16',
                                      loIP='10.0.2.1/24'))
        quaggaHosts.append(QuaggaHost(name='R3', ip='172.0.3.2/16',
                                      loIP='10.0.3.1/24'))
        quaggaHosts.append(QuaggaHost(name='R4', ip='172.0.4.1/16',
                                      loIP='10.0.4.1/24'))
        quaggaHosts.append(QuaggaHost(name='H1', ip='172.0.5.1/16',
                                      loIP='10.0.5.1/24'))
        quaggaHosts.append(QuaggaHost(name='H2', ip='172.0.6.1/16',
                                      loIP='10.0.6.1/24'))
        # Add switch for IXP fabric
        # ixpfabric = self.addSwitch('fabric-sw1')

        # Setup each Quagga router, add a link between it and the IXP fabric
        for host in quaggaHosts:
            # Create an instance of a host, called a quaggaContainer
            quaggaContainer = self.addHost(name=host.name,
                                           ip=host.ip,
                                           hostname=host.name,
                                           privateLogDir=True,
                                           privateRunDir=True,
                                           inMountNamespace=True,
                                           inPIDNamespace=True,
                                           inUTSNamespace=True)

            # Add a loopback interface with an IP in router's announced range
            self.addNodeLoopbackIntf(node=host.name, ip=host.loIP)

            # Configure and setup the Quagga service for this node
            quaggaSvcConfig = \
                	{'quaggaConfigPath': quaggaBaseConfigPath + host.name}
            self.addNodeService(node=host.name, service=quaggaSvc,
                                nodeConfig=quaggaSvcConfig)

            # Attach the quaggaContainer to the IXP Fabric Switch
	    # if host != quaggaHosts[0]:
            #	self.addLink(quaggaContainer, self.hosts(sort=False)[0])
	self.addLink(self.hosts()[0],self.hosts()[2])
	self.addLink(self.hosts()[2],self.hosts()[3])
	self.addLink(self.hosts()[2],self.hosts()[4])
	self.addLink(self.hosts()[3],self.hosts()[5])
	self.addLink(self.hosts()[4],self.hosts()[5])
	self.addLink(self.hosts()[1],self.hosts()[5])
	
