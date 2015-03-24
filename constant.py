
class Constant(object):

	IP_GS_NS = "localhost"
	IP_RM_NS = "localhost"

	TOTAL_GS = 2
	TOTAL_RM = 3
	TOTAL_NODE = TOTAL_RM * 4
	TOTAL_NODE_EACH = 4

	NUMBER_OF_JOBS = 100

	WORKER_STATUS_IDLE = 0
	WORKER_STATUS_BUSY = 1

	NODE_WORKER = "workernode"
	NODE_RESOURCEMANAGER = "RMnode"
	NODE_GRIDSCHEDULER = "GSnode"

	NAMESPACE_RM = "rd.vgs.resourcemanager"
	NAMESPACE_GS = "rd.vgs.gridscheduler"
	NAMESPACE_WK = "rd.vgs.workernode"
