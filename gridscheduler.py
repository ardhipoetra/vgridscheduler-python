import Pyro4
import threading
import serpent
from node import Node
from resourcemanager import ResourceManager
from constant import Constant
import utils
import time
import signal
import sys
from operator import attrgetter
stop = True

class GridScheduler(Node):

    # list of jobs that waiting
    job_queue = []

    # id RM, load per RM/cluster
    RM_loads = [(1,0.8), (2, 0.4)]
    #RM_loads = []
    gs_URI = ""

    ## specify the current status of the neighbouring GS it containss the URI and TRUE/FALSE (functioning/non functioning)details
    neighbor_state = [("URI","FALSE")] 
    # id RM, jobs on that cluster-RM
    jobs_assigned_RM = [(1, ["job1", "job2"]), (2, ["jobA", "jobC"])]

    # every GS store everyone's state, except himself, maybe. including timestamp
    neighbor_stateGS = [(123, 1, "stateGS1"), (41, 3, "stateGS3")]

   ## Define the data structure which maintains the state of each GS
    def __init__(self, oid, name="GS"):
        Node.__init__(self, oid, name)
        print 'gs %s created with id %d' %(name, oid)

        self.RM_loads = [(i, 0.0) for i in range(Constant.TOTAL_RM)] #rm connected in this

    # report received after finishing the task from RM
    def receivereport(self, details, d_report):
        detobj = Pyro4.Proxy(details)
        report = serpent.loads(d_report)

        print '%s received report %s from %s' %(self,report,detobj.tostr())

    # add job to this GS
    def addjob(self, d_job, uri):
        job = serpent.loads(d_job)
        self.job_queue.append(job)

        # should do something
        gs_URI = uri 
        jobsub = self._choose_job()
        print "sulabh"
        self._monitorneighborGS()
        rmidsub = self._chooseRM()

        if rmidsub == -1 :
            print 'no rm!'
            return False
        else:
            jobsub["RM_assigned"] = rmidsub
            self._assignjob(rmidsub, serpent.dumps(jobsub))
        return True

    # handle when retrieving state from other GS
    def get_structure(self, id_GS, structureObj):
        return True;

    # get the current status of the cluster AND RM in his jurisdiction
    # activity: return the data structure containing the deails such as how many nodes are avaiable, current workload in the network etc
    # output: data structure for the cluster status from the perticular cluster
    def getclusterstatus(self, rmobject):
        return True

    # assign job to RM
    def _assignjob(self, rmid, d_job):
        job = serpent.loads(d_job)

        print '%s assigned job %s' % (self,job)

        ns = Pyro4.locateNS()
        uri = ns.lookup(Constant.NAMESPACE_RM+"."+"[RM-"+str(rmid)+"]"+str(rmid))
        rmobj = Pyro4.Proxy(uri)

        print 'send job to %s' % (rmobj.tostr())
        rmobj.add_job(d_job)

    # GS choose job
    def _choose_job(self):
        job = self.job_queue.pop()
        return job

    def _chooseRM(self):
        ns = Pyro4.locateNS()
        for rm, rm_uri in ns.list(prefix=Constant.NAMESPACE_RM+".").items():
            rmobj = Pyro4.Proxy(rm_uri)
            self.RM_loads.append(rmobj.get_workloadRM())

        x = sorted(self.RM_loads, key = lambda x : x[1])
        print x
        if x[0][1] < 0.9 :    
            return(x[0][0])

        return -1        


    # Inform about the RM who has started executing the job
    # Might not be required purpose was that central GS keep rack of all the Jobs and where they are running
    #def _update_jobdetailsRM(self): # to be honest I don't understand this function
        return True

    # Update the data structure for consistency/replication to designated distributed GS (neighbor) -> create snapshot
    def _update_GSstructure(self):
        return False

    # push current structure to other GS (consistency)
    def _push_structure(self):
        return True

    # monitor GS to handle fault in GS
    def _monitorneighborGS(self):
        ns = Pyro4.locateNS()
        for gs, gs_uri in ns.list(prefix=Constant.NAMESPACE_GS+".").items():
            
            if gs_uri == self.gs_URI :
                continue
            gsobj = Pyro4.Proxy(gs_uri)
            self.neighbor_state.append(gsobj.get_gs_neighbour_status())


        return self.neighbor_state;


    def get_gs_neighbour_status(self):
        return (str(self.gs_URI),"TRUE")

    # monitor RM to handle fault in RM
    # This function might not be required
    def _monitorRM(self):
        ns = Pyro4.locateNS()
        for rm, rm_uri in ns.list(prefix=Constant.NAMESPACE_RM+".").items():
            rmobj = Pyro4.Proxy(rm_uri)
            rmobj.get_statusRM()

        return True;

def check_stop():
    return stop

def main():
    # g_sch = GridScheduler()
    ns = Pyro4.locateNS()

    if len(sys.argv) == 0:
        oid = len(ns.list(prefix=Constant.NAMESPACE_GS+"."))
    else:
        oid = int(sys.argv[1])

    node = GridScheduler(oid, "[GS-"+str(oid)+"]")

    daemon = Pyro4.Daemon()
    uri = daemon.register(node)
    node.seturi(uri)

    ns.register(Constant.NAMESPACE_GS+"."+node.getname()+str(oid), uri)

    def signal_handler(signal, frame):
        print('You pressed Ctrl+C on GS!')
        stop = False
        daemon.shutdown()

    signal.signal(signal.SIGINT, signal_handler)

    try:
        daemon.requestLoop(loopCondition=check_stop)
    finally:
        ns.remove(name=Constant.NAMESPACE_GS+"."+node.getname()+str(oid))



if __name__=="__main__":
    main()
