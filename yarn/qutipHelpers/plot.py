
import numpy as np

import matplotlib.pyplot as plt
from matplotlib import colors
import datetime
from qutip import *
import qutip.control.pulseoptim as pulseoptim

from .miscellaneous import toLatex

def plotExpectation(time,observables,result):
    """
    observables = [{'Hcavity':Hcavity}]
    """
    fig, axs = plt.subplots(len(observables), 1)
    if len(observables)==1: axs = [axs]
    for i, row in enumerate(observables):
        for name, observable in row.items():
            expectation = expect(observable, result.states)
            axs[i].plot(time, expectation, label=name)
        axs[i].legend()
    fig.tight_layout(); plt.show()

def plotWigners(
    rhoList,radius,
    nCol=6,titleList=None, ptraceIndex=None, 
):
    if(len(rhoList)<nCol): nCol = len(rhoList)
    x = np.linspace(-radius, radius, 200)
    nRow = int(np.ceil(len(rhoList) / nCol))
    fig, axs = plt.subplots(nRow, nCol, 
        figsize=(3*nCol,3*nRow)
    )
    for i, rho in enumerate(rhoList):
        if ptraceIndex is not None:
            rho = ptrace(rho, ptraceIndex)
        W = wigner(rho, x, x)
        row = i // nCol
        col = i %  nCol
        ax = axs[row][col] if nRow > 1 else axs[col]
        ax.contourf(
            x, x, W, 100, cmap=plt.get_cmap('RdBu'),
            norm=colors.Normalize(-.25,.25), 
        )
        if titleList: ax.set_title(titleList[i])
    plt.tight_layout(); plt.show()

def makeTitle(t):
        return "t = {:.2f}".format(t)

def plotWignersIntermediateStates(
    time,result,number,
    radius, nCol=6,titleList=None, ptraceIndex=None, 
):
    N = len( result.states )
    if number > 1: number = number-1
    step = N // number 
    indices = np.arange(0,N,step)
    rhoList = [ket2dm(result.states[i]) for i in indices]
    rhoList.append(result.states[-1])
    titleList = [makeTitle(time[i]) for i in indices]
    titleList.append(makeTitle(time[-1]))
    plotWigners(
        rhoList,radius,
        nCol,titleList, ptraceIndex, 
    )

def plotOccupations(
    rhoList,
    nCol=6,titleList=None, ptraceIndex=None, 
):
    if(len(rhoList)<nCol): nCol = len(rhoList)
    if ptraceIndex is not None:
        rho0 = ptrace(rhoList[0], ptraceIndex)
    else:
        rho0 = rhoList[0]
    x = np.arange(0,rho0.diag().shape[0])
    nRow = int(np.ceil(len(rhoList) / nCol))
    fig, axs = plt.subplots(nRow, nCol, figsize=(3*nCol,3*nRow))
    for i, rho in enumerate(rhoList):
        if ptraceIndex is not None:
            rho = ptrace(rho, ptraceIndex)
        row = i // nCol
        col = i %  nCol
        ax = axs[row][col] if nRow > 1 else axs[col]
        ax.set_ylim(-0.2, 1.2)
        ax.bar(x, np.abs(rho.diag()))
        if titleList: ax.set_title(titleList[i])
    plt.tight_layout(); plt.show()

def plotOccupationsIntermediateStates(
    time,result,number,
    nCol=6,titleList=None, ptraceIndex=None, 
):
    N = len( result.states )
    if number > 1: number = number-1
    step = N // number 
    indices = np.arange(0,N,step)
    rhoList = [ket2dm(result.states[i]) for i in indices]
    rhoList.append(result.states[-1])
    titleList = [makeTitle(time[i]) for i in indices]
    titleList.append(makeTitle(time[-1]))
    plotOccupations( 
        rhoList,
        nCol,titleList, ptraceIndex, 
    )

def plotOptimalControl(result,controlsName,title='title'):
    fig, axs = plt.subplots(2,1)
    initial = result.initial_amps
    final = result.final_amps
    def stack(x,j): return np.hstack((x[:, j], x[-1, j]))
    pulseNames = ['initial','final']
    for i,pulse in enumerate([initial,final]):
        for j in range(pulse.shape[1]):
            axs[i].step(result.time, stack(pulse,j),
                        label=toLatex(controlsName[j]))
        axs[i].set_title(pulseNames[i]+" control")
        axs[i].legend()
    fig.tight_layout(); plt.show()
    print('*'*16 +' '+ title + " summary " + '*'*16)
    print("Final fidelity error {}".format(result.fid_err))
    print("Final gradient normal {}".format(result.grad_norm_final))
    print("Terminated due to {}".format(result.termination_reason))
    print("Number of iterations {}".format(result.num_iter))
    print("Completed in {} HH:MM:SS.US".format(
        datetime.timedelta(seconds=result.wall_time)))