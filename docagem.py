#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import subprocess
from shutil import copyfile
from os import listdir
from os.path import isfile, join

receptor = sys.argv[2]

f = open(os.getcwd() + "/" + receptor + "/settings.txt", "r")
if f.mode == "r":
    settings = f.read()
f.close()

p = re.compile("PYTHONSH[ ]{1,}=[ ]{1,}\'([A-z0-9./]{1,})\'")
if p.findall(settings) == None:
        print("Caminho para pythonsh não encontrado no arquivo de configuração. Utilizando o padrão.")
        PYTHONSH = '/Library/MGLTools/1.5.6/bin/pythonsh'
else:
        PYTHONSH = p.findall(settings).pop()

p = re.compile("MGL_TOOLS[ ]{1,}=[ ]{1,}\'([A-z0-9./]{1,})\'")
if p.findall(settings) == None:
        print("Caminho para MGLTools não encontrado no arquivo de configuração. Utilizando o padrão.")
        MGL_TOOLS = '/Library/MGLTools/1.5.6/MGLToolsPckgs/AutoDockTools/Utilities24'
else:
        MGL_TOOLS = p.findall(settings).pop()

prep_commands = PYTHONSH + " " + MGL_TOOLS

ligand = sys.argv[1]

size_x = re.findall("(size_x)[ ]{0,}=[ ]{0,}([0-9a-z_ .-]{1,})", settings, re.IGNORECASE)[0][1]
size_y = re.findall("(size_y)[ ]{0,}=[ ]{0,}([0-9a-z_ .-]{1,})", settings, re.IGNORECASE)[0][1]
size_z = re.findall("(size_z)[ ]{0,}=[ ]{0,}([0-9a-z_ .-]{1,})", settings, re.IGNORECASE)[0][1]

center_x = re.findall("(center_x)[ ]{0,}=[ ]{0,}([0-9a-z_ .-]{1,})", settings, re.IGNORECASE)[0][1]
center_y = re.findall("(center_y)[ ]{0,}=[ ]{0,}([0-9a-z_ .-]{1,})", settings, re.IGNORECASE)[0][1]
center_z = re.findall("(center_z)[ ]{0,}=[ ]{0,}([0-9a-z_ .-]{1,})", settings, re.IGNORECASE)[0][1]

const = 0.375 # Spacing of grid points in autodock (in angstrons).
              # It will be used to calculate the equivalent
              # grid size for vina, which uses a 1 angstron spacing.

grid_adt = size_x + "," + size_y + "," + size_z
grid_vina = [str(float(size_x) * const), str(float(size_y) * const), str(float(size_z) * const)]

grid_center = '{},{},{}'.format(center_x,center_y,center_z)

runs = re.findall("(runs)[ ]{0,}=[ ]{0,}([0-9a-z_ .-]{1,})", settings, re.IGNORECASE)[0][1]
evals = re.findall("(evals)[ ]{0,}=[ ]{0,}([0-9a-z_ .-]{1,})", settings, re.IGNORECASE)[0][1]
exhaust = re.findall("(exhaust)[ ]{0,}=[ ]{0,}([0-9a-z_ .-]{1,})", settings, re.IGNORECASE)[0][1]

receptor_dir = "{}/{}".format(os.getcwd(),receptor)
ligand_dir = "{}/{}".format(receptor_dir,ligand)

dirs = [
        "/vina/",                                # 0
        "/autodock4/",                           # 1
        "/autodock4/pdbqt/",                     # 2
        "/autodock4/grid/",                      # 3
        "/autodock4/docking/",                   # 4
        "/autodock4/resultados/",                # 5
        "/autodock4/resultados/lowest_energy/",  # 6
        "/autodock4/resultados/cluster/",        # 7
        "/ligplot/"                              # 8
        ]

for i in dirs:
        dir_name = ligand_dir + i[:-1]
        if not os.path.exists(dir_name):
                os.mkdir(dir_name)

# Arquivos pdb
file_ligand_pdb = "{}/{}.pdb".format(ligand_dir,ligand) # PDB do ligante
file_receptor_pdb = receptor_dir + "/" + receptor + ".pdb" # PDB da macromolécula
file_complex_pdb = ligand_dir + dirs[6] + "complexo_"+ ligand + "_" + receptor + "_lowest_energy.pdb"
file_complex_vina = ligand_dir+dirs[0]+"complexo_vina_" + ligand + ".pdb"

# Arquivos pdbqt
file_ligand_pdbqt = ligand_dir + dirs[2] + ligand + ".pdbqt" # PDBQT do ligante
file_receptor_pdbqt = ligand_dir + dirs[2] + receptor + ".pdbqt" # PDBQT da macromolécula
file_vina_pdbqt = ligand_dir + dirs[0] + ligand + "_out.pdbqt" # PDBQT do resultado do Vina

# Arquivos de docking (dpf e dlg)
file_dpf = ligand_dir + dirs[4] + ligand + "_" + receptor + ".dpf"
file_dlg = ligand_dir + dirs[4] + ligand + "_" + receptor + ".dlg"

# Arquivos de grid (gpf e glg)
file_gpf = ligand_dir + dirs[3] + receptor + ".gpf"
file_glg = ligand_dir + dirs[3] + receptor + ".glg"

# Arquivos de resultado (cluster e lowest energy)
# Lowest energy
file_lowest_energy_pdb = ligand_dir + dirs[6] +\
ligand + "_" + receptor + "_lowest_energy.pdb"
file_lowest_energy_pdbqt = ligand_dir + dirs[6] +\
ligand + "_" + receptor + "_lowest_energy.pdbqt"

# Cluster
file_cluster_pdb = ligand_dir + dirs[7] + ligand + "_" + receptor + "_clust.pdb"
file_cluster_pdbqt = ligand_dir + dirs[7] + ligand + "_" + receptor + "_clust.pdbqt"

# Arquivo de configuração do Vina
config_filename = ligand_dir + "/vina/config_" + ligand + "_" + receptor + ".txt"

os.chdir(receptor_dir) # muda o diretório para o da macromolécula

def run_prepare_ligand():
        print("\n##### PREPARANDO O PDBQT DO LIGANTE...")
        cmd = prep_commands + "/prepare_ligand4.py -l " + file_ligand_pdb +\
         " -o " + file_ligand_pdbqt + " -A bonds_hydrogens -U nphs_lps"

        subprocess.call([cmd],shell=True)
        copyfile(file_ligand_pdbqt, receptor_dir + "/" + ligand + ".pdbqt")
        print("Ok!")

def run_prepare_receptor():
        print("\n##### PREPARANDO O PDBQT DO RECEPTOR...")
        cmd = prep_commands + "/prepare_receptor4.py -r " + file_receptor_pdb + " -o " +\
        file_receptor_pdbqt + " -e True -A bonds_hydrogens -U nphs -U lps -U nonstdres"

        subprocess.call([cmd],shell=True)
        copyfile(file_receptor_pdbqt, receptor_dir + "/" + receptor + ".pdbqt")
        print("Ok!")

def make_config_vina():
        
        print("\n##### GERANDO ARQUIVO DE CONFIGURAÇÃO DO VINA...")

        f = open(config_filename, "w")
        f.write(
                "receptor = " + file_receptor_pdbqt + "\n" +\
                "ligand = " + file_ligand_pdbqt + "\n" +\
                "\n" +\
                "center_x = " + center_x + "\n" +\
                "center_y = " + center_y + "\n" +\
                "center_z = " + center_z + "\n" +\
                "\n" +\
                "size_x = " + grid_vina[0] + "\n" +\
                "size_y = " + grid_vina[1] + "\n" +\
                "size_z = " + grid_vina[2] + "\n" +\
                "\n" +\
                "num_modes = " + runs + " \n" +\
                "exhaustiveness = " + exhaust + "\n" +\
                "\n" +\
                "\n" +\
                "out = " + file_vina_pdbqt + " \n" +\
                #"seed = 0123456789" +\
                "\n")
        f.close()
        print("OK!")


def run_vina():
        print("\n##### RODANDO VINA...\n\n")
        cmd = "vina --config " + config_filename +\
         " --log " + ligand_dir + "/vina/" + ligand + "_vina_log.txt"
        subprocess.call([cmd], shell=True)

        cmd = "mv -f " + file_vina_pdbqt + " " +\
         ligand_dir + "/vina/" + ligand + "_out.pdbqt"
        subprocess.call([cmd], shell=True)

        print("Ok!")
        print("Vina encerrado.")

def create_vina_complex():
        print("\n##### GERANDO ARQUIVO PDB DA MELHOR CONFORMAÇÃO DO VINA...")
        c = open(file_vina_pdbqt, "r")
        if c.mode == "r":
                pdbqt_content = c.read()
        c.close()

        best_model = re.split("MODEL 1\n([\s\S]*)\nENDMDL\nMODEL 2\n",pdbqt_content)
        pdbqt_content = best_model[1]
        
        copyfile(file_receptor_pdb, file_complex_vina)

        x = open(file_complex_vina, "r")
        if x.mode == "r":
                pdb = x.read()
        x.close()
        
        x = re.sub('END','TER',pdb)

        c = open(file_complex_vina, "w")
        if c.mode == "w":
                c.write(x+pdbqt_content+"\nEND")
        else:
                print("Problema na leitura do arquivo")
        c.close()

        print("Ok!")

def make_gpf():
        print("\n\n######################")
        print("##### AUTODOCK 4 #####")
        print("######################\n")
        print("\n##### GERANDO PARÂMETROS DO GRID...")
        cmd = prep_commands + "/prepare_gpf4.py -l " + file_ligand_pdbqt + " -r " + file_receptor_pdbqt +\
         " -o " + file_gpf + " -p npts=\"" + grid_adt + "\" -p gridcenter=\"" + grid_center + "\""
        subprocess.call([cmd], shell=True)
        print("Ok!")

def run_autogrid():
        print("\n##### RODANDO AUTOGRID...")
        cmd = "autogrid4 -p " + file_gpf + " -l " + file_glg
        subprocess.call([cmd],shell=True)
        print("Ok!")

def make_dpf():
        print("\n##### GERANDO PARÂMETROS DA DOCAGEM...")
        cmd = prep_commands + "/prepare_dpf42.py -l " + file_ligand_pdbqt +\
         " -r " + file_receptor_pdbqt +\
         " -o " + file_dpf + " -p ga_run='" + runs + "' -p ga_num_evals=" + evals
        subprocess.call([cmd], shell = True)
        print("Ok!")

def run_autodock():
        print("\n##### RODANDO AUTODOCK 4 (pode demorar vários minutos)")
        cmd = "autodock4 -p " + file_dpf + " -l " + file_dlg
        subprocess.call([cmd], shell = True)
        print("Ok!")

def find_lowest_energy():
        print("\n##### BUSCANDO CONFORMAÇÃO DE MENOR ENERGIA...")
        
        cmd = prep_commands + "/write_lowest_energy_ligand.py -f " + file_dlg +\
         " -o " + file_lowest_energy_pdbqt
        subprocess.call([cmd], shell = True)
        print("Ok!")
        
        print("\n##### GERANDO PDB DA CONFORMAÇÃO DE MENOR ENERGIA...")
        cmd = prep_commands + "/pdbqt_to_pdb.py -f " + file_lowest_energy_pdbqt +\
         " -o " + file_lowest_energy_pdb
        subprocess.call([cmd], shell = True)
        print("Ok!")

def find_cluster():
        print("\n##### BUSCANDO A MELHOR CONFORMAÇÃO DO MELHOR CLUSTER...")
        curr_wd = os.getcwd()
        
        os.chdir(ligand_dir + dirs[4])
        
        cmd = prep_commands + "/write_largest_cluster_ligand.py -o ../resultados/cluster/" +\
         ligand + "_" + receptor + "_clust.pdbqt"
        subprocess.call([cmd], shell = True)
        
        os.chdir(curr_wd)
        print("Ok!")

        print("\n##### GERANDO PDB DA CONF. DO MELHOR CLUSTER...")
        cmd = prep_commands + "/pdbqt_to_pdb.py -f " + file_cluster_pdbqt +\
         " -o " + file_cluster_pdb
        subprocess.call([cmd], shell = True)
        print("Ok!")

def create_complex_pdb():
        print("\n##### GERANDO PDB DO COMPLEXO DE MENOR ENERGIA DE LIGAÇÃO...")
        cmd = "cat " + file_receptor_pdbqt + " " + file_lowest_energy_pdb +\
         " | grep -v '^END ' | grep -v '^END$' > " + ligand +\
         dirs[6] + "complexo_" +\
        receptor + "_" + ligand + ".pdb"
        subprocess.call([cmd], shell = True)
        print("Ok!")

def run_command(i):
        if i == 1:
                run_prepare_ligand()
        elif i == 2:
                run_prepare_receptor()
        elif i == 3:
                make_config_vina()
        elif i == 4:
                run_vina()
        elif i == 5:
                make_gpf()
        elif i == 6:
                run_autogrid()
        elif i == 7:
                make_dpf()
        elif i == 8:
                run_autodock()
        elif i == 9:
                find_lowest_energy()
        elif i == 10:
                find_cluster()
        elif i == 11:
                create_complex_pdb()
        elif i == 12:
                create_vina_complex()

def check(opt):
        if opt == file_ligand_pdbqt:
                x = ["pdbqt do ligante", 1]
        if opt == file_receptor_pdbqt:
                x = ["pdbqt do receptor", 2]
        if opt == config_filename:
                x = ["de configuração do vina", 3]
        if opt == file_vina_pdbqt:
                x = ["pdbqt do resultado do vina", 4]
        if opt == file_gpf:
                x = ["de configuração do grid (.gpf)", 5]
        if opt == file_glg:
                x = ["de log do autogrid", 6]
        if opt == file_dpf:
                x = ["de parâmetros do autodock", 7]
        if opt == file_dlg:
                x = ["de log do autodock", 8]
        if opt == file_lowest_energy_pdbqt:
                x = ["da conformação de menor energia", 9]
        if opt == file_cluster_pdbqt:
                x = ["da cluster da conformação de menor energia", 10]
        if opt == file_complex_pdb:
                x = ["pdb do complexo de menor energia", 11]
        if opt == file_complex_vina:
                x = ["pdb do complexo do resultado do Vina", 12]
        
        if os.path.exists(opt):
                q = input("O arquivo " + x[0] + " já existe. Deseja refazê-lo? [s/n]: ")
                if (q == "s") | (q == "S"):
                        run_command(x[1])
        else:
                run_command(x[1])

check(file_ligand_pdbqt)
check(file_receptor_pdbqt)
check(config_filename)
check(file_vina_pdbqt)
check(file_complex_vina)
check(file_gpf)
check(file_glg)
check(file_dpf)
check(file_dlg)
check(file_lowest_energy_pdbqt)
check(file_cluster_pdbqt)
check(file_complex_pdb)

print("\n\n\n##### FINALIZANDO...\n")
print("Removendo arquivos pdbqt da pasta principal (se houver)...")
print("Ok!")

p = re.compile("[A-z0-9_ -]{1,}.pdbqt")
all_files = [f for f in listdir(receptor_dir) if isfile(join(receptor_dir, f))]

for file_ in all_files:
        if p.search(file_) != None:
                os.remove(receptor_dir+"/"+p.search(file_).group())

print("\n\n\n##############################\n")
print("Processo finalizado!")
print("Receptor: {}\nLigante: {}".format(receptor, ligand))
