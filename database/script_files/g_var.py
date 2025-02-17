#!/usr/bin/env python3

import os, sys
from time import gmtime, strftime
import distutils.spawn
import argparse


parser = argparse.ArgumentParser(description='Converts CG representation into an atomistic representation', epilog='Enjoy the program and best of luck!\n', allow_abbrev=True)
parser.add_argument('-c', help='coarse grain coordinates',metavar='pdb/gro/tpr',type=str, required=True)
parser.add_argument('-a', help='atomistic coordinates',metavar='pdb/gro/tpr',type=str)
parser.add_argument('-v', action="count", default=0, help="increase output verbosity (eg -vv, 3 levels)")
parser.add_argument('-ter', help='interactively choose terminal species', action='store_true')
parser.add_argument('-clean', help='removes all part files from build', action='store_true')
# parser.add_argument('-chains', help='list of chains to rigid body fit together, starts at chain 0',metavar='1 2',type=int, nargs='*')
parser.add_argument('-w', help='choose your solvent, common choices are: tip3p, tip4p, spc and spce. This is optional',metavar='tip3p',type=str)
parser.add_argument('-ff', help='choose your forcefield. This is optional',metavar='charmm36',type=str)
parser.add_argument('-fg', help='choose your fragment library. This is optional',metavar='charmm36',type=str, nargs='*')
parser.add_argument('-gromacs', help='gromacs executable name',metavar='gmx_avx',type=str)
args = parser.parse_args()
options = vars(args)


c, a, v, ter, clean, w, ff, fg= args.c, args.a, args.v , args.ter, args.clean, args.w, args.ff, args.fg

timestamp =  strftime("%Y-%m-%d_%H-%M-%S", gmtime())
start_dir=os.getcwd()+'/'  ### initial working directory
working_dir=os.getcwd()+'/CG2AT_'+timestamp+'/'   ### working directory 
final_dir=os.getcwd()+'/CG2AT_'+timestamp+'/FINAL/'  ### final directory for run files
input_directory=os.getcwd()+'/CG2AT_'+timestamp+'/INPUT/'  ### contains input run files
database_dir=os.path.dirname(os.path.realpath(__file__))+'/../'

pdbline = "ATOM  %5d %4s %4s%1s%4d    %8.3f%8.3f%8.3f%6.2f%6.2f"
mass = {'H': 0,'C': 12,'N': 14,'O': 16,'P': 31,'M': 0, 'B': 32 ,'S': 32} 
aas = {'ALA':'A', 'ARG':'R', 'ASN':'N', 'ASP':'D', 'CYS':'C', 'GLN':'Q', 'GLU':'E', 
       'GLY':'G', 'HIS':'H', 'ILE':'I', 'LEU':'L', 'LYS':'K', 'MET':'M', 'PHE':'F', 
       'PRO':'P', 'SER':'S', 'THR':'T', 'TRP':'W', 'TYR':'Y', 'VAL':'V'}


### finds gromacs installation

gmx=None
if args.gromacs != None:
    gmx=distutils.spawn.find_executable(args.gromacs)
if gmx==None:
    for root, dirs, files in os.walk(os.environ.get("GMXBIN")):
        for gro_type in files:
            if '.' not in gro_type and gro_type.islower():
                gmx=distutils.spawn.find_executable(gro_type)
                if gmx != None:
                    break
        break
    if gmx == None:
        sys.exit('Cannot find gromacs installation')
