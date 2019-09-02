from __future__ import print_function
import subprocess
import os
import pyVmomi
import requests
from pyVim import connect
from pyVim.connect import SmartConnect
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import numpy as np

def main():

    limpa()

    si = connect.SmartConnectNoSSL(host='<server>', user='<name>', pwd='<pass>')
    view_ref = si.content.viewManager.CreateContainerView(
        container=si.content.rootFolder,
        type=[pyVmomi.vim.VirtualMachine],
        recursive=True
    )

    Ambiente = []
    Maquina = []
    Status = []

    print("\n- 1)Gerar Planilha")
    print("- 2)Gerar Inventarios Ansible")
    print("- 3)Gerar Planilha e Inventarios Ansible")
    print("- 4)Voltar para o menu principal")
    escolha=raw_input("\nQual a sua escolha? ")

    directory = '/workdir/'
    if not os.path.exists(directory):
        os.makedirs(directory)

    vmNum=0
    for i in view_ref.view:
        vm = view_ref.view[vmNum]
        vmName = (vm.name)
        folderName = (vm.parent.name)
        vmStatus = (vm.guestHeartbeatStatus)
        Ambiente.append(folderName)
        Maquina.append(vmName)
        if(vmStatus == 'gray'):
            Status.append('Desativado')
        elif(vmStatus == 'green'):
            Status.append('Ativo')
        vmNum+=1
    if(int(escolha) == 1):
        geraPlanilha(Ambiente, Maquina, Status)
    elif(int(escolha) == 2):
        geraInventarioAnsible(Ambiente, Maquina, Status)
    elif(int(escolha) == 3):
        geraPlanilha(Ambiente, Maquina, Status)
        geraInventarioAnsible(Ambiente, Maquina, Status)
    elif(int(escolha) == 4):

def limpa():
    os.system('cls' if os.name == 'nt' else 'clear')

def geraPlanilha(Ambiente, Maquina, Status):
    df = pd.DataFrame()
    df['Ambiente'] = np.array(Ambiente)
    df['Maquina'] = np.array(Maquina)
    df['Status'] = np.array(Status)
    writer = ExcelWriter('Planilha.xlsx')
    df.to_excel(writer,'Sheet1',index=False,engine='openpyxl')
    writer.save()

def geraInventarioAnsible(Ambiente, Maquina, Status):
    arquivos=[]
    i = 0
    flag = 0
    sep = ' '
    for maquina in Maquina:
        if(Status[i] == 'Ativo'):
            if (flag == 0):
                Amb = Ambiente[i].encode('utf-8')
                f = open("/workdir/"+Amb, "a+")
                Maq = Maquina[i].encode('utf-8')
                rest = Maq.split(sep, 1)[0]
                f.write(rest+"\n")
                flag=1
            elif(Ambiente[i] == Ambiente[i-1]):
                Maq = Maquina[i].encode('utf-8')
                rest = Maq.split(sep, 1)[0]
                f.write(rest+"\n")
            else:
                f.close()
                Amb = Ambiente[i].encode('utf-8')
                f = open("/workdir/"+Amb, "a+")
                Maq = Maquina[i].encode('utf-8')
                rest = Maq.split(sep, 1)[0]
                f.write(rest+"\n")
            i+=1
        else:
            if(Ambiente[i] != Ambiente[i-1]):
                f.close()
                flag = 0
            i+=1
    f.close()

def selectCustom(vm, key):
    count = 0
    for i in vm.customValue:
        if (vm.customValue[count].key == key):
            print(vm.customValue[count].value)
        count+=1

if __name__ == '__main__':
    main()
