import logging, sys, os
from mpi4py import MPI
from pyrocopy import pyrocopy
from blast_utils import check_bl_out, run_blast

size = MPI.COMM_WORLD.Get_size()
rank = MPI.COMM_WORLD.Get_rank()
name = MPI.Get_processor_name()

def run_mpi_blast(fa_files,config):
    print("Hello World! \n I am process %d of %d on %s. \n" % (rank, size, name))
    print(os.environ.get('USER'))
    uniprot_db=config["data"]["mixed-method"]["preprocess"]["uniprot_db"]
    
    tmpdir=config["input"]["tmpdir"]
    src=os.path.dirname(uniprot_db)
    dest=tmpdir
    results = pyrocopy.copy(src,dest)

    chunk_size = len(fa_files)/(size)
    print(chunk_size)
    start=chunk_size*(rank)
    if rank+1 < size:
        end=chunk_size*(rank+1)
    else:
        end=len(fa_files)
    
    sel_files = fa_files[start:end]
    print(start,end)
    for fa_file in sel_files:
        print("I am process %d of %d on %s. \n" % (rank, size, name))
        run_blast(fa_file,uniprot_db,config)
