import logging, sys, os, time
from mpi4py import MPI
from pyrocopy import pyrocopy
from blast_utils import check_bl_out, run_blast
from natsort import natsorted
from pprint import pprint
from glob import glob

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

def slave(dest,config):
    comm = MPI.COMM_WORLD
    status = MPI.Status()
    while 1:
        data = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
        if status.Get_tag(): break
        uniprot_db=dest+"/"+os.path.basename(config["data"]["mixed-method"]["preprocess"]["uniprot_db"])
        print("Running BLASTP for %s against %s" % (data,uniprot_db))
        run_blast(data,uniprot_db,config)
        comm.send(data, dest=0)

def run_mpi_blast(config):
    
    size = MPI.COMM_WORLD.Get_size()
    rank = MPI.COMM_WORLD.Get_rank()
    name = MPI.Get_processor_name()

    print("Hello World! \n I am process %d of %d on %s." % (rank, size, name))
    uniprot_db=config["data"]["mixed-method"]["preprocess"]["uniprot_db"]
    if "tmpdir" in config["input"]:
        tmpdir=config["input"]["tmpdir"]
    else:
        tmpdir="/tmpdir"
    
    src=os.path.dirname(uniprot_db)
    dest=tmpdir+"/blastdb"


    if rank == 0:
        workdir=config["input"]["gomap_dir"]+"/"
        print(workdir)
        tmp_fa_dir=workdir + config["input"]["split_path"]+"/"
        dest=workdir+config["data"]["mixed-method"]["preprocess"]["blast_out"]+"/temp/"
        results = pyrocopy.copy(tmp_fa_dir,dest)
        print(results)
        fa_pattern=dest+config["input"]["basename"]+"*.fa"
        fa_files = glob(fa_pattern)
        work_list = natsorted(fa_files)
        all_dat = master(work_list)
    else:
        results = pyrocopy.copy(src,dest)
        #pprint(results)
        slave(dest,config)
