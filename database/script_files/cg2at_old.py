#!/usr/bin/env python3

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__))+'/database/script_files')
import numpy as np
from subprocess import Popen, PIPE
import subprocess, shlex
from time import gmtime, strftime
import math
import multiprocessing as mp
import argparse
import copy
from shutil import copyfile
from distutils.dir_util import copy_tree
import time
from string import ascii_uppercase
from pathlib import Path
import re
import datetime
import glob
from scipy.spatial import KDTree
import difflib
sys.path.append(os.path.dirname(os.path.realpath(__file__))+'/database/script_files')
import gen
from gen import start_dir,working_dir,final_dir,input_directory,script_dir 
import gro


# parser = argparse.ArgumentParser(description='Converts CG representation into an atomistic representation', epilog='Enjoy the program and best of luck!\n', allow_abbrev=True)
# parser.add_argument('-c', help='coarse grain coordinates',metavar='pdb/gro/tpr',type=str, required=True)
# parser.add_argument('-a', help='atomistic coordinates',metavar='pdb/gro/tpr',type=str)
# parser.add_argument('-v', action="count", default=0, help="increase output verbosity (eg -vv, 3 levels)")
# parser.add_argument('-ter', help='interactively choose terminal species', action='store_true')
# parser.add_argument('-clean', help='removes all part files from build', action='store_true')
# # parser.add_argument('-chains', help='list of chains to rigid body fit together, starts at chain 0',metavar='1 2',type=int, nargs='*')
# parser.add_argument('-w', help='choose your solvent, common choices are: tip3p, tip4p, spc and spce. This is optional',metavar='tip3p',type=str)
# parser.add_argument('-ff', help='choose your forcefield. This is optional',metavar='charmm36',type=str)
# parser.add_argument('-fg', help='choose your fragment library. This is optional',metavar='charmm36',type=str, nargs='*')
# args = parser.parse_args()
# options = vars(args)


################################################################ Initialisation ##################################################################

# def collect_input():
# #### collates all input files in input directory
#     copyfile(args.c, input_directory+args.c.split('/')[-1])
#     if args.a != None:
#         copyfile(args.a, input_directory+args.a.split('/')[-1])
#     os.chdir(input_directory)
# #### converts input files into pdb files 
#     gromacs('gmx editconf -f '+args.c.split('/')[-1]+' -resnr 0 -o CG_input.pdb')
#     if args.a != None:
#         gromacs('gmx editconf -f '+args.a.split('/')[-1]+' -resnr 0 -o AT_input.pdb')
#         return True
#     return False

# def get_forcefields_from_gromacs():
# #### maybe implement fetching forcefields from gromacs install
#     gmxdat = os.environ.get("GMXDATA")
#     if gmxdat:
#         if os.path.exists(os.path.join(gmxdat,'gromacs','top')):
#             return os.path.join(gmxdat,'gromacs','top')

#         elif os.path.exists(os.path.join(gmxdat,'top')):
#             return os.path.join(gmxdat,'top')
#         else:
#             print('cannot find gromacs forcefields')
#             return False
#     else:
#         return False

# def read_database_directories():
# #### maybe implement fetching forcefields from gromacs install  
#     gromacs_directory=get_forcefields_from_gromacs()
#     gromacs_provided=[]
#     if gromacs_directory: 
#         for root, dirs, files in os.walk(gromacs_directory):
#             gromacs_provided=dirs
#             break
# #### Read in forcefields provided
#     available_provided_database=[]
#     for directory_type in ['forcefields', 'fragments']:
#         if os.path.exists(script_dir+'database/'+directory_type):
#             for root, dirs, files in os.walk(script_dir+'database/'+directory_type):
#                     available_provided=dirs
#                     break
#         else:
#             available_provided=[]

#         available_provided_database.append(available_provided)

#     if len(available_provided_database[0]) != 0 and len(available_provided_database[1]) != 0:
#         return  available_provided_database[0], available_provided_database[1]
#     else:
#         sys.exit('no '+selection_type+' found')

# def database_selection(provided, selection_type):
# #### print out selection of forcefields
#     print('\n\n{0:^45}\n'.format('Provided '+selection_type))
#     print('{0:^20}{1:^30}'.format('Selection',selection_type))
#     print('{0:^20}{1:^30}'.format('---------','----------'))
#     for force_num_prov, line in enumerate(provided):
#         print('{0:^20}{1:^30}'.format(force_num_prov,line.split('.')[0]))
#     return ask_database(provided,  selection_type)

# def ask_database(provided, selection_type):
# #### ask which database to use
#     while True:
#         try:
#             if len(provided)==1:
#                 print('\nOnly 1 '+selection_type[:-1]+' database is currently available, therefore you have no choice but to accept the following choice.')
#                 return 0
#         #### if asking about fragments accept a list of libraries 
#             if selection_type=='fragments': 
#                 number = np.array(input('\nplease select fragment libraries (in order of importance: eg. "1 0" then ENTER): ').split())
#                 number=number.astype(int)
#                 if len(number[np.where(number >= len(provided))]) == 0:
#                     return number
#         #### if forcefield only accept one selection
#             else:
#                 number = int(input('\nplease select a forcefield: '))
#                 if number < len(provided):
#                     return number
#         except KeyboardInterrupt:
#             sys.exit('\nInterrupted')
#         except:
#             print("Oops!  That was a invalid choice")


# def sort_forcefield(forcefield_available_prov, f_number):
# #### returns forcefield location and forcefield name
# #### if forcefield selection is in provided copy forcefield to FORCEFIELD and FINAL directories
#     print('\nYou have selected: '+forcefield_available_prov[f_number].split('.')[0])
#     copy_tree(script_dir+'/database/forcefields/'+forcefield_available_prov[f_number], working_dir+'FORCEFIELD/'+forcefield_available_prov[f_number]+'/.')
#     copy_tree(script_dir+'/database/forcefields/'+forcefield_available_prov[f_number], final_dir+forcefield_available_prov[f_number]+'/.')
#     return script_dir+'/database/forcefields/', forcefield_available_prov[f_number].split('.')[0]



def fetch_residues(fragments_available_prov):
#### list of directories and water types  [[root, folders...],[root, folders...]]
    np_directories, p_directories,mod_directories=[], [],[]
    try: 
        fragment_number = []
        for frag in args.fg:
            fragment_number.append(fragments_available_prov.index(frag))
    except:
        if args.fg != None: 
            print('Cannot find fragment library: '+frag+' please select library from below\n')
        fragment_number = database_selection(fragments_available_prov, 'fragments')

    if type(fragment_number) == int:
        fragment_number=[0]
#### run through selected fragments
    for database in fragment_number:
        print('\nYou have selected: '+fragments_available_prov[database])
    #### separate selection between provided and user
        location = script_dir+'database/fragments/'+ fragments_available_prov[database]
    #### runs through protein and non protein
        for directory_type in ['/non_protein/', '/protein/']:
    #### adds non protein residues locations to np_directories
            if os.path.exists(location+directory_type):
                for root, dirs, files in os.walk(location+directory_type):
                    if directory_type =='/non_protein/':
                        np_directories.append([])
                        np_directories[-1].append(root)
                        np_directories[-1]+=dirs
        #### adds protein residues locations to p_directories
                    else:
                        p_directories.append([])
                        p_directories[-1].append(root)
                        p_directories[-1]+=dirs 
                    #### adds modified residues to mod directories and removes MOD from p_directories
                        if os.path.exists(location+directory_type+'MOD/'):
                            p_directories[-1].remove('MOD')
                            p_directories.append([])
                            for root, dirs, files in os.walk(location+directory_type+'MOD/'):
                                p_directories[-1].append(root)
                                p_directories[-1]+=dirs
                                mod_directories.append([])
                                mod_directories[-1].append(root)
                                mod_directories[-1]+=dirs
                                break
                    break
    return sort_directories(p_directories, mod_directories, np_directories)             

def check_water_molecules():
    exists = False
    if args.w != None:
        for directory in np_directories:
            if os.path.exists(directory[0]+'SOL/'+args.w+'.pdb'):
                return directory[0]+'SOL/', args.w
    if not exists:
        if args.w != None:
            print('\nThe water type '+args.w+' doesn\'t exist')
        water=[]
        for directory in np_directories:
            water.append([directory[0]+'SOL/'])
            for root, dirs, files in os.walk(directory[0]+'SOL/'):
                for file in files:
                    if file.endswith('.pdb'):
                        water[-1].append(file)
                break
        print('\nPlease select a water molecule from below:\n')
        print('{0:^20}{1:^30}'.format('Selection','water_molecule'))
        print('{0:^20}{1:^30}'.format('---------','----------'))
        offset=0
        for d_val, directory in enumerate(np_directories):
            print('the following water models are found in: \n\n'+water[d_val][0]+'\n')
            for selection, water_file in enumerate(water[d_val][1:]):
                print('{0:^20}{1:^30}'.format(selection+offset,water_file.split('.')[0]))
            offset+=len(water[d_val][1:])
    while True:
        try:
            number = int(input('\nplease select a water molecule: '))
            minim = 0
            for water_val, water_selection in enumerate(water):
                if minim <= number < minim + len(water_selection):
                    return water_selection[0], water_selection[number-minim+water_val+1].split('.')[0]
                minim += len(water_selection)
        except KeyboardInterrupt:
            sys.exit('\nInterrupted')
        except:
            print("Oops!  That was a invalid choice")           

def sort_directories(p_directories, mod_directories, np_directories):
#### sorts directories alphabetically and creates residue database
    p_residues, np_residues, mod_residues = [],[],[]
    for directory in range(len(mod_directories)):
        mod_directories[directory].sort()
        mod_residues+=mod_directories[directory][1:]
    for directory in range(len(p_directories)):
        p_directories[directory].sort()
        p_residues+=p_directories[directory][1:]
    for directory in range(len(np_directories)):
        np_directories[directory].sort()
        np_residues+=np_directories[directory][1:]
#### if verbose prints all fragments found
    if args.v >= 1:
        print('\n{:-<75}'.format('>  Verbose level 1 start'))
        for directory in range(len(np_directories)):
            print('\nnon protein residues fragment directories found: \n\nroot file system\n')
            print(np_directories[directory][0],'\n\nresidues\n\n',np_directories[directory][1:], '\n')
        for directory in range(len(p_directories)):
            print('\nprotein residues fragment directories found: \n\nroot file system\n')
            print(p_directories[directory][0],'\n\nresidues\n\n',p_directories[directory][1:], '\n')
        print('\n{:-<75}'.format('>  Verbose level 1 end\n'))

    return np_residues, p_residues, mod_residues, np_directories, p_directories, mod_directories

def fetch_fragment(p_directories):
#### fetches the Backbone heavy atoms and the connectivity with pre/proceeding residues 
    
    processing={}     ### dictionary of backbone heavy atoms and connecting atoms eg backbone['ASP'][atoms/b_connect]
    for directory in range(len(p_directories)):
        for residue in p_directories[directory][1:]:    
            if residue not in processing:
                atom_list, bb_list, restraint, disulphide, terminal, dihedral=[], [], [], '', False, []
                for file_name in os.listdir(p_directories[directory][0]+residue):
                    if file_name.endswith('.pdb'):
                        with open(p_directories[directory][0]+residue+'/'+file_name, 'r') as pdb_input:
                            for line_nr, line in enumerate(pdb_input.readlines()):
                                if line.startswith('ATOM'):
                                    line_sep = pdbatom(line)
                                    if 'H' not in line_sep['atom_name']:
                                        if file_name.startswith('B'):
                                            atom_list.append(line_sep['atom_name'])    ### list of backbone heavy atoms
                                        if line_sep['backbone'] == 2:
                                            bb_list.append(line_sep['atom_name'])  ### connecting atoms
                                        if line_sep['backbone'] in [3,4,5]:
                                            restraint.append(line_sep['atom_name'])  ### position restrained atoms
                                        if line_sep['backbone'] in [5]:
                                            disulphide = line_sep['atom_name'] ### position restrained atoms
                                        if line_sep['backbone'] == 4:
                                            terminal=True
                                        if line_sep['backbone'] in [6] and file_name.startswith('B'):
                                            dihedral.append(line_sep['atom_name'])
                processing[residue]={'atoms':atom_list,'b_connect':bb_list,'restraint':restraint, 'disulphide':disulphide, 'ter':terminal, 'dihedral':dihedral}  ### adds heavy atoms and connecting atoms to backbone dictionary 
                atom_list, bb_list, restraint=[], [], []  ### resets residue lists of heavy atoms, connecting atoms and restraint 
#### if verbose prints out all heavy atoms and connecting atoms for each backbone
    if args.v >= 2:
        print('\n{:-<75}'.format('>  Verbose level 2 start'))
        print('backbone atoms for each residue and connecting atoms:\n')
        for residue in processing:
            print(residue, '\tbackbone atoms:', processing[residue]['atoms'], '\n\tbackbone connecting atoms:', processing[residue]['b_connect'], \
                '\n\trestrained atoms:', processing[residue]['restraint'],'\n\tTerminal residue:', processing[residue]['ter'],'\n\tdihedral atoms:', processing[residue]['dihedral'],'\n')
        print('\n{:-<75}'.format('>  Verbose level 2 end\n'))

    return processing

def eulerAnglesToRotationMatrix(theta) :
#### rotaion matrices for the rotation of fragments. theta is [x,y,z] in radians     
    R_x = np.array([[1,         0,                  0                   ],
                    [0,         math.cos(theta[0]), -math.sin(theta[0]) ],
                    [0,         math.sin(theta[0]), math.cos(theta[0])  ]
                    ])
         
    R_y = np.array([[math.cos(theta[1]),    0,      math.sin(theta[1])  ],
                    [0,                     1,      0                   ],
                    [-math.sin(theta[1]),   0,      math.cos(theta[1])  ]
                    ])
                 
    R_z = np.array([[math.cos(theta[2]),    -math.sin(theta[2]),    0],
                    [math.sin(theta[2]),    math.cos(theta[2]),     0],
                    [0,                     0,                      1]
                    ])
                                        
    R = np.dot(R_z, np.dot( R_y, R_x ))


    return R

#################################################################################### Initialisation end ################################################

#################################################################################### Make sections      ################################################

# def mkdir_directory(directory):
# #### checks if folder exists, if not makes folder
#     if not os.path.exists(directory):
#         os.mkdir(directory)

# def make_min(residue):#, fragments):
# #### makes minimisation folder
#     mkdir_directory('min')
# #### makes em.mdp file for each residue
#     if not os.path.exists('em_'+residue+'.mdp'):
#         with open('em_'+residue+'.mdp','w') as em:
#             em.write('define = \n integrator = steep\nnsteps = 10000\nemtol = 1000\nemstep = 0.001\ncutoff-scheme = Verlet\n')


#################################################################################### General gromacs bits #######################################
### runs gromacs commands
# def gromacs(cmd):
# #### if the flag gromacs is used every gromacs command will be printed to the terminal 
#     if args.v >= 3:
#         print('\nrunning gromacs: \n '+cmd+'\n')
#     output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     err, out = output.communicate()
#     exitcode = output.returncode
#     out=out.decode("utf-8")
# #### all gromacs outputs will be saved into gromacs_outputs within the folder it is run
#     with open('gromacs_outputs', 'a') as checks:
#         checks.write(out)
# #### standard catch for failed gromacs commands
#         if 'File input/output error:' in out:
#             sys.exit('\n'+out)
#         elif 'Error in user input:' in out:
#             sys.exit('\n'+out)
#         elif 'did not converge to Fmax ' in out:
#             sys.exit('\n'+out)
#         elif 'Segmentation fault (core dumped):' in out:
#             sys.exit('\n'+out)
#         elif 'Fatal error:' in out:
#             sys.exit('\n'+out)
#         elif 'but did not reach the requested Fmax' in out:
#             sys.exit('\n'+out)

def write_topol(residue_type, residue_number, chain):
#### open topology file
    found=False
    with open('topol_'+residue_type+chain+'.top', 'w') as topol_write:
    #### add standard headers may need to be changed dependant on forcefield
        topol_write.write('; Include forcefield parameters\n#include \"'+working_dir+'FORCEFIELD/'+forcefield+'.ff/forcefield.itp\"\n')
        if 'SOL' in cg_residues:
            topol_write.write('#include \"'+water_dir+water+'.itp\"\n\n#include \"'+working_dir+'/FORCEFIELD/'+forcefield+'.ff/ions.itp\"\n\n')
    #### add location of residue topology file absolute file locations
        if residue_type not in ['ION','SOL']:
            for directory in range(len(np_directories)):
                if os.path.exists(np_directories[directory][0]+residue_type+'/'+residue_type+'.itp'):
                    topol_write.write('#include \"'+np_directories[directory][0]+residue_type+'/'+residue_type+'.itp\"\n')
                    found=True
                    break
            if os.path.exists(working_dir+'/PROTEIN/'+residue_type+chain+'.itp'):
                topol_write.write('#include \"'+residue_type+chain+'.itp\"\n')
                found=True
            if not found:
                sys.exit('cannot find itp : '+residue_type+'/'+residue_type+chain)
    #### topology section headers
        topol_write.write('\n\n[ system ]\n; Name\nSomething clever....\n\n[ molecules ]\n; Compound        #mols\n')
    #### individual number of residues
        if residue_type.split('_')[0] == 'PROTEIN':
             residue_type='PROTEIN_'
        topol_write.write(residue_type+chain+'    '+str(residue_number))

############################################################################################## fragment rotation #################################################################################

def rotate_atom(coord, center,xyz_rot_apply):
    coord =  coord-center  #### centers COM coordinates to 0,0,0
    coord =  coord.dot(eulerAnglesToRotationMatrix([xyz_rot_apply[0],0,0]))  #### rotates coord around x
    coord =  coord.dot(eulerAnglesToRotationMatrix([0,xyz_rot_apply[1],0]))  #### rotates coord around y
    coord =  coord.dot(eulerAnglesToRotationMatrix([0,0,xyz_rot_apply[2]]))  #### rotates coord around z
    coord =  coord+center #### translates coord back by original offset
    return coord

def rotate(at_connections, cg_connections, same):
    xyz_rot_apply=[]
#### iterates through rotation matrices
    for xyz_rot in [x_rot,y_rot,z_rot]:
        dist=[]
    #### iterates through rotation matrices 
        for rot_val, rotation in enumerate(xyz_rot):
        #### applies matrix to coordinates saved as check
            check = at_connections.dot(rotation)
        #### for each connection the distance is calculated and added to list
            individual_connections=[]
            for connect in range(len(cg_connections)):
                individual_connections.append(np.sqrt(((check[connect][0]-cg_connections[connect][0])**2)+((check[connect][1]-cg_connections[connect][1])**2)+((check[connect][2]-cg_connections[connect][2])**2)))
        #### for each rotation the connection distances are added to dist list 
            dist.append(individual_connections)
    #### the RMS is calculated for each rotation    
        dist=np.array(dist)
        inter= np.sqrt(np.mean(dist**2,axis=1))
        if len(dist[0])==2 and same:
            ratio=dist/np.min(dist, axis=1)[:,np.newaxis]
            rotation_index=np.argmin(inter[np.where(np.sum(ratio, axis=1)<np.min(np.sum(ratio, axis=1))*1.02)])
            for i in range(len(ratio)):
                if np.all(ratio[i]<1.05):
                    if 'rotation_RMS' in locals():
                        if inter[i] < rotation_RMS:
                            rotation_RMS = inter[i]
                            rotation_index=i
                    else:
                        rotation_RMS=inter[i]
                        rotation_index=i
        else:
            rotation_index=np.argmin(inter)

    #### the rotation with the lowest RMS applied to the at_connections
        at_connections = at_connections.dot(xyz_rot[rotation_index])
    #### the optimal rotation is added to xyz_rot_apply list as radians
        xyz_rot_apply.append(np.radians(rotation_index*5))
    return xyz_rot_apply

#################################################################################################### PDB processing ####################################################################################

def pdbatom(line):
### get information from pdb file
### atom number, atom name, residue name,chain, resid,  x, y, z, backbone (for fragment), connect(for fragment)
    try:
        return dict([('atom_number',int(line[7:11].replace(" ", ""))),('atom_name',str(line[12:16]).replace(" ", "")),('residue_name',str(line[17:21]).replace(" ", "")),\
            ('chain',line[21]),('residue_id',int(line[22:26])), ('x',float(line[30:38])),('y',float(line[38:46])),('z',float(line[46:54])), ('backbone',int(float(line[55:61]))),\
            ('connect',int(float(line[62:67])))])
    except:
        sys.exit('\npdb line is wrong:\t'+line) 

def create_pdb(file_name):
    pdb_output = open(file_name, 'w')
    pdb_output.write('REMARK    GENERATED BY sys_setup_script\nTITLE     SELF-ASSEMBLY-MAYBE\nREMARK    Good luck\n\
'+box_vec+'MODEL        1\n')
    return pdb_output

####################################################################################################  Atomistic processing #######################################################################

def fragment_location(residue, fragment):  
#### runs through dirctories looking for the atomistic fragments returns the correct location
    if residue in p_residues:
        for directory in range(len(p_directories)):
            if os.path.exists(p_directories[directory][0]+residue+'/'+fragment):
                return p_directories[directory][0]+residue+'/'+fragment
        for directory in range(len(mod_directories)):
            if os.path.exists(mod_directories[directory][0]+residue+'/'+fragment):
                return mod_directories[directory][0]+residue+'/'+fragment
    else:
        for directory in range(len(np_directories)):
            if os.path.exists(np_directories[directory][0]+residue+'/'+fragment):
                return np_directories[directory][0]+residue+'/'+fragment
    sys.exit('cannot find fragment: '+residue+'/'+fragment)

def get_atomistic(residue,cg_fragment, cg_coord,resid):
    SF=0.8
#### find atomistic residues
    residue_list={} ## a dictionary of bead in each residue eg residue_list[atom number(1)][residue_name(ASP)/coordinates(coord)/atom name(C)/connectivity(2)/atom_mass(12)]
    frag_location=fragment_location(residue, cg_fragment+'.pdb') ### get fragment location from database
    fragment_masses=[] ### list [[coord, mass],[coord, mass]]
#### read in atomistic fragments into dictionary    
    with open(frag_location, 'r') as pdb_input:
        for line_nr, line in enumerate(pdb_input.readlines()):
            if line.startswith('ATOM'):
                line_sep = pdbatom(line) ## splits up pdb line
                residue_list[line_sep['atom_number']]={'coord':np.array([line_sep['x']*SF,line_sep['y']*SF,line_sep['z']*SF]),'atom':line_sep['atom_name'], 'res_type':line_sep['residue_name'],'extra':line_sep['backbone'], 'connect':line_sep['connect'], 'frag_mass':1}
#### updates fragment mass   
                if 'H' not in line_sep['atom_name']:
                    for atom in line_sep['atom_name']:
                        if atom in mass:
                            residue_list[line_sep['atom_number']]['frag_mass']=mass[atom]  ### updates atom masses with crude approximations
                            fragment_masses.append([line_sep['x']*SF,line_sep['y']*SF,line_sep['z']*SF,mass[atom]])
                else:
                    fragment_masses.append([line_sep['x']*SF,line_sep['y']*SF,line_sep['z']*SF,1])
    return align_at_frag_to_CG_frag(fragment_masses, cg_coord, residue_list)

def align_at_frag_to_CG_frag(fragment_masses, cg_coord, residue_list):
#### aligns atomistic fragment to cg bead
    COM_vector=np.average(np.array(fragment_masses)[:,:3], axis=0, weights=np.array(fragment_masses)[:,3])-np.array(cg_coord['coord']) ### gets vector between COM of atoms in fragment and cg bead 
    for at_id, residue in enumerate(residue_list): ### runs through atoms in fragments and centers on the cg bead 
        residue_list[residue]['coord']=residue_list[residue]['coord']-COM_vector
    return residue_list


def get_atomistic_fragments(cg_residue_type,cg_residue, cg_resid):
    at_residues={}
    connect=[]
#### runs through every in bead in residue 
    for cg_bead in cg_residue:
    #### gets atoms from database for each bead 
        at_residues[cg_bead]=get_atomistic(cg_residue_type,cg_bead, cg_residue[cg_bead], cg_resid+1)
    #### if not SOL/ION the connectivity is read from the fragment dictionary key (connect)
        if cg_residue_type not in ['SOL', 'ION']:
            for atom_num, atom in enumerate(at_residues[cg_bead]):
            #### if atom has a connection which is not zero (0 = does not connect)
                if at_residues[cg_bead][atom]['connect'] > 0:
                    connect.append([cg_bead,atom, at_residues[cg_bead][atom]['connect']]) 
    connect=np.array(connect)   
    return at_residues, connect


def connectivity(bead_number, cg_bead, connect, at_residues, cg_residues, resid):
    at_connections,cg_connections=[],[]
#### finds all beads that the cg_bead is connected to
    try:
        run=np.where(connect[:,0]==cg_bead)
    except:
        if cg_bead == 'BB':
            return [],[], cg_residues[resid][cg_bead]['coord']
        sys.exit('cannot find connectivity for :'+str(cg_bead))
#### center of mass of cg_bead
    center=cg_residues[resid][cg_bead]['coord']
#### loop through bead connections from bead of interest
    for con_test in connect[run]:
        cg_temp=[]
    #### fetch connections which have more than one bead 1 to 2 beads and not self      
        cg=connect[np.where(np.logical_and(connect[:,2]==con_test[2],connect[:,0]!=cg_bead))]
    #### for each connecting bead 
        for con_bead in cg[:,0]:
            cg_temp.append(cg_residues[resid][con_bead]['coord']-center)
    #### average position of connecting bead
        cg_connections.append(np.mean(cg_temp, axis=0))
    #### all atoms with bead connections and self. should only ever be one. 
        at = int(connect[np.where(np.logical_and(connect[:,2]==con_test[2],connect[:,0]==cg_bead))][:,1])
        at_connections.append(at_residues[cg_bead][at]['coord']-center)
    return at_connections, cg_connections, center


############################################################ Read in CG file Section ################################################################

def read_initial_pdb():
#### initialisation of dictionaries etc
    cg_residues={}  ## dictionary of CG beads eg cg_residues[residue type(POPE)][resid(1)][bead name(BB)][residue_name(PO4)/coordinates(coord)]
    residue_list={} ## a dictionary of bead in each residue eg residue_list[bead name(BB)][residue_name(PO4)/coordinates(coord)]
    box_line="CRYST1 %8.3f %8.3f %8.3f  90.00  90.00  90.00 P 1           1\n"  ## box vectors format for pdbs
    count=0  ### residue counter initialisation
    with open(input_directory+'CG_input.pdb', 'r') as pdb_input:
        for line in pdb_input.readlines():
#### separates lines
            run=False ## turns to true is line is a bead/atom
            if line.startswith('ATOM'):
                line_sep = pdbatom(line)
#### set up resnames in dictionaries
                if line_sep['residue_name'] in p_residues: ## if in protein database 
                    if 'PROTEIN' not in cg_residues:  ## if protein does not exist add to dict
                        cg_residues['PROTEIN']={}
                elif line_sep['residue_name'].startswith('W') and line_sep['atom_name'].startswith('W'):#in np_residues or line_sep['residue_name'] in water:
                    # if line_sep['residue_name'] in water: ## renames waters to SOL saves headache later on
                    line_sep['residue_name']='SOL'
                    if line_sep['residue_name'] not in cg_residues: ## if residue type does not exist add to dict
                        water_dir, water = check_water_molecules()
                        print()
                        cg_residues[line_sep['residue_name']]={}
                    line_sep['atom_name']=water
                elif line_sep['residue_name'] in np_residues:
                    if line_sep['residue_name'] not in cg_residues:
                        cg_residues[line_sep['residue_name']]={}
                    if line_sep['residue_name'] == 'ION' and 'water' not in locals():
                        water_dir, water = check_water_molecules()
                        cg_residues['SOL']={}
                        print()
                else:
                    sys.exit('\n'+line_sep['residue_name']+' is not in the fragment database!')
#### sets up previous resid id 
                if 'residue_prev' not in locals(): 
                    residue_prev=line_sep['residue_id'] 
#### if resid the same as previous line
                if residue_prev == line_sep['residue_id']:   ### if resid is the same as the previous line, it adds resname and coordinates to the atom name key in residue_list 
                    residue_list[line_sep['atom_name']]={'residue_name':line_sep['residue_name'],'coord':np.array([line_sep['x'],line_sep['y'],line_sep['z']])}
                    line_sep_prev=line_sep.copy()
#### if resids are different then the residue list is added to cg_residues
                else: 
                    if line_sep_prev['residue_name'] not in p_residues:
                        cg_residues[line_sep_prev['residue_name']][count]={} ### then create sub dictionary cg_residues[resname][count]
                        cg_residues[line_sep_prev['residue_name']][count]=residue_list ### adds residue list to dictionary key cg_residues[resname][count]
                        if line_sep_prev['residue_name'] == 'ION':
                            cg_residues['SOL'][count]={}
                            sol_res_list={}
                            sol_res_list[water]=residue_list[line_sep_prev['atom_name']]
                            sol_res_list[water]['residue_name']='SOL'
                            cg_residues['SOL'][count]=sol_res_list
                    else:
                        for bead in residue_list:
                            if bead.startswith('B'):
                                residue_list['BB']= residue_list.pop(bead)
                        cg_residues['PROTEIN'][count]={} ### then create sub dictionary cg_residues['PROTEIN'][count]
                        cg_residues['PROTEIN'][count]=residue_list ### adds residue list to dictionary key cg_residues['PROTEIN'][count]
#### updates dictionaries and counters
                    residue_list={}  ### resets residue list
                    count+=1 ### moves counter along to next residue
                    residue_list[line_sep['atom_name']]={'residue_name':line_sep['residue_name'],'coord':np.array([line_sep['x'],line_sep['y'],line_sep['z']])} ### it adds resname and coordinates to the atom name key in residue_list
                    residue_prev=line_sep['residue_id']   ### updates residue_prev with new resid
                    line_sep_prev=line_sep.copy()
                run=False ### resets check if atom
#### finds box vectors
            if line.startswith('CRYST'): ### collects box vectors from pdb
                box_vec=line
#### adds final residue to cg_residues in the same manner as above
    if line_sep['residue_name'] in p_residues: 
        if count not in cg_residues['PROTEIN']:
            cg_residues['PROTEIN'][count]={}
        cg_residues['PROTEIN'][count]=residue_list
    else:
        if count not in cg_residues[line_sep['residue_name']]:
            cg_residues[line_sep['residue_name']][count]={}
        cg_residues[line_sep['residue_name']][count]=residue_list
        if line_sep['residue_name'] == 'ION':
            cg_residues['SOL'][count]={}
            sol_res_list={}
            sol_res_list[water]=residue_list[line_sep['atom_name']]
            sol_res_list[water]['residue_name']='SOL'
            cg_residues['SOL'][count]=sol_res_list
#### checks if box vectors exist
    if 'box_vec' not in locals():### stops script if it cannot find box vectors
        sys.exit('missing box vectors')
    if 'water' in locals():
        return cg_residues, box_vec, water_dir, water
    else:
        return cg_residues, box_vec, False, False

def fix_pbc(cg_residues, box_vec):
#### fixes box PBC
    box = box_vec.split()[1:4]
    # print(residues_all)
    for residue_type in cg_residues:
        if residue_type not in ['ION','SOL']:
            for res_val, residue in enumerate(cg_residues[residue_type]):
                for bead_val, bead in enumerate(cg_residues[residue_type][residue]):
                    if bead_val != 0:
                        for xyz in range(3):
                        #### for x, y, z if the distance between bead is more than half the box length
                            if np.sqrt((cg_residues[residue_type][residue][bead]['coord'][xyz]-cg_residues[residue_type][residue][bead_prev]['coord'][xyz])**2) > float(box[xyz])/2:
                            #### if the bead if in the opposite 1/3 of the box the position the box length is add/subtracted
                                if cg_residues[residue_type][residue][bead]['coord'][xyz] <= float(box[xyz])/2:
                                    temp = cg_residues[residue_type][residue][bead]['coord'][xyz]+float(box[xyz])
                                elif cg_residues[residue_type][residue][bead]['coord'][xyz] > float(box[xyz])/2:
                                    temp = cg_residues[residue_type][residue][bead]['coord'][xyz]-float(box[xyz])
                            #### if distance between corrected coordinate is still > 1/2 the box length then counts as a new chain
                                if np.sqrt((temp-cg_residues[residue_type][residue][bead_prev]['coord'][xyz])**2) > 8:
                                    bead_prev=bead
                                else:
                                    cg_residues[residue_type][residue][bead]['coord'][xyz] = temp
                    if residue_type != 'PROTEIN':
                        bead_prev=bead
                    elif res_val == 0 and residue_type == 'PROTEIN':
                        bead_prev=bead
    return cg_residues

############################################################ Build Non Protein Section ################################################################

def build_atomistic_system(cg_residues, box_vec):
    system={}
    atomistic_fragments={}
#### for each residue type covert to atomistic except protein
    for residue_type in [key for value, key in enumerate(cg_residues) if key not in ['PROTEIN']]:
        if residue_type not in system and residue_type != 'ION':
            system[residue_type] = 0
    #### reset counters for each residue type
        print('Converting residue type: ' +residue_type)
    #### creates folder for residue type
        mkdir_directory(working_dir+residue_type)
    #### fetches atoms for the residue type and centers then on cg bead

        atomistic_fragments[residue_type] = atomistic_non_protein(residue_type, cg_residues[residue_type])
        # print(atomistic_fragments[residue_type])
    #### if the residue type is in ['SOL', 'ION'] a single pdb is created
        if residue_type == 'SOL':            
            mkdir_directory(working_dir+'SOL')  
        #### creates solvent directory and SOL key in system dictionay otherwise it appends solvent molecules to sol pdb
            if not os.path.exists(working_dir+'SOL'+'/SOL_0.pdb'):   
                # system['SOL']=0
                pdb_sol = open(working_dir+'SOL'+'/SOL_0.pdb', 'w')
                pdb_sol.write('REMARK    GENERATED BY sys_setup_script\nTITLE     SELF-ASSEMBLY-MAYBE\nREMARK    Good luck\n'
                              +box_vec+'MODEL        1\n')
            else:
                pdb_sol = open(working_dir+'SOL'+'/SOL_0.pdb', 'a')
        #### creates ion pdb with header
        if residue_type == 'ION':
            #### make minimisation directory and makes homogeneous directory structure
                mkdir_directory(working_dir+'ION/min')
                pdb_ion = create_pdb(working_dir+residue_type+'/'+residue_type+'_merged.pdb')
    #### loop through all resids of that residue type 
        for resid in atomistic_fragments[residue_type]:
        #### if the residue type is not in ['SOL', 'ION'] a individual pdbs are created for each resid
            if residue_type not in ['SOL', 'ION']:
                pdb_output = create_pdb(working_dir+residue_type+'/'+residue_type+'_'+str(resid)+'.pdb')         
                atomistic_fragments[residue_type][resid] = check_hydrogens(atomistic_fragments[residue_type][resid])
            ####### check if any atoms in residue overlap #######
                coord=[]
                for atom in atomistic_fragments[residue_type][resid]:
                    coord.append(atomistic_fragments[residue_type][resid][atom]['coord'])
                coord=check_atom_overlap(coord)
                for atom_val, atom in enumerate(atomistic_fragments[residue_type][resid]):
                    atomistic_fragments[residue_type][resid][atom]['coord']=coord[atom_val]

            for at_id, atom in enumerate(atomistic_fragments[residue_type][resid]):
            #### separates out the water molecules from the ion in the fragment
                if residue_type in ['SOL']:
                    if atomistic_fragments[residue_type][resid][at_id+1]['frag_mass'] > 1:                  
                        system['SOL']+=1
                    short_line=atomistic_fragments[residue_type][resid][at_id+1]
                    pdb_sol.write(pdbline%((at_id+1,short_line['atom'],short_line['res_type'],' ',1,short_line['coord'][0],
                                  short_line['coord'][1],short_line['coord'][2],short_line['extra'],short_line['connect']))+'\n')
                elif residue_type in ['ION']:
                #### write ion coordinate out
                    short_line=atomistic_fragments[residue_type][resid][at_id+1]
                    pdb_ion.write(pdbline%((at_id+1,short_line['atom'],short_line['res_type'],' ',1,short_line['coord'][0],
                                  short_line['coord'][1],short_line['coord'][2],short_line['extra'],short_line['connect']))+'\n')
                    if atomistic_fragments[residue_type][resid][at_id+1]['res_type'] != 'SOL':
                        if atomistic_fragments[residue_type][resid][at_id+1]['res_type'] not in system:
                            system[atomistic_fragments[residue_type][resid][at_id+1]['res_type']]=1
                        else:
                            system[atomistic_fragments[residue_type][resid][at_id+1]['res_type']]+=1
                else:
                #### write residue out to a pdb file
                    short_line=atomistic_fragments[residue_type][resid][at_id+1]
                    pdb_output.write(pdbline%((at_id+1,short_line['atom'],short_line['res_type'],' ',1,short_line['coord'][0],
                                     short_line['coord'][1],short_line['coord'][2],short_line['extra'],short_line['connect']))+'\n')
        if residue_type not in ['SOL','ION']:
        #### adds retype to system dictionary
            system[residue_type]=int(resid)+1
    return system 

def check_hydrogens(residue):
#### finds the connecting carbons and their associated carbons [carbon atom, hydrogen ref number, connecting ref number]    
    connect=[]
    for atom_num, atom in enumerate(residue):
        if residue[atom]['connect'] > 0 and residue[atom]['extra'] > 1:
            connect.append([atom, residue[atom]['extra'],  residue[atom]['connect']]) 
    connect=np.array(connect)
    for atom_num, carbon in enumerate(connect):
        h_coord=[]
        h_atoms=[]
    #### strips coordinates 
        for atom_num, atom in enumerate(residue):
            if residue[atom]['extra'] == carbon[1] and atom != carbon[0]:
                h_coord.append(residue[atom]['coord'])
                h_atoms.append(atom)
            if residue[atom]['connect'] == carbon[2] and atom != carbon[0]:
                connecting_coord=residue[atom]['coord']
        h_coord=np.array(h_coord)
    #### gets COM of Hydrogens
        h_com=np.array([np.mean(h_coord[:,0]),np.mean(h_coord[:,1]),np.mean(h_coord[:,2])]) ### center of mass of hydrogens
    #### vector between H COM and bonded carbon 
        vector=np.array([h_com[0]-residue[carbon[0]]['coord'][0],h_com[1]-residue[carbon[0]]['coord'][1],h_com[2]-residue[carbon[0]]['coord'][2]])
    #### flips  
        h_com_f=h_com+vector*2
        d1 = np.sqrt((h_com[0]-connecting_coord[0])**2+(h_com[1]-connecting_coord[1])**2+(h_com[2]-connecting_coord[2])**2)
        d2 = np.sqrt((h_com_f[0]-connecting_coord[0])**2+(h_com_f[1]-connecting_coord[1])**2+(h_com_f[2]-connecting_coord[2])**2)
        if d2<d1 and len(h_coord) == 2:
            for h_at in h_atoms:
                residue[h_at]['coord']=residue[h_at]['coord']+vector*2
        elif d2>d1 and len(h_coord) == 1: 
            for h_at in h_atoms:
                residue[h_at]['coord']=residue[h_at]['coord']-vector*2

    return residue

def atomistic_non_protein(cg_residue_type,cg_residues):
    atomistic_fragments={}  #### residue dictionary
#### run through every residue in a particular residue type
    for cg_resid, cg_residue in enumerate(cg_residues):
    #### get atomistic fragments for each bead and connectivity with other beads
        at_residues, connect = get_atomistic_fragments(cg_residue_type,cg_residues[cg_residue], cg_resid)   
        atomistic_fragments[cg_resid]={}  #### creats key in atomistic_fragments for each residue eg atomistic_fragments[1]
    #### runs through all beads in each resid
        for bead_number, cg_bead in enumerate(cg_residues[cg_residue]):
        #### if cg_residue_type not in ['SOL', 'ION'] as they have no connectivity 
            if cg_residue_type not in ['SOL', 'ION']:
            #### finds all beads that the cg_bead is connected to, and returns atom coord, cg coord and center of cg_bead
                at_connections,cg_connections, center=connectivity(bead_number, cg_bead, connect, at_residues, cg_residues,cg_residue)
            #### rotates at_connections to finds minimum RMS distance with cg_connections 
                if len(at_connections)==len(cg_connections):
                    try:
                        xyz_rot_apply=rotate(np.array(at_connections), np.array(cg_connections), False)
                    except:
                        sys.exit(str(cg_bead)+' '+str(at_connections)+' '+str(cg_connections))
                else:
                    sys.exit('the bead '+cg_bead+' in residue '+cg_residues[cg_residue][cg_bead]['residue_name']+' contains the wrong number of connections')
        #### if ION/SOL a random rotation is applied to the cluster 
            else:
                center=cg_residues[cg_residue][cg_bead]['coord']
                xyz_rot_apply=[np.random.uniform(0, math.pi*2), np.random.uniform(0, math.pi*2), np.random.uniform(0, math.pi*2)]
            #### applies optimum rotation to each atom in the fragment 
            for atom in at_residues[cg_bead]:
                at_residues[cg_bead][atom]['coord']=rotate_atom(at_residues[cg_bead][atom]['coord'], center, xyz_rot_apply)  ### applies rotation
            #### adds bead number to at_residues dictionary
                at_residues[cg_bead][atom].update({'cg_bead':bead_number+1})
            #### adds atomistic fragment to new dictionary atomistic_fragments[resid][atom number] allows reordering of atoms by atom number in fragment database
                atomistic_fragments[cg_resid][int(atom)]=at_residues[cg_bead][atom]
    return atomistic_fragments

def non_protein_minimise(resid, residue_type):
#### in the case of SOL all residues are minimised, whilst in all other cases individual residues are minimised separately
    if residue_type != 'SOL':
        individual = 1
        resid=resid
    else:
        individual=resid
        resid=1
    os.chdir(working_dir+residue_type)
### write topology and minimisation parts (min folder and em.mdp)
    write_topol(residue_type, individual, '')
    make_min(residue_type)#, fragment_names)
#### spin up multiprocessing for grompp 
    pool = mp.Pool(mp.cpu_count())
    pool_process = pool.map_async(gromacs, [(gmx+' grompp \
        -po md_out-'+residue_type+'_temp_'+str(rid)+' \
        -f em_'+residue_type+'.mdp \
        -p topol_'+residue_type+'.top \
        -c '+residue_type+'_'+str(rid)+'.pdb \
        -o min/'+residue_type+'_temp_'+str(rid)+' -maxwarn 1') \
        for rid in range(0, resid)]).get()          ## minimisation grompp parallised  #        -r '+residue_type+'_'+str(rid)+'.pdb \
    pool.close()
#### close grompp multiprocessing and change to min directory and spin up mdrun multiprocessing
    os.chdir('min')
    pool = mp.Pool(mp.cpu_count())
    pool.map_async(gromacs, [(gmx+' mdrun -v -nt 1 -deffnm '+residue_type+'_temp_'+str(rid)+' -c '+residue_type+'_'+str(rid)+'.pdb') \
        for rid in range(0, resid)]).get()
    pool.close()
    os.chdir(working_dir)

def merge_minimised(residue_type):
    os.chdir(working_dir+residue_type+'/min')
    print('Merging individual residues : '+residue_type)
#### create merged pdb in min folder
    pdb_output=create_pdb(working_dir+residue_type+'/min/'+residue_type+'_merged.pdb')  
    if residue_type =='SOL':
        resid_range=1
    else:
        resid_range=np_system[residue_type]
    merge,merge_coords=[],[]
#### run through every resid 
    for resid in range(resid_range):
    #### check if it exists
        if os.path.exists(working_dir+residue_type+'/min/'+residue_type+'_'+str(resid)+'.pdb'):
        #### read in resid and write straight to merged pdb
            with open(working_dir+residue_type+'/min/'+residue_type+'_'+str(resid)+'.pdb', 'r') as pdb_input:
                for line in pdb_input.readlines():
                    if line.startswith('ATOM'):
                        line_sep = pdbatom(line)
                        merge.append(line_sep)
                        merge_coords.append([line_sep['x'],line_sep['y'],line_sep['z']])
        else:
            sys.exit('cannot find minimised residue: \n'+ working_dir+residue_type+'/'+residue_type+'_merged.pdb')
    if residue_type !='SOL':
        merge_coords = check_atom_overlap(merge_coords)
    for line_val, line in enumerate(merge):
        pdb_output.write(pdbline%((int(line['atom_number']), line['atom_name'], line['residue_name'],' ',line['residue_id'],\
            merge_coords[line_val][0],merge_coords[line_val][1],merge_coords[line_val][2],1,0))+'\n')
    pdb_output.write('TER\nENDMDL')
    pdb_output.close()

def minimise_merged(residue_type):
#### write topology for merged system
    os.chdir(working_dir+residue_type)
    write_topol(residue_type, np_system[residue_type], '')
#### grompp with merged system
    gromacs(gmx+' grompp \
        -po md_out-'+residue_type+' \
        -f em_'+residue_type+'.mdp \
        -p topol_'+residue_type+'.top \
        -c '+working_dir+residue_type+'/min/'+residue_type+'_merged.pdb \
        -o '+working_dir+residue_type+'/min/'+residue_type+'_merged_min -maxwarn 1')
#### change to min directory and minimise
    os.chdir('min') 
    gromacs(gmx+' mdrun -v -deffnm '+residue_type+'_merged_min -c ../'+residue_type+'_merged.pdb')
    os.chdir(working_dir)



############################################################ Build Protein Section ################################################################

def BB_connectivity(at_connections,cg_connections, cg_residues, at_residues, residue_number, BB_connect, res, center):
#### connect to preceeding backbone bead in chain
    try:
        cg_connections.append(cg_residues[residue_number-1]['BB']['coord']-center)
        at_connections.append(at_residues[residue_number]['BB'][BB_connect[0]]['coord']-center)
    except:
        res=residue_number
        pass
#### connect to next backbone bead in chain
    try:
        cg_connections.append(cg_residues[residue_number+1]['BB']['coord']-center)
        at_connections.append(at_residues[residue_number]['BB'][BB_connect[1]]['coord']-center)
    except:
        pass
    return at_connections,cg_connections, res

# def dihedral(p1,p2,p3,p4):
# #### https://en.wikipedia.org/w/index.php?title=Dihedral_angle&oldid=689165217#Angle_between_three_vectors
# #### dihedral = atan2(([b1xb2]x[b2xb3]).b2/|b2|, [b1xb2].[b2xb3]))

#     b1 = -1.0*(p2 - p1) ## needs to be inverted
#     b2 = p3 - p2
#     b3 = p4 - p3

#     b1_b2 = np.cross(b1, b2)
#     b2_b3 = np.cross(b2, b3)

#     b1_b2_cross_b2_b3 = np.cross(b1_b2, b2_b3)
#     b2_norm = b2/np.linalg.norm(b2)

#     x = np.dot(b1_b2_cross_b2_b3, b2_norm)
#     y = np.dot(b1_b2, b2_b3)

#     return np.degrees(np.arctan2(x, y))

# def find_angle(a,b,c):
#     AB = a - b
#     BC = c - b
#     ABBC = np.linalg.norm(AB)*np.linalg.norm(BC)
#     AB_dot_BC = AB.dot(BC)
#     angle = np.arccos(AB_dot_BC/ABBC)
#     return np.degrees(angle)

def fix_carbonyl(residue_id, cg, at):
    ca=[]
    for index in range(3):
        for atom in at[residue_id+index]['BB']:
            if at[residue_id+index]['BB'][atom]['atom'] in backbone[cg[residue_id+index]['BB']['residue_name']]['restraint']: 
                ca.append(at[residue_id+index]['BB'][atom]['coord'])
            if index == 0 :
                if at[residue_id+index]['BB'][atom]['atom'] == backbone[cg[residue_id+index]['BB']['residue_name']]['b_connect'][1]: 
                    C = atom
                if at[residue_id+index]['BB'][atom]['atom'] in backbone[cg[residue_id+index]['BB']['residue_name']]['dihedral']:   
                    O = atom     
            #     if at[residue_id+index]['BB'][atom]['atom'] == backbone[cg[residue_id+index]['BB']['residue_name']]['b_connect'][0]: 
            #         N = atom 
            # if index == 1:
            #     if at[residue_id+index]['BB'][atom]['atom'] == backbone[cg[residue_id+index]['BB']['residue_name']]['b_connect'][0]: 
            #         Nn = atom                  

    initial_vector, cross_vector = align_to_vector( ca, at[residue_id]['BB'][C]['coord'], at[residue_id]['BB'][O]['coord'])
    rotation = rotation_matrix_vectors(initial_vector, cross_vector)
    center = ca[0]+(ca[1]-ca[0])/3
    at[residue_id]['BB'][C]['coord'] = (at[residue_id]['BB'][C]['coord']-center).dot(rotation)+center
    at[residue_id]['BB'][O]['coord'] = (at[residue_id]['BB'][O]['coord']-center).dot(rotation)+center
    return at

def align_to_vector(ca, C, O):
    initial_vector= O-C
    initial_vector = initial_vector/np.linalg.norm(initial_vector)
    AB = ca[0]-ca[1]
    AC = ca[0]-ca[2] 
    cross_vector = np.cross(AB, AC)
    cross_vector = cross_vector/np.linalg.norm(cross_vector)
    
    return initial_vector, cross_vector


def rotation_matrix_vectors(v1, v2):
    v = np.cross(v1,v2)
    c = np.dot(v1,v2)
    s = np.linalg.norm(v)

    rotation=np.array([[0,    -v[2],  v[1]],
                       [v[2],     0, -v[0]],
                       [-v[1], v[0],    0], 
                       ])

    r = np.identity(3) - rotation + np.matmul(rotation,rotation) * ((1 - c)/(s**2))
    return r

def fix_dihedrals(atomistic_residues, cg_residues):
    for res_index, residue_id in enumerate(atomistic_residues):
        if res_index < len(atomistic_residues)-2:
            atomistic_residues = fix_carbonyl(residue_id, cg_residues, atomistic_residues)
    final = {}
    atom_count=0
    residue_number=0
    final_resid={}
    for residue_id in atomistic_residues:
        final_resid[residue_id]={}
        residue_length=0
        residue_temp={}
        for cg_fragments in atomistic_residues[residue_id]:
            residue_temp.update(atomistic_residues[residue_id][cg_fragments])
        for atom in range(1, len(residue_temp)+1):
            final[atom_count]=residue_temp[atom]
            final[atom_count].update({'resid':residue_number})
            final_resid[residue_id][atom]=residue_temp[atom]
            atom_count+=1
        residue_number+=1
    return final, final_resid

def build_protein_atomistic_system(cg_residues, box_vec):
#### initisation of counters
    chain_information=[]
    chain_count=0
    system={}
    at_residues={}
    backbone_coords={}
    backbone_coords[chain_count]=[]
    terminal={}
    terminal[chain_count]=[]
    temporary_coordinates_atomistic={}
    temporary_coordinates_atomistic[chain_count]={}
    sequence={}
    sequence[chain_count]=[]
    res=0
    print('Converting Protein')
    mkdir_directory(working_dir+'PROTEIN')  ### make and change to protein directory
#### create new pdb file for chain 0 
    pdb_output = create_pdb(working_dir+'PROTEIN/PROTEIN_novo_'+str(chain_count)+'.pdb')
#### for each residue in protein
    initial=True

    for cg_residue_id, residue_number in enumerate(cg_residues):
    #### temporary index/dictionaries       
        at_residues[residue_number]={}
    #### fetch fragments in residue and connectivity
        at_residues[residue_number], connect=get_atomistic_fragments(cg_residues[residue_number][next(iter(cg_residues[residue_number]))]['residue_name'],cg_residues[residue_number], residue_number)
    #### if residue contains BB bead a index of the BB connectivity is collected
        if 'BB' in at_residues[residue_number]:
            BB_connect=[] ### backbone connectivity
            for atom_num, atom in enumerate(at_residues[residue_number]['BB']):
                if at_residues[residue_number]['BB'][atom]['atom'] in backbone[cg_residues[residue_number]['BB']['residue_name']]['b_connect']:
                    BB_connect.append(atom)
        
    #### for each bead in residue
        for frag_val,cg_fragments in enumerate(cg_residues[residue_number]):
        #### gets connectivity between fragents 
            at_connections, cg_connections, center=connectivity(frag_val, cg_fragments, connect, at_residues[residue_number], cg_residues, residue_number)
        #### if BB bead adds the N and C terminal atoms to connectivity
            if cg_fragments=='BB':
                at_connections, cg_connections, res = BB_connectivity(at_connections,cg_connections, cg_residues, at_residues, residue_number, BB_connect, res, center)
            #### measures the distance between BB beads. 
                if not initial:
                    xyz_prev=[cg_residues[residue_number-1]['BB']['coord'][0],cg_residues[residue_number-1]['BB']['coord'][1],cg_residues[residue_number-1]['BB']['coord'][2]]              
                    xyz_cur=[cg_residues[residue_number]['BB']['coord'][0],cg_residues[residue_number]['BB']['coord'][1],cg_residues[residue_number]['BB']['coord'][2]]
                    dist=np.sqrt(((xyz_prev[0]-xyz_cur[0])**2)+((xyz_prev[1]-xyz_cur[1])**2)+((xyz_prev[2]-xyz_cur[2])**2))
                #### if distance between BB beads is more than 5 A then it is considered a new chain.
                    if dist > 5:
                        terminal[chain_count].append(backbone[cg_residues[residue_number-1]['BB']['residue_name']]['ter'])
                        chain_count+=1  ### adds to to the protein count
                        temporary_coordinates_atomistic[chain_count]={}
                        backbone_coords[chain_count]=[]   #### creates another dictionary key for bb fragments 
                        backbone_coords[chain_count].append(xyz_cur+[1])  #### adds xyz coord and mass of 1 to list
                        chain_information.append([dist, residue_number, residue_number-res])  ### info for verbose flag
                        res=residue_number-1 #### updates residue
                        terminal[chain_count]=[]
                        terminal[chain_count].append(backbone[cg_residues[residue_number]['BB']['residue_name']]['ter'])
                        sequence[chain_count]=[]
                        if cg_residues[residue_number]['BB']['residue_name']  not in mod_residues:
                            sequence[chain_count]+=aas[cg_residues[residue_number]['BB']['residue_name']]
                        else:
                            sequence[chain_count]+='X'
                    else:
                    #### the xyz coord of the BB bead are added to the backbone_coords dictionary
                        backbone_coords[chain_count].append(xyz_cur+[1])
                        if cg_residues[residue_number]['BB']['residue_name']  not in mod_residues:
                            sequence[chain_count]+=aas[cg_residues[residue_number]['BB']['residue_name']]
                        else:
                            sequence[chain_count]+='X'
                #### if not prev residue the xyz coord of the cg_bead are added to the backbone_coords dictionary
                else:
                    xyz_cur=[cg_residues[residue_number]['BB']['coord'][0],cg_residues[residue_number]['BB']['coord'][1],cg_residues[residue_number]['BB']['coord'][2]]
                    backbone_coords[chain_count].append(xyz_cur+[1])
                    initial=False
                    terminal[chain_count].append(backbone[cg_residues[residue_number]['BB']['residue_name']]['ter'])
                    if cg_residues[residue_number]['BB']['residue_name'] not in mod_residues:
                        sequence[chain_count]+=aas[cg_residues[residue_number]['BB']['residue_name']]
                    else:
                        sequence[chain_count]+='X'
            if cg_residues[residue_number][cg_fragments]['residue_name'] == 'CYS' and cg_fragments != 'BB':
                at_connections, cg_connections, disulphide, disul_at_info, disul_cg_info= find_closest_cysteine(at_connections, cg_connections, cg_residues, at_residues, residue_number, BB_connect, res, center)
        #### finds optimum rotation of fragment
            if len(at_connections) == len(cg_connections):
                if cg_residues[residue_number][cg_fragments]['residue_name'] == 'PRO' and cg_fragments != 'BB':
                    xyz_rot_apply=rotate(np.array(at_connections), np.array(cg_connections), True)
                else:
                    xyz_rot_apply=rotate(np.array(at_connections), np.array(cg_connections), False)
            else:
                print('atom connections: '+str(len(at_connections))+' does not equal CG connections: '+str(len(cg_connections)))
                sys.exit('residue number: '+str(residue_number)+', residue type: '+str(cg_residues[residue_number][cg_fragments]['residue_name'])+', bead: '+cg_fragments)


        #### applies rotation to each atom
            for atom in at_residues[residue_number][cg_fragments]:
                at_residues[residue_number][cg_fragments][atom]['coord'] = rotate_atom(at_residues[residue_number][cg_fragments][atom]['coord'], center, xyz_rot_apply)     
    #### if disulphide bond found move the S atoms to within 2 A of each other
        if 'disulphide' in locals():
            if disulphide:
                at_residues[residue_number] = shift_sulphur(residue_number, disul_at_info, disul_cg_info, at_residues, cg_residues) 
                disulphide = False
        temporary_coordinates_atomistic[chain_count][residue_number]=at_residues[residue_number]

    final_coordinates_atomistic = finalise_novo_atomistic(temporary_coordinates_atomistic, cg_residues)

    terminal[chain_count].append(backbone[cg_residues[residue_number]['BB']['residue_name']]['ter'])

    system['terminal_residue']=terminal
    system['PROTEIN']=chain_count+1
    if args.v >=1:
        print('\n{:-<75}'.format('>  Verbose level 1 start'))
        print('\nchain number\tDelta A\t\tno in pdb\tlength of chain')
        print('------------\t-------\t\t---------\t---------------')
        for chain in range(chain_count):
            print('\t',chain,'\t',np.round(chain_information[chain][0], 1),'\t\t',chain_information[chain][1]-chain_information[chain][2]+1,'-',chain_information[chain][1],'\t\t',chain_information[chain][2])
        if chain_count >1:
            print('\t', chain_count,'\tN/A\t\t',chain_information[chain][1]+2,'-',residue_number+1,'\t\t',residue_number-res)
        else:
            print('\t', chain_count,'\tN/A\t\t',res+2,'-',residue_number+1,'\t\t',residue_number-res)

        print('\n{:-<75}'.format('>  Verbose level 1 end\n'))
    return system, backbone_coords, final_coordinates_atomistic, sequence

def finalise_novo_atomistic(temporary_coordinates_atomistic, cg_residues):
    final_at_residues={}
    final_at_resids = {}
    for chain in temporary_coordinates_atomistic:
        pdb_output = create_pdb(working_dir+'PROTEIN/PROTEIN_novo_'+str(chain)+'.pdb')
        final_at_residues[chain], final_at_resids[chain] = fix_dihedrals(temporary_coordinates_atomistic[chain], cg_residues)
    #### check if any atom overlap if so give the atom a kick
        coords=[]
        for atom in final_at_residues[chain]:
            coords.append(final_at_residues[chain][atom]['coord'])
        coords = check_atom_overlap(coords)
        for line_index, atom in enumerate(final_at_residues[chain]):
            final_at_residues[chain][atom]['coord']=coords[line_index]
            pdb_output.write(pdbline%((line_index,final_at_residues[chain][atom]['atom'],final_at_residues[chain][atom]['res_type'],ascii_uppercase[chain],\
                final_at_residues[chain][atom]['resid'],final_at_residues[chain][atom]['coord'][0],final_at_residues[chain][atom]['coord'][1],final_at_residues[chain][atom]['coord'][2],1,0))+'\n')
        pdb_output.close()
    return final_at_resids

################# Fixes disulphide bond, martini cysteine bone is too far apart to be picked up by pdb2gmx. 
#### 

def find_closest_cysteine(at_connections, cg_connections, cg_residues, at_residues, residue_number, BB_connect, res, center):
    disulphide, atom_number=False, 0
    for res_id in cg_residues: 
        try:
            #### checks distance between cysteines if closer than 7A then adds another connection between the S and the sidechain of the other cysteine CG bead
            if cg_residues[res_id]['SC1']['residue_name'] == 'CYS' and res_id not in [residue_number-1, residue_number, residue_number+1]:
                xyz_cur=[cg_residues[residue_number]['SC1']['coord'][0],cg_residues[residue_number]['SC1']['coord'][1],cg_residues[residue_number]['SC1']['coord'][2]] ### cysteine of interest
                xyz_check=[cg_residues[res_id]['SC1']['coord'][0],cg_residues[res_id]['SC1']['coord'][1],cg_residues[res_id]['SC1']['coord'][2]] ### cysteine to check distance
                dist=np.sqrt(((xyz_check[0]-xyz_cur[0])**2)+((xyz_check[1]-xyz_cur[1])**2)+((xyz_check[2]-xyz_cur[2])**2)) ### distance
                if dist < 6:
                    for atom_number in at_residues[residue_number]['SC1']:
                        if at_residues[residue_number]['SC1'][atom_number]['atom']==backbone[cg_residues[residue_number]['SC1']['residue_name']]['disulphide']: ### if sulphur
                            at_connections.append(at_residues[residue_number]['SC1'][atom_number]['coord']-center) ### add at centered coordinates
                    cg_connections.append(cg_residues[res_id]['SC1']['coord']-center) ### add cg centered coordinates
                    disulphide=True
                    break
        except:
            pass
    return at_connections, cg_connections, disulphide, atom_number, res_id

def shift_sulphur(residue_number, disul_at_info, disul_cg_info, at_residues, cg_residues ):
#### to shift sidechains roughly equally the 1st sidechain is shifted to within 3.2A and the second to 2A (pdb2gmx cutoff)
    if disul_cg_info > residue_number:
        xyz_cur=np.array([cg_residues[disul_cg_info]['SC1']['coord'][0],cg_residues[disul_cg_info]['SC1']['coord'][1],cg_residues[disul_cg_info]['SC1']['coord'][2]])
        cutoff=3.2
    else:
        xyz_cur=np.array([at_residues[disul_cg_info]['SC1'][disul_at_info]['coord'][0],at_residues[disul_cg_info]['SC1'][disul_at_info]['coord'][1],at_residues[disul_cg_info]['SC1'][disul_at_info]['coord'][2]])
        cutoff=2

    xyz_check=np.array([at_residues[residue_number]['SC1'][disul_at_info]['coord'][0],at_residues[residue_number]['SC1'][disul_at_info]['coord'][1],at_residues[residue_number]['SC1'][disul_at_info]['coord'][2]])
    dist=np.sqrt(((xyz_check[0]-xyz_cur[0])**2)+((xyz_check[1]-xyz_cur[1])**2)+((xyz_check[2]-xyz_cur[2])**2))
#### moves sidechains closer together in increments of 5% of the length of the vector 
    offset=0
    if dist >= cutoff:
        vector=xyz_cur-xyz_check
        x=0.05
        while True:
            xyz_check_new = xyz_check + ( vector * x )
            dist=np.sqrt(((xyz_check_new[0]-xyz_cur[0])**2)+((xyz_check_new[1]-xyz_cur[1])**2)+((xyz_check_new[2]-xyz_cur[2])**2))
            if dist >= cutoff:
                x+=0.05
            else:
                offset = vector * x 
                break
#### applies final shift to the rest of the atoms in the sidechain
    for atom in at_residues[residue_number]['SC1']:
        at_residues[residue_number]['SC1'][atom]['coord']=at_residues[residue_number]['SC1'][atom]['coord']+offset
    return at_residues[residue_number]

############################################################ Processes atomistic protein input ################################################################


def read_in_atomistic(protein, chain_count, check_alignment):
#### reset location and check if pdb exists  
    os.chdir(start_dir)
    if not os.path.exists(protein):
        sys.exit('cannot find atomistic protein : '+protein)
#### read in atomistic fragments into dictionary residue_list[0]=x,y,z,atom_name    
    atomistic_protein_input={}
    chain_count=0
#### read in pdb
    ter_residues=[]
    with open(protein, 'r') as pdb_input:
        atomistic_protein_input[chain_count]={}
        for line_nr, line in enumerate(pdb_input.readlines()):
            #### separate line 
            run=False ## turns to true is line is a bead/atom
            if line.startswith('ATOM'):
                line_sep = pdbatom(line)
                run=True
            #### if line is correct
            if run:
                if line_sep['residue_name'] in p_residues or line_sep['residue_name'] in mod_residues:
                    if 'H' not in line_sep['atom_name'][0] or line_sep['residue_name'] in mod_residues:  
                    #### sorts out wrong atoms in terminal residues
                        if line_sep['atom_name'] in ['OT', 'O1', 'O2']:
                            line_sep['atom_name']='O'
                    #### makes C_terminal connecting atom variable  
                        if line_sep['atom_name'] == backbone[line_sep['residue_name']]['b_connect'][1]:
                            C_ter=[line_sep['x'],line_sep['y'],line_sep['z']]
                            C_resid=line_sep['residue_id']
                            C=True
                        try:
                        #### tries to make a N_terminal connecting atom variable
                            if line_sep['atom_name'] == backbone[line_sep['residue_name']]['b_connect'][0]:
                                N_resid=line_sep['residue_id']
                                N_ter=[line_sep['x'],line_sep['y'],line_sep['z']]
                                N=True
                        #### measures distance between N and C atoms. if the bond is over 3 A it counts as a new protein
                            dist=np.sqrt(((N_ter[0]-C_ter[0])**2)+((N_ter[1]-C_ter[1])**2)+((N_ter[2]-C_ter[2])**2))
                            if N and C and C_resid != N_resid and dist > 3.5:# and aas[line_sep['residue_name']] != sequence[chain_count][line_sep['residue_id']]:
                                # print(dist)
                                N_ter, C_ter=False, False
                                ter_residues.append(line_sep['residue_id'])
                                chain_count+=1
                                atomistic_protein_input[chain_count]={} ### new chain key
                        except:
                            pass
                        if line_sep['residue_id'] not in atomistic_protein_input[chain_count]:  ## if protein does not exist add to dict
                            atomistic_protein_input[chain_count][line_sep['residue_id']]={}
                    #### adds atom to dictionary, every atom is given a initial mass of zero 
                        atomistic_protein_input[chain_count][line_sep['residue_id']][line_sep['atom_number']]={'coord':np.array([line_sep['x'],line_sep['y'],line_sep['z']]),'atom':line_sep['atom_name'], 'res_type':line_sep['residue_name'],'frag_mass':0, 'resid':line_sep['residue_id']}
                    #### if atom is in the backbone list then its mass is updated to the correct one
                        if line_sep['atom_name'] in backbone[line_sep['residue_name']]['atoms']:
                            for atom in line_sep['atom_name']:
                                if atom in mass:
                                    atomistic_protein_input[chain_count][line_sep['residue_id']][line_sep['atom_number']]['frag_mass']=mass[atom]

    if check_alignment:
        atomistic_protein_input = check_sequence(atomistic_protein_input, chain_count+1)
#### check if number of monomers is the same
    elif chain_count+1 != system['PROTEIN']:
        sys.exit('number of chains in atomistic protein input ('+str(chain_count+1)+') does not match CG representation ('+str(system['PROTEIN'])+')')
    return atomistic_protein_input

def align_chains(atomistic_protein_input, seq_user):
    at={}
    sequence_temp = sequence.deepcopy()
    for chain_at in range(len(atomistic_protein_input)):
        chain_cg=0
        s = difflib.SequenceMatcher(None, seq_user[chain_at], sequence[chain_cg])
        seq_info = s.get_matching_blocks()
        while seq_info[0][2] != len(seq_user[chain_at]):
            chain_cg+=1
            s = difflib.SequenceMatcher(None, seq_user[chain_at], sequence[chain_cg])
            seq_info = s.get_matching_blocks()
            if chain_cg > len(final_coordinates_atomistic):
                sys.exit('Cannot find a match for usesr supplied chain: '+str(chain_at))
        temp={}
        print(seq_info)
        # del sequence_temp[chain_cg][seq_info[0][1]:seq_info[0][1]+seq_info[0][2]]
        if chain_cg not in at:
            at[chain_cg]={}
        if seq_info[0][2] == len(seq_user[chain_at]):
            for resid,  residue in enumerate(atomistic_protein_input[chain_at]):
                temp[resid + seq_info[0][1]] = atomistic_protein_input[chain_at][residue]
            at[chain_cg][str(seq_info[0][1])+':'+str(seq_info[0][1]+seq_info[0][2])]=temp  
    return at

def check_sequence(atomistic_protein_input, chain_count):
    at={}
    seq_user={}
    for chain in range(len(atomistic_protein_input)):
        seq_user[chain]=[]
        for resid in atomistic_protein_input[chain]:
            for atom in atomistic_protein_input[chain][resid]:
                if atomistic_protein_input[chain][resid][atom]['res_type']  not in mod_residues:
                    seq_user[chain]+=aas[atomistic_protein_input[chain][resid][atom]['res_type']]
                else:
                    seq_user[chain]+='X'
                break
    at = align_chains(atomistic_protein_input, seq_user)
    return at

def center_atomistic(atomistic_protein_input): 
    cg_com=[]
#### for each protein chain center on cg representation 
    for chain in range(len(atomistic_protein_input)):
        cg_com.append([])
        for part_val, part in enumerate(atomistic_protein_input[chain]):
            sls, sle= int(part.split(':')[0]),int(part.split(':')[1])
            protein_mass=[]
            for residue in atomistic_protein_input[chain][part]:
            #### creates a list of all coordinates and masses [[coord, mass],[coord, mass]]
                for atom in atomistic_protein_input[chain][part][residue]:
                    short_line=atomistic_protein_input[chain][part][residue][atom]
                    protein_mass.append([short_line['coord'][0],short_line['coord'][1],short_line['coord'][2],short_line['frag_mass']])
        #### returns the COM of the atomistic protein
            atomistic_protein_mass=np.average(np.array(protein_mass)[:,:3], axis=0, weights=np.array(protein_mass)[:,3])#### add center of mass of CG_proteins
        #### for each chain the COM of the CG representation is stored (only cg is needed)
            cg_com[chain].append(np.average(np.array(backbone_coords[chain])[sls:sle,:3], axis=0, weights=np.array(backbone_coords[chain])[sls:sle,3]))
        #### each atoms coord is updated so the monomer COM is the same as the CG
            for residue in atomistic_protein_input[chain][part]:
                for atom in atomistic_protein_input[chain][part][residue]:
                    atomistic_protein_input[chain][part][residue][atom]['coord']=atomistic_protein_input[chain][part][residue][atom]['coord']-(atomistic_protein_mass-cg_com[chain][part_val])
    return atomistic_protein_input, cg_com

def rotate_protein_monomers(atomistic_protein_centered):
#### run through each chain in proteins
    for chain in range(len(atomistic_protein_centered)):
    #### creates atomistic pdb
        pdb_output = create_pdb(working_dir+'PROTEIN/PROTEIN_at_rep_user_supplied_'+str(chain)+'.pdb')
        xyz_rot_apply=[]
        for part_val, part in enumerate(atomistic_protein_input[chain]):
            sls, sle= int(part.split(':')[0]),int(part.split(':')[1])        
            at_centers=[]
        #### runs through every residue and atom  
            for residue in atomistic_protein_input[chain][part]:
            #### gets center of mass of each residue (note only backbone heavy atoms have a mass)
                at_centers_iter=[]
                for atom in atomistic_protein_input[chain][part][residue]:
                    at_centers_iter.append(np.append(atomistic_protein_centered[chain][part][residue][atom]['coord'],atomistic_protein_centered[chain][part][residue][atom]['frag_mass']))
                try:
                    at_centers.append(np.average(np.array(at_centers_iter)[:,:3], axis=0, weights=np.array(at_centers_iter)[:,3]))
                except:
                    for atom in atomistic_protein_input[chain][part][residue]:
                        print(atomistic_protein_input[chain][part][residue][atom])
                    sys.exit()
        #### finds optimal rotation of each monomer  
            if len(at_centers) == len(np.array(backbone_coords[chain])[sls:sle,:3]):
                xyz_rot_apply.append(rotate(np.array(at_centers)-cg_com[chain][part_val], np.array(backbone_coords[chain])[sls:sle,:3]-cg_com[chain][part_val], False))
            else:
                sys.exit('In chain '+str(chain)+' the atomistic input does not match the CG. \n\
    number of CG residues '+str(len(backbone_coords[chain]))+'\nnumber of AT residues '+str(len(at_centers)))

            if args.v >= 1:
                print('\nThe proteins chains are rotated around the COM of all the backbone heavy atoms.')
                print('The COM of chain', chain,'is :', np.round(cg_com[chain][0], 2),',', np.round(cg_com[chain][1], 2),',', np.round(cg_com[chain][2], 2))
                print('rotating chain ', chain, 'by :',np.round(np.degrees(xyz_rot_apply[0]),2),',',np.round(np.degrees(xyz_rot_apply[1]),2),',',np.round(np.degrees(xyz_rot_apply[2]),2))
                print()
        #### applies optimal rotation to each atom 
        for residue in final_coordinates_atomistic[chain]:
            exists=False
            for initial_index in final_coordinates_atomistic[chain][residue]:
                if final_coordinates_atomistic[chain][residue][initial_index]['res_type'] in mod_residues:
                    for atom in final_coordinates_atomistic[chain][residue]:
                        short_line=final_coordinates_atomistic[chain][residue][atom]
                        pdb_output.write(pdbline%((atom,short_line['atom'],short_line['res_type'],ascii_uppercase[chain],residue,
                                        short_line['coord'][0],short_line['coord'][1],short_line['coord'][2],1,0))+'\n')
                elif final_coordinates_atomistic[chain][residue][initial_index]['res_type'] not in mod_residues:
                    for part_val, part in enumerate(atomistic_protein_input[chain]):
                        if residue in atomistic_protein_centered[chain][part]:
                            exists=True
                            for atom in atomistic_protein_centered[chain][part][residue]:
                                short_line = atomistic_protein_centered[chain][part][residue][atom]
                                atomistic_protein_centered[chain][part][residue][atom]['coord'] = rotate_atom(atomistic_protein_centered[chain][part][residue][atom]['coord'], cg_com[chain][part_val], xyz_rot_apply[part_val])
                            #### writes out new pdb for each optimised chain
                                pdb_output.write(pdbline%((atom,short_line['atom'],short_line['res_type'], ascii_uppercase[chain],
                                                 residue,short_line['coord'][0],short_line['coord'][1],short_line['coord'][2],1,0))+'\n')
                if not exists:
                    # print(residue)
                    for atom in final_coordinates_atomistic[chain][residue]:
                        short_line=final_coordinates_atomistic[chain][residue][atom]  
                        # print(short_line['res_type'])                  
                        pdb_output.write(pdbline%((atom,short_line['atom'],short_line['res_type'],ascii_uppercase[chain],residue,
                                         short_line['coord'][0],short_line['coord'][1],short_line['coord'][2],1,0))+'\n')
                break

def RMSD_measure(structure_atoms):
    RMSD_dict = {}
    for chain in range(system['PROTEIN']):
        at_centers=[]
    #### runs through every residue and atom  
        for residue in structure_atoms[chain]:
        #### gets center of mass of each residue (note only backbone heavy atoms have a mass)
            at_centers_iter=[]
            for atom in structure_atoms[chain][residue]:
                at_centers_iter.append(np.append(structure_atoms[chain][residue][atom]['coord'],structure_atoms[chain][residue][atom]['frag_mass']))
            try:
                at_centers.append(np.average(np.array(at_centers_iter)[:,:3], axis=0, weights=np.array(at_centers_iter)[:,3]))
            except:
                for atom in structure_atoms[chain][residue]:
                    print(structure_atoms[chain][residue][atom])
                sys.exit()
    #### checks that the number of residues in the chain are the same between CG and AT
        if len(at_centers) != len(backbone_coords[chain]):
            sys.exit('In chain '+str(chain)+' the atommistic input does not match the CG. \n\
    number of CG residues '+str(len(backbone_coords[chain]))+'\nnumber of AT residues '+str(len(at_centers)))
        #### finds distance between backbone COM and cg backbone beads
        dist=np.sqrt((np.array(at_centers) - np.array(backbone_coords[chain])[:,:3])**2)
        RMSD_val = np.sqrt(np.mean(dist**2)) #### RMSD calculation
        RMSD_dict[chain]=np.round(RMSD_val, 3)  #### stores RMSD in dictionary
    return RMSD_dict

######################################################################## GROMACS protein ###################################################################

def minimise_protein():
#### makes em.mdp for each chain
    os.chdir(working_dir+'/PROTEIN')
    mkdir_directory(working_dir+'FORCEFIELD')
    copy_tree(forcefield_location+forcefield+'.ff', working_dir+'PROTEIN/'+forcefield+'.ff/.')
    mkdir_directory('min')
    copyfile(forcefield_location+'/residuetypes.dat', 'residuetypes.dat')
    with open('em.mdp','w') as em:
        em.write('define = \nintegrator = steep\nnsteps = 10000\nemtol = 1000\nemstep = 0.001\ncutoff-scheme = Verlet\n')
    for chain in range(system['PROTEIN']):
        pdb2gmx_selections=ask_terminal(chain)
        minimise_protein_chain(chain, 'novo_', ' << EOF \n1\n'+str(pdb2gmx_selections[0])+'\n'+str(pdb2gmx_selections[1]))
        pdb2gmx_selections = histidine_protonation(chain, 'novo_', pdb2gmx_selections)
        if user_at_input and 'PROTEIN' in system:
            minimise_protein_chain(chain, 'at_rep_user_supplied_', pdb2gmx_selections)
    os.chdir('..')

def histidine_protonation(chain, input, chain_ter):
#### reads protonation state of histidine from itp file
    histidines=[]
    with open('PROTEIN_'+input+str(chain)+'.top', 'r') as top_input:
        for line in top_input.readlines():
            if line.startswith('; residue'):
                if line.split()[5] in ['HSD','HID']:
                    histidines.append(0)
                elif line.split()[5] in ['HSE', 'HIE']:
                    histidines.append(1)
                elif line.split()[5] in ['HSP','HIS1']:
                    histidines.append(2)
    pdb2gmx_selections='-his << EOF \n1'
    for his in histidines:
        pdb2gmx_selections+='\n'+str(his)
    pdb2gmx_selections+='\n'+str(chain_ter[0])+'\n'+str(chain_ter[1])
    return pdb2gmx_selections

def ask_terminal(chain):
#### default termini is neutral, however if ter flag is supplied you interactively choose termini 
    default_ter=[1,1]
    ter_name=['N terminal','C terminal']
    for ter_val,  ter_residue in enumerate(p_system['terminal_residue'][chain]):
        if not ter_residue:
            if args.ter:
                print('\n please select species for '+ter_name[ter_val]+' residue in chain '+str(chain)+' :\n 0: charged\n 1: neutral')
                while True:
                    try:
                        number = int(input('\nplease select terminal species: '))
                        if number in [0,1]:
                            default_ter[ter_val]=number
                            break
                    except KeyboardInterrupt:
                        sys.exit('\nInterrupted')
                    except:
                        print("Oops!  That was a invalid choice")
        else:
            if args.ter:
                print('\n The '+ter_name[ter_val]+' residue is non adjustable')
            if ter_val == 0:
                default_ter[ter_val]=3
            else:
                default_ter[ter_val]=4
    return default_ter

def minimise_protein_chain(chain, input, pdb2gmx_selections):
#### pdb2gmx on on protein chain, creates the topologies    
    gromacs(gmx+' pdb2gmx -f PROTEIN_'+input+str(chain)+'.pdb -o PROTEIN_'+input+str(chain)+'_gmx.pdb -water none \
-p PROTEIN_'+input+str(chain)+'.top  -i PROTEIN_'+input+str(chain)+'_posre.itp -ter '+pdb2gmx_selections+'\nEOF') #### single chains
#### converts the topology file and processes it into a itp file
    convert_topology('PROTEIN_'+input, chain)
#### writes topology overview for each chain 
    write_topol('PROTEIN_'+input, 1, str(chain))
#### writes restraints file for each chain
    write_posres(chain)
#### grompps each protein chain
    gromacs(gmx+' grompp \
-f em.mdp \
-p topol_PROTEIN_'+input+str(chain)+'.top \
-c PROTEIN_'+input+str(chain)+'_gmx.pdb \
-o min/PROTEIN_'+input+str(chain)+' \
-maxwarn 1 ')
#### minimises chain
    os.chdir('min')
    gromacs(gmx+' mdrun -v -deffnm PROTEIN_'+input+str(chain)+' -c PROTEIN_'+input+str(chain)+'.pdb')
    os.chdir('..')  

def write_posres(chain):
#### if not posres file exist create one
    if not os.path.exists(working_dir+'PROTEIN/PROTEIN_'+str(chain)+'_steered_posre.itp'):
        posres_output = open(working_dir+'PROTEIN/PROTEIN_'+str(chain)+'_steered_posre.itp', 'w')
        posres_output.write('[ position_restraints ]\n; atom  type      fx      fy      fz\n')
    #### read in each chain from after pdb2gmx 
        with open(working_dir+'PROTEIN/PROTEIN_novo_'+str(chain)+'_gmx.pdb', 'r') as pdb_input:
            at_counter=0
            for line in pdb_input.readlines():
                if line.startswith('ATOM'):
                    line_sep = pdbatom(line)
                    at_counter+=1
                #### if atom is in the restraint list for that residue add to position restraint file
                    if line_sep['atom_name'] in backbone[line_sep['residue_name']]['restraint']:
                        posres_output.write(str(at_counter)+'     1  1000  1000  1000\n')

def steered_md_atomistic_to_cg_coord(chain):
    os.chdir(working_dir+'PROTEIN')
    mkdir_directory('steered_md')
#### create bog standard mdp file, simulation is only 3 ps in a vaccum so settings should not have any appreciable effect 
    with open('steered_md.mdp', 'w') as steered_md:
        steered_md.write('define = -DPOSRES_STEERED\nintegrator = md\nnsteps = 3000\ndt = 0.001\ncontinuation   = no\nconstraint_algorithm = lincs\nconstraints = h-bonds\nns_type = grid\nnstlist = 25\n\
rlist = 1\nrcoulomb = 1\nrvdw = 1\ncoulombtype  = PME\npme_order = 4\nfourierspacing = 0.16\ntcoupl = V-rescale\ntc-grps = system\ntau_t = 0.1\nref_t = 310\npcoupl = no\n\
pbc = xyz\nDispCorr = no\ngen_vel = yes\ngen_temp = 310\ngen_seed = -1')    
#### run grompp on chain 
    gromacs(gmx+' grompp \
-f steered_md.mdp \
-p topol_PROTEIN_at_rep_user_supplied_'+str(chain)+'.top \
-c min/PROTEIN_at_rep_user_supplied_'+str(chain)+'.pdb \
-r min/PROTEIN_novo_'+str(chain)+'.pdb \
-o steered_md/PROTEIN_at_rep_user_supplied_'+str(chain)+' -maxwarn 1 ')
#### run mdrun on steered MD
    os.chdir('steered_md')
    gromacs(gmx+' mdrun -v -deffnm PROTEIN_at_rep_user_supplied_'+str(chain)+' -c PROTEIN_at_rep_user_supplied_'+str(chain)+'.pdb')
#### if no pdb file is created stop script with error message
    if os.path.exists('PROTEIN_at_rep_user_supplied_'+str(chain)+'.pdb'):
        pass
    else:
        sys.exit('steered MD failed! Starting atomistic input may be too far from CG structure')



def merge_protein(no_chains, protein):
#### merge protein chains into single pdb
    merge = read_in_protein_pdbs(no_chains, working_dir+'PROTEIN/min/PROTEIN'+protein)
    if protein!='_at_rep_user_supplied':
        write_merged_pdb(merge, protein)
    if protein=='_at_rep_user_supplied':
        write_merged_pdb(merge, '_no_steered')
        merge = read_in_protein_pdbs(no_chains, working_dir+'PROTEIN/steered_md/PROTEIN'+protein)
        write_merged_pdb(merge, protein)

def read_in_protein_pdbs(no_chains, file):
#### reads in each chain into merge list
    merge, merge_coords = [],[]
    for chain in range(0,no_chains):
        if os.path.exists(file+'_'+str(chain)+'.pdb'):
            with open(file+'_'+str(chain)+'.pdb', 'r') as pdb_input:
                for line in pdb_input.readlines():
                    if line.startswith('ATOM'):
                        line_sep=pdbatom(line)
                        merge.append(line_sep)
                        merge_coords.append([line_sep['x'], line_sep['y'],line_sep['z']])
        else:
            sys.exit('cannot find minimised residue: \n'+'PROTEIN/'+location+'/PROTEIN'+protein+'_'+str(chain)+'.pdb')     
    merged_coords = check_atom_overlap(merge_coords)
    merged=[]
    for line_val, line in enumerate(merge):
        merged.append(pdbline%((int(line['atom_number']), line['atom_name'], line['residue_name'],' ',line['residue_id'],\
            merged_coords[line_val][0],merged_coords[line_val][1],merged_coords[line_val][2],1,0))+'\n')

    return merged

def concat(atom):
    return np.array([atom['x'],atom['y'],atom['z']])

def correct_dihedrals(at,merged, merged_coord):

    for atom in at:
        merged.append(atom)
        merged_coord.append(concat(atom))
    return merged, merged_coord

def write_merged_pdb(merge, protein):
#### creates merged pdb and writes chains to it
    pdb_output=create_pdb(working_dir+'PROTEIN/PROTEIN'+protein+'_merged.pdb')
    for line in merge:
        pdb_output.write(line)
    pdb_output.close()

def check_atom_overlap(coordinates):
#### creates tree of atom coordinates
    tree = KDTree(coordinates)
#### provides index of any atoms that are within 0.3A of each other
    overlapped_ndx = tree.query_ball_tree(tree, r=0.3)  ### takes a while 
    done=[]
    moved_coord=[]
    dist=0.35
#### runs through overlapping atoms and moves atom in a random diection until it is no longer overlapping
    for ndx in overlapped_ndx:
        if len(ndx) == 2 and ndx[0] not in done:
            xyz_check = np.array([coordinates[ndx[0]][0]+np.random.uniform(-0.2, 0.2), coordinates[ndx[0]][1]+np.random.uniform(-0.2, 0.2),coordinates[ndx[0]][2]+np.random.uniform(-0.2, 0.2)])
            if len(moved_coord)>0:
                dist=np.min(np.sqrt(((xyz_check[0]-np.array(moved_coord)[:,0])**2)+((xyz_check[1]-np.array(moved_coord)[:,1])**2)+((xyz_check[2]-np.array(moved_coord)[:,2])**2)))
            while len(tree.query_ball_point(xyz_check, r=0.3)) == 2 or dist < 0.3:
                if len(moved_coord)>0:
                    dist=np.min(np.sqrt(((xyz_check[0]-np.array(moved_coord)[:,0])**2)+((xyz_check[1]-np.array(moved_coord)[:,1])**2)+((xyz_check[2]-np.array(moved_coord)[:,2])**2)))
                xyz_check = np.array([coordinates[ndx[0]][0]+np.random.uniform(-0.2, 0.2), coordinates[ndx[0]][1]+np.random.uniform(-0.2, 0.2),coordinates[ndx[0]][2]+np.random.uniform(-0.2, 0.2)])
            coordinates[ndx[0]]=xyz_check
            moved_coord.append(xyz_check)
            done.append(ndx[0])
    return coordinates

def convert_topology(topol, protein_number):
#### reads in topology 
    if Path(topol+str(protein_number)+'.top').exists():
        read=False
        with open(topol+str(protein_number)+'.itp', 'w') as itp_write:
            for line in open(topol+str(protein_number)+'.top', 'r').readlines():
            #### copies between moleculetype and position restraint section
                if len(line.split()) > 1: 
                    if read == False and line.split()[1] == 'moleculetype':
                        read = True
                    if read == True and line.split()[1] == 'POSRES':
                        read = False
                #### sorts out chain naming
                    if line.split()[0][:-1] == 'Protein_chain_':
                        line= re.sub('Protein_chain_.?', 'protein_'+str(protein_number),line)
            #### writes to itp file copied section          
                if read:
                    itp_write.write(line)
        #### adds position restraint section to end of itp file         
            itp_write.write('#ifdef POSRES\n#include \"PROTEIN_'+str(protein_number)+'_posre.itp\"\n#endif\n') 
            itp_write.write('\n; Include CA Position restraint file\n#ifdef POSRES_STEERED\n#include \"PROTEIN_'+str(protein_number)+'_steered_posre.itp\"\n#endif')
    else:
        sys.exit('cannot find : '+topol+'_'+str(protein_number)+'.top')





#################################################################### GROMACS system ###################################################################

def merge_system_pdbs(system, protein):
    os.chdir(working_dir+'MERGED')
#### create merged pdb 
    pdb_output=create_pdb(working_dir+'MERGED/merged_cg2at'+protein+'.pdb') 
#### using updated dictionary for the edge case of ions and no waters, eg. converting a protein with only its bound ions.
    if 'ION' in cg_residues and 'SOL' not in cg_residues:
        cg_updated={}
        cg_updated['SOL']=[]
        cg_updated.update(cg_residues)
    else:
        cg_updated=cg_residues
    merge=[]
    merge_coords=[]
    merge2=[]
    merge_coords2=[]
    merge_protein=[]
    merge_protein_coords=[]
#### run through every residue type in cg_residues
    for segment, residue_type in enumerate(cg_updated):
    #### if file contains user input identifier 
        if residue_type != 'PROTEIN':
            input_type=''
        else:
            input_type=protein
        if os.path.exists(working_dir+residue_type+'/'+residue_type+input_type+'_merged.pdb'):
        #### opens pdb files and writes straight to merged_cg2at pdb
            with open(working_dir+residue_type+'/'+residue_type+input_type+'_merged.pdb', 'r') as pdb_input:
                for line in pdb_input.readlines():
                    if line.startswith('ATOM'):
                        line_sep = pdbatom(line)
                        merge.append(line_sep)
                        merge_coords.append([line_sep['x'],line_sep['y'],line_sep['z']])
        else:
            sys.exit('cannot find minimised residue: \n'+ working_dir+residue_type+'/'+residue_type+input_type+'_merged.pdb')
    if protein in ['_at_rep_user_supplied','_novo']:
        print('checking for atom overlap in : '+protein[1:])
        merge_coords = check_atom_overlap(merge_coords)
    for line_val, line in enumerate(merge):
        pdb_output.write(pdbline%((int(line['atom_number']), line['atom_name'], line['residue_name'],' ',line['residue_id'],\
            merge_coords[line_val][0],merge_coords[line_val][1],merge_coords[line_val][2],1,0))+'\n')
    pdb_output.write('TER\nENDMDL')
    pdb_output.close()

def write_merged_topol(system, protein):
    os.chdir(working_dir+'MERGED')
    with open('topol_final.top', 'w') as topol_write:
    #### writes topology headers (will probably need updating with other forcefields)
        topol_write.write('; Include forcefield parameters\n#include \"'+working_dir+'FORCEFIELD/'+forcefield+'.ff/forcefield.itp\"\n')
        if 'SOL' in cg_residues:
            copyfile(water_dir+water+'.itp', water+'.itp')
            topol_write.write('#include \"'+water+'.itp\"')
            topol_write.write('\n#include \"'+working_dir+'/FORCEFIELD/'+forcefield+'.ff/ions.itp\"\n\n')
    #### runs through residue types and copies to MERGED directory and simplifies the names
        for residue_type in system:
            if residue_type not in ['ION','SOL']:
            #### copies 1st itp file it comes across 
                for directory in np_directories:
                    if os.path.exists(directory[0]+residue_type+'/'+residue_type+'.itp'):       
                        topol_write.write('#include \"'+residue_type+'.itp\"\n')
                        copyfile(directory[0]+residue_type+'/'+residue_type+'.itp', residue_type+'.itp')
                        break
            #### copies across protein itp files and simplifies the names 
                if residue_type == 'PROTEIN':
                    for protein_unit in range(system[residue_type]): 
                        topol_write.write('#include \"PROTEIN_'+str(protein_unit)+'.itp\"\n')
                        copyfile(working_dir+'PROTEIN/PROTEIN'+protein+'_'+str(protein_unit)+'.itp', 'PROTEIN_'+str(protein_unit)+'.itp')
                        copyfile(working_dir+'PROTEIN/PROTEIN_'+str(protein_unit)+'_steered_posre.itp', 'PROTEIN_'+str(protein_unit)+'_steered_posre.itp')
                        copyfile(working_dir+'PROTEIN/PROTEIN'+protein+'_'+str(protein_unit)+'_posre.itp', 'PROTEIN_'+str(protein_unit)+'_posre.itp')

        topol_write.write('[ system ]\n; Name\nSomething clever....\n\n[ molecules ]\n; Compound        #mols\n')
    #### adds number of residues to the topology
        for residue_type in system:
            if residue_type not in  ['PROTEIN']:
                topol_write.write(residue_type+'    '+str(system[residue_type])+'\n')   
        #### adds monomers separately
            if residue_type == 'PROTEIN':
                for protein_unit in range(system[residue_type]):
                    topol_write.write('PROTEIN_'+str(protein_unit)+'    1\n')                    

def minimise_merged_pdbs(system, protein):
    print('Minimising merged atomistic files : '+protein[1:])
    os.chdir(working_dir+'MERGED')
#### grompps final merged systems
    gromacs(gmx+' grompp -po md_out-merged_cg2at -f em_merged_cg2at.mdp -p topol_final.top \
-r merged_cg2at'+protein+'.pdb -c merged_cg2at'+protein+'.pdb -o min/merged_cg2at'+protein+'_minimised -maxwarn 1')
    os.chdir('min')
#### runs minimises final systems
    gromacs(gmx+' mdrun -v -deffnm merged_cg2at'+protein+'_minimised -c merged_cg2at'+protein+'_minimised.pdb')

def alchembed(system):
    
    os.chdir(working_dir+'MERGED')
    mkdir_directory('alchembed')
#### runs through each chain and run alchembed on each sequentially
    for chain in range(system):
        print('Running alchembed on chain: '+str(chain))
    #### creates a alchembed mdp for each chain 
        with open('alchembed_'+str(chain)+'.mdp', 'w') as alchembed:
            alchembed.write('define = -DPOSRES\nintegrator = sd\nnsteps = 750\ndt = 0.001\ncontinuation = no\nconstraint_algorithm = lincs\nconstraints = h-bonds\nns_type = grid\nnstlist = 25\n\
rlist = 1\nrcoulomb = 1\nrvdw = 1\ncoulombtype  = PME\npme_order = 4\nfourierspacing = 0.16\ntc-grps = system\ntau_t = 0.1\nref_t = 310\npcoupl = no\ncutoff-scheme = Verlet\n\
pbc = xyz\nDispCorr = no\ngen_vel = yes\ngen_temp = 310\ngen_seed = -1\nfree_energy = yes\ninit_lambda = 0.00\ndelta_lambda = 1e-3\nsc-alpha = 0.1000\nsc-power = 1\nsc-r-power = 6\n\
couple-moltype = protein_'+str(chain)+'\ncouple-lambda0 = none\ncouple-lambda1 = vdw')
    #### if 1st chain use minimised structure for coordinate input
        if chain == 0:
            gromacs(gmx+' grompp -po md_out-merged_cg2at_alchembed_'+str(chain)+' -f alchembed_'+str(chain)+'.mdp -p topol_final.top -r min/merged_cg2at_at_rep_user_supplied_minimised.pdb \
-c min/merged_cg2at_at_rep_user_supplied_minimised.pdb -o alchembed/merged_cg2at_at_rep_user_supplied_alchembed_'+str(chain)+' -maxwarn 1')
    #### if not 1st chain use the previous output of alchembed tfor the input of the next chain 
        else:
            gromacs(gmx+' grompp -po md_out-merged_cg2at_alchembed_'+str(chain)+' -f alchembed_'+str(chain)+'.mdp -p topol_final.top -r min/merged_cg2at_at_rep_user_supplied_minimised.pdb \
-c alchembed/merged_cg2at_at_rep_user_supplied_alchembed_'+str(chain-1)+'.pdb -o alchembed/merged_cg2at_at_rep_user_supplied_alchembed_'+str(chain)+' -maxwarn 1')          
        os.chdir('alchembed')
        chain_grompp=time.time()
    #### run alchembed on the chain of interest
        gromacs(gmx+' mdrun -v -deffnm merged_cg2at_at_rep_user_supplied_alchembed_'+str(chain)+' -c merged_cg2at_at_rep_user_supplied_alchembed_'+str(chain)+'.pdb')
        os.chdir('..')
#### copy final output to the FINAL folder
    copyfile('alchembed/merged_cg2at_at_rep_user_supplied_alchembed_'+str(chain)+'.pdb', final_dir+'final_cg2at_at_rep_user_supplied.pdb')
    copyfile('merged_cg2at_no_steered.pdb', final_dir+'final_cg2at_no_steered.pdb')

############################################################################## Clean up ######################################################################

def clean():
#### cleans temp files from residue_types
    for residue_type in cg_residues:
        if residue_type not in ['SOL', 'ION']:
            print('\ncleaning temp files from : '+residue_type)
            os.chdir(working_dir+residue_type)
            file_list = glob.glob('*temp*', recursive=True)
            for file in file_list:
                os.remove(file)
            os.chdir(working_dir+residue_type+'/min')
            file_list = glob.glob('*temp*', recursive=True)
            for file in file_list:
                os.remove(file) 

start_time=time.time()

print('\nInitialisation of CG2AT v2\n')

### finds initial rotation matrices
x_rot, y_rot, z_rot=[],[],[]
for angle in range(0,360, 5):
    angle=np.radians(angle)
    x_rot.append(eulerAnglesToRotationMatrix([angle,0,0]))
    y_rot.append(eulerAnglesToRotationMatrix([0,angle,0]))
    z_rot.append(eulerAnglesToRotationMatrix([0,0,angle]))

np_system,p_system=[],[]

# gmx='gmx'
# pdbline = "ATOM  %5d %4s %4s%1s%4d    %8.3f%8.3f%8.3f%6.2f%6.2f"
# mass = {'H': 0,'C': 12,'N': 14,'O': 16,'P': 31,'M': 0, 'B': 32 ,'S': 32} 

# aas = {'ALA':'A', 'ARG':'R', 'ASN':'N', 'ASP':'D', 'CYS':'C', 'GLN':'Q', 'GLU':'E', 
#        'GLY':'G', 'HIS':'H', 'ILE':'I', 'LEU':'L', 'LYS':'K', 'MET':'M', 'PHE':'F', 
#        'PRO':'P', 'SER':'S', 'THR':'T', 'TRP':'W', 'TYR':'Y', 'VAL':'V'}
# ### sets up file locations

# timestamp =  strftime("%Y-%m-%d_%H-%M-%S", gmtime())

# start_dir=os.getcwd()+'/'  ### initial working directory
# working_dir=os.getcwd()+'/CG2AT_'+timestamp+'/'   ### working directory 
# final_dir=os.getcwd()+'/CG2AT_'+timestamp+'/FINAL/'  ### final directory for run files
# input_directory=os.getcwd()+'/CG2AT_'+timestamp+'/INPUT/'  ### contains input run files

# mkdir_directory(working_dir)
# mkdir_directory(final_dir)
# mkdir_directory(input_directory)

# script_dir=os.path.dirname(os.path.realpath(__file__))+'/'

user_at_input = collect_input(args.c, args.a)
initialisation_time=time.time()

### read in and sort forcefield info
forcefield_available_prov, fragments_available_prov = read_database_directories()

try: 
    forcefield_number = forcefield_available_prov.index(args.ff.split('.')[0]+'.ff')
except:
    if args.ff != None: 
        print('Cannot find forcefield: '+args.ff.split('.')[0]+'.ff  please select one from below\n')
    forcefield_number = database_selection(forcefield_available_prov, 'forcefields')
forcefield_location, forcefield=sort_forcefield(forcefield_available_prov, forcefield_number)

### reads in and sorts fragment information
np_residues, p_residues, mod_residues,np_directories, p_directories, mod_directories=fetch_residues(fragments_available_prov)



backbone=fetch_fragment(p_directories)

fragment_selection_time=time.time()
print('\nThis script is now hopefully doing the following (Good luck):\n')

#### read in CG file
print('Reading in your CG representation\n')
cg_residues, box_vec, water_dir, water = read_initial_pdb()
#### Fix any pbc issues

cg_residues=fix_pbc(cg_residues, box_vec)

os.chdir(working_dir)
read_in_time=time.time()

system={}
#### converts protein into atomistic and minimises
if 'PROTEIN' in cg_residues:
    if len(cg_residues['PROTEIN'])>0:
    #### biulds 
        p_system, backbone_coords, final_coordinates_atomistic, sequence=build_protein_atomistic_system(cg_residues['PROTEIN'], box_vec)
        system['PROTEIN']=p_system['PROTEIN']
        protein_de_novo_time=time.time()
        if user_at_input and 'PROTEIN' in system:
        #### reads in atomistic structure   
            atomistic_protein_input = read_in_atomistic(input_directory+'AT_input.pdb', system['PROTEIN'], True)  
            atomistic_protein_centered, cg_com = center_atomistic(atomistic_protein_input)
            rotate_protein_monomers(atomistic_protein_centered)
        minimise_protein()
        merge_protein(system['PROTEIN'], '_novo')
        if user_at_input and 'PROTEIN' in system:
            print('\tRunning steered MD on input atomistic structure\n')
        #### runs steered MD on atomistic structure on CA and CB atoms
            for chain in range(system['PROTEIN']):
                steered_md_atomistic_to_cg_coord(chain)
            merge_protein(system['PROTEIN'], '_at_rep_user_supplied')
        
final_protein_time=time.time()

#### converts non protein residues into atomistic and minimises 
if len([key for value, key in enumerate(cg_residues) if key not in ['PROTEIN']]) > 0:
    np_system=build_atomistic_system(cg_residues, box_vec)
    print('\nThis may take some time....(probably time for a coffee)\n')
    for residue_type in cg_residues:
        if residue_type not in ['PROTEIN', 'ION']:
            print('Minimising individual residues: '+residue_type)
            non_protein_minimise(np_system[residue_type], residue_type)
            merge_minimised(residue_type)
            print('Minimising merged: '+residue_type)
            minimise_merged(residue_type)
    system.update(np_system)
    build_non_protein_time=time.time()

non_protein_time=time.time()

#### creates merged folder
print('\nMerging all residue types to single file. (Or a possibly tea)\n')


if len(system)>0:
    mkdir_directory(working_dir+'MERGED')
#### make final topology in merged directory
    write_merged_topol(system, '_novo')
#### make minimisation directory
    make_min('merged_cg2at')
#### merges provided atomistic protein and residues types into a single pdb file into merged directory
    if user_at_input and 'PROTEIN' in system:
        merge_system_pdbs(system, '_no_steered')
        merge_system_pdbs(system, '_at_rep_user_supplied' )
        minimise_merged_pdbs(system, '_at_rep_user_supplied')
        if len(system) > 1:
            alchembed(system['PROTEIN'])
        else:
            copyfile(working_dir+'MERGED/min/merged_cg2at_at_rep_user_supplied_minimised.pdb', final_dir+'final_cg2at_at_rep_user_supplied.pdb')
            copyfile(working_dir+'MERGED/merged_cg2at_no_steered.pdb', final_dir+'final_cg2at_no_steered.pdb')
#### merges de novo protein and residues types into a single pdb file into merged directory
    merge_system_pdbs(system, '_novo' )
    minimise_merged_pdbs(system, '_novo')
    copyfile('merged_cg2at_novo_minimised.pdb', final_dir+'final_cg2at_de_novo.pdb')
    merge_time=time.time()

#### copies all itp files and topologies from whereever they are stored
    for file_name in os.listdir(working_dir+'MERGED'):
        if file_name.endswith('.itp') or file_name.endswith('final.top'):
            copyfile(working_dir+'MERGED/'+file_name, final_dir+file_name)
#### calculates final RMS
if 'PROTEIN' in cg_residues:
    with open(final_dir+'steered_md.mdp', 'w') as steered_md:
        steered_md.write('define = -DPOSRES\nintegrator = md\nnsteps = 3000\ndt = 0.001\ncontinuation   = no\nconstraint_algorithm = lincs\nconstraints = h-bonds\nns_type = grid\nnstlist = 25\n\
rlist = 1\nrcoulomb = 1\nrvdw = 1\ncoulombtype  = PME\npme_order = 4\nfourierspacing = 0.16\ntcoupl = V-rescale\ntc-grps = system\ntau_t = 0.1\nref_t = 310\npcoupl = no\n\
pbc = xyz\nDispCorr = no\ngen_vel = yes\ngen_temp = 310\ngen_seed = -1')    
    RMSD={}
    if len(cg_residues['PROTEIN'])>0:
        de_novo_atoms = read_in_atomistic(final_dir+'final_cg2at_de_novo.pdb', system['PROTEIN'], False)
        RMSD['de novo '] = RMSD_measure(de_novo_atoms)
        if user_at_input and 'PROTEIN' in system:
            at_input_atoms = read_in_atomistic(final_dir+'final_cg2at_at_rep_user_supplied.pdb', system['PROTEIN'], False)
            RMSD['at input'] = RMSD_measure(at_input_atoms)         
    print('\n{0:^10}{1:^25}{2:^10}'.format('output ','chain','RMSD ('+chr(197)+')'))
    print('{0:^10}{1:^25}{2:^10}'.format('-------','-----','---------'))
    for rmsd in RMSD:
        for chain in RMSD[rmsd]:
            print('{0:^10}{1:^25}{2:^10}'.format(rmsd, str(chain), float(RMSD[rmsd][chain])))

if args.clean:
    clean()

final_time=time.time()

#### prints out system information

print('\n{:-<100}'.format(''))
print('{0:^100}'.format('Script has completed, time for a beer'))
print('\n{0:^20}{1:^10}'.format('molecules','number'))
print('{0:^20}{1:^10}'.format('---------','------'))
for section in system:
    print('{0:^20}{1:^10}'.format(section, system[section]))
print()


#### prints out script timings for each section
if args.v == 1:
    print('\nInitialisation: ', str(datetime.timedelta(minutes=np.round(initialisation_time-start_time, 2))).rsplit(':', 1)[0], ' min',\
    '\nFragment selection: ', str(datetime.timedelta(minutes=np.round(fragment_selection_time-initialisation_time, 2))).rsplit(':', 1)[0], ' min' ,\
    '\nRead in CG system: ', str(datetime.timedelta(minutes=np.round(read_in_time-fragment_selection_time, 2))).rsplit(':', 1)[0], ' min')
    if user_at_input and 'PROTEIN' in system:
        print('Build de novo protein system: ', str(datetime.timedelta(minutes=np.round(protein_de_novo_time-read_in_time, 2))).rsplit(':', 1)[0], ' min',\
        '\nBuild protein system from provided structure: ', str(datetime.timedelta(minutes=np.round(final_protein_time-protein_de_novo_time, 2))).rsplit(':', 1)[0], ' min', \
        '\nTotal protein system build: ', str(datetime.timedelta(minutes=np.round(final_protein_time-read_in_time, 2))).rsplit(':', 1)[0], ' min')
    else:
        print('Build de novo protein system: ', str(datetime.timedelta(minutes=np.round(final_protein_time-read_in_time, 2))).rsplit(':', 1)[0], ' min')
    print('Build non protein system: ', str(datetime.timedelta(minutes=np.round(non_protein_time-final_protein_time, 2))).rsplit(':', 1)[0], ' min', \
    '\nMerge protein and non protein system: ', str(datetime.timedelta(minutes=np.round(merge_time-non_protein_time, 2))).rsplit(':', 1)[0], ' min')
    print('Total run time: ', str(datetime.timedelta(minutes=np.round(final_time-start_time, 2))).rsplit(':', 1)[0], ' min')
