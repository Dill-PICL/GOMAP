import logging, sys, os, time
from mpi4py import MPI
from pyrocopy import pyrocopy
from iprs_utils import run_iprs
from natsort import natsorted
from pprint import pprint

WORKTAG = 0
DIETAG = 1

class Work():
    def __init__(self, work_items):
        self.work_items = natsorted(work_items[:])
 
    def get_next_item(self):
        if len(self.work_items) == 0:
            return None
        return self.work_items.pop()

def master(wi):
    all_data = []
    size = MPI.COMM_WORLD.Get_size()
    current_work = Work(wi) 
    comm = MPI.COMM_WORLD
    status = MPI.Status()
    for i in range(1, size): 
        anext = current_work.get_next_item() 
        if not anext: break
        comm.send(anext, dest=i, tag=WORKTAG)
 
    while 1:
        anext = current_work.get_next_item()
        if not anext: break
        data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
        comm.send(anext, dest=status.Get_source(), tag=WORKTAG)
        time.sleep(5)
    
    for i in range(1,size):
        comm.send(None, dest=i, tag=DIETAG)

def slave(config):
    comm = MPI.COMM_WORLD
    status = MPI.Status()
    while 1:
        data = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
        if status.Get_tag(): break
        print("Running IPRS for %s" % (data))
        iprs_loc="/tmpdir"
        run_iprs(data,config,iprs_loc)
        comm.send(data, dest=0)

def run_mpi_iprs(fa_files,config):
    
    size = MPI.COMM_WORLD.Get_size()
    rank = MPI.COMM_WORLD.Get_rank()
    name = MPI.Get_processor_name()

    print("Hello World! \n I am process %d of %d on %s." % (rank, size, name))
    iprs_src=config["software"]["iprs"]["path"]
    if "tmpdir" in config["input"]:
        tmpdir=config["input"]["tmpdir"]
    else:
        tmpdir="/tmpdir"
    
    src=iprs_src
    dest=tmpdir+"/"

    print(src + " " + dest)

    work_list = natsorted(fa_files)
    
    if rank == 0:
        all_dat = master(work_list)
    else:
        results = pyrocopy.copy(src,dest)
        pprint(results)
        slave(config)
        
        
