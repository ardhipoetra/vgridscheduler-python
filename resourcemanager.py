import Pyro4
import serpent
from node import Node

class ResourceManager(Node):
    def __init__(self, oid, name="RM"):
        Node.__init__(self, oid, name)
        print 'rm %s created with id %d' %(name, oid)

    def assignjob(self, assignee, d_job):

    	ns = Pyro4.locateNS()
    	asgn = Pyro4.Proxy(assignee)

        job = serpent.loads(d_job)
    	print '%s got job %s from %s' %(self, job, asgn.tostr())

    	asgn.receivereport(self.uri, d_job)
