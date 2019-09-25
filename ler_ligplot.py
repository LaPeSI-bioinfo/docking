#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys

o = os.path.abspath(os.curdir)

regex_pontes_de_hidrogenio = re.compile(
    "0.102 0.502 0 setrgbcolor[\n]"+
    "[0-9. ]{6,}moveto[\n]"+
    "[^ \t\n\r\f\v]{1}[A-z]{3}[0-9]{1,5}[^\t\n\r\f\v]{1,}Center[\n]"+
    "[^ \t\n\r\f\v]{1}([A-z]{3}[0-9]{1,5})[^\t\n\r\f\v]{1,}Print[\n]",re.MULTILINE)

regex_interacoes_hidrofobicas = re.compile(
    "0 0 0 setrgbcolor[\n]"+
    "[0-9. ]{6,}moveto[\n]"+
    "[^ \t\n\r\f\v]{1}[A-z]{3}[0-9]{1,5}[^\t\n\r\f\v]{1,}Center[\n]"+
    "[^ \t\n\r\f\v]{1}([A-z]{3}[0-9]{1,5})[^\t\n\r\f\v]{1,}Print[\n]",re.MULTILINE)

extensao_ps = re.compile(".ps$", re.IGNORECASE)

check = False

explicacao = "\n\nEste programa lê o arquivo .ps do ligplot e retorna a " + \
            "quantidade de pontes de hidrogênio e interações hidrofóbicas e " + \
            "diz quantas ocorrências de cada existem.\n" + \
            "Para utilizar você pode dar os seguintes argumentos:\n\n" + \
            "1) o caminho para o arquivo .ps \nou\n" + \
            "2) o nome do ligante seguido do nome do receptor \n\n"

if len(sys.argv)< 2:
     print(explicacao)
     exit()

if extensao_ps.search(sys.argv[1]) != None:
    ligplot_ps_file = sys.argv[1]
else:
    ligante = sys.argv[:2][1]
    receptor = sys.argv[:3][2]

    ligplot_ps_file = o + "/"+receptor+"/"+ligante+"/ligplot/ligplot_"+ligante+"_"+receptor+".ps"
    check = True

f = open(ligplot_ps_file, "r")
ps_content = f.read()
f.close()

pontes_hidrogenio = regex_pontes_de_hidrogenio.findall(ps_content)
interacoes_hidrofobicas = regex_interacoes_hidrofobicas.findall(ps_content)

a = "Pontes de hidrogênio: "
a = a + ', '.join(pontes_hidrogenio)

b = "Interações hidrofóbicas: "
b = b + ', '.join(interacoes_hidrofobicas)

print("\nQuantidade de pontes de hidrogênio: "+str(len(pontes_hidrogenio)))
print("Quantidade de interações hidrofóbicas: "+str(len(interacoes_hidrofobicas))+"\n\n"+a+"\n"+b+"\n\n")

if check == True:
    f = open(o + "/"+receptor+"/"+ligante+"/ligplot/ligacoes_"+ligante+"_"+receptor+".txt","w")
else:
    f = open(os.path.dirname(ligplot_ps_file)+"/ler_ligplot.txt","w")

f.write("\
Quantidade de pontes de hidrogênio: "+str(len(pontes_hidrogenio))+"\n\
Quantidade de interações hidrofóbicas: "+str(len(interacoes_hidrofobicas))+"\n\n"+a+"\n"+b)
f.close()