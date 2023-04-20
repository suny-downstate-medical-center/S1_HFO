import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt

rootFolder = '/home/fernando/Dropbox/SUNY/2022/S1_netpyne/sim/'

os.chdir(rootFolder)
print(rootFolder)
folder = os.listdir('cell_data/')
folder = sorted(folder)

def loadTemplateName(cellnumber):     
    f = open(outFolder+'/template.hoc', 'r')
    for line in f.readlines():
        if 'begintemplate' in line:
            templatename = str(line)     
    templatename=templatename[:-1]        
    templatename=templatename[14:]
    return templatename

from netpyne import specs, sim   

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters

## cfg  
cfg = specs.SimConfig()					            # object of class SimConfig to store simulation configuration
cfg.duration = 1100.0 						            # Duration of the simulation, in ms
cfg.dt = 0.05								                # Internal integration timestep to use
cfg.verbose = False							                # Show detailed messages 
cfg.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
cfg.recordStep = 0.1 			
cfg.printRunTime = 0.1 # in sec			

cfg.seeds = {'conn': 1, 'stim': 1, 'loc': 1} 
cfg.hParams = {'celsius': 34, 'v_init': -71.0}  
cfg.verbose = False
cfg.createNEURONObj = True
cfg.createPyStruct = True  
#------------------------------------------------------------------------------
# Saving
#------------------------------------------------------------------------------

cfg.gabaVrev = -80.0

cfg.filename = 'IPSP_type5_gabaaVrev' + str(cfg.gabaVrev)  			# Set file output name

cfg.savePickle = False         	## Save pkl file
cfg.saveJson = True	           	## Save json file
cfg.saveDataInclude = ['simData'] ## 'simData' , 'simConfig', 'netParams'
cfg.backupCfgFile = None 		##  
cfg.gatherOnlySimData = False	##  
cfg.saveCellSecs = False			
cfg.saveCellConns = False	

cfg.analysis['plotTraces'] = {'include': [i for i in range(100)], 'oneFigPer': 'trace', 'overlay': True, 'timeRange': [0,cfg.duration], 'saveFig': True, 'showFig': False, 'figSize':(12,4)} # Plot recorded traces for this list of cells

#------------------------------------------------------------------------------
# Cell parameters
#------------------------------------------------------------------------------
#StochKv_deterministic.mod
for cellnumber in range(755,775):
    cellName = folder[cellnumber]
    outFolder = rootFolder+'/cell_data/'+folder[cellnumber]
    cellTemplateName = loadTemplateName(cellnumber)
    cellRule = netParams.importCellParams(label=cellName, somaAtOrigin=False,
        conds={'cellType': cellName, 'cellModel': 'HH_full'},
        fileName='cellwrapper.py',
        cellName='loadCell',
        cellInstance = True,
        cellArgs={'cellName': cellName, 'cellTemplateName': cellTemplateName})

for cellnumber in range(755,775):
    # ---------------------------------------------------------------------------------------------------- #
    cellName = folder[cellnumber]
    outFolder = rootFolder+'/cell_data/'+folder[cellnumber]
    cellTemplateName = loadTemplateName(cellnumber)
    
    # ---------------------------------------------------------------------------------------------------- #
    netParams.renameCellParamsSec(label=cellName, oldSec='soma_0', newSec='soma')
    
    for secname2 in netParams.cellParams[cellName]['secLists'].keys():
        if 'soma_0' in netParams.cellParams[cellName]['secLists'][secname2]:
            print(cellName,secname2,netParams.cellParams[cellName]['secLists'][secname2][0])
            netParams.cellParams[cellName]['secLists'][secname2][0] = 'soma'
    # ---------------------------------------------------------------------------------------------------- #
    
    nonSpiny = ['axon_0', 'axon_1']
    netParams.cellParams[cellName]['secLists']['spiny'] = [sec for sec in netParams.cellParams[cellName]['secLists']['all'] if sec not in nonSpiny]
    nonSpinyEE = ['axon_0', 'axon_1', 'soma']
    netParams.cellParams[cellName]['secLists']['spinyEE'] = [sec for sec in netParams.cellParams[cellName]['secLists']['all'] if sec not in nonSpinyEE]    
    
    # ---------------------------------------------------------------------------------------------------- #
    for ii in range(5):
        netParams.popParams[cellName + '_' + str(ii)] = {'cellType': cellName, 'numCells': 1, 'cellModel': 'HH_full'}

# ---------------------------------------------------------------------------------------------------- #
spkTimes = [1000]
netParams.popParams['presyn'] = {'cellModel': 'VecStim', 'numCells': 1, 'spkTimes': spkTimes}  # VecStim with spike times

# ---------------------------------------------------------------------------------------------------- #
#BBP	gsyn	decay	       use	     dep	 fac	types	rules
# 5	0.91±0.61	6.44±1.70	0.32±0.140	144±80	62±31	I3-IE	SBC_bNAC or LBC-NBC_(cNAC dSTUT cSTUT bSTUT):Excitatory
for ii in range(100):
    netParams.synMechParams['INH:L5_PC'+str(ii+1)] = {'mod': 'DetGABAAB',
                                         'Use': 0.32,
                                         'Dep': 144.0,
                                         'Fac': 62.0,
                                         'tau_d_GABAA': 6.44,
                                         'tau_r_GABAA': 0.2,   #rng.lognormal(0.2, 0.1) in synapses.hoc  
                                         'tau_d_GABAB': 260.9,
                                         'tau_r_GABAB': 3.5,
                                         'e_GABAA': cfg.gabaVrev, #= -80   (mV) : GABAA reversal potential    
                                            }

import random

## Cell connectivity rules
for ii in range(100):
    
    listsecs = random.sample(netParams.cellParams[cellName]['secLists']['spiny'], len(netParams.cellParams[cellName]['secLists']['spiny']))

    netParams.connParams['pre->post'+str(ii+1)] = { 
            'preConds': {'pop': 'presyn'},
            'postConds': {'pop': list(netParams.popParams.keys())[ii]},
            'sec': listsecs,                  # target postsyn section
            'synMech': 'INH:L5_PC'+str(ii+1),              # target synaptic mechanism
            'weight': 0.91, # weight[ii], # # synaptic weight 
            'synsPerConn': 15, 
            'delay': 0.05}       
    

sim.initialize(
    simConfig = cfg, 	
    netParams = netParams)  				# create network object and set cfg and net params
sim.net.createPops()               			# instantiate network populations
sim.net.createCells()              			# instantiate network cells based on defined populations
sim.net.connectCells()            			# create connections between cells based on params

sim.net.addStims() 							# add network stimulation
sim.setupRecording()              			# setup variables to record for each cell (spikes, V traces, etc)

sim.runSim()                      			# run Neuron simulation  

sim.gatherData()                  			# gather spiking data and cell info from each node
sim.saveData()                    			# save params, cell info and sim output to file (pickle,mat,txt,etc)#
sim.analysis.plotData()         			# plot spike raster etc


alltraces = []
gmax1 = []

Traces2 = sim.analysis.plotTraces(oneFigPer='trace', overlay=1, timeRange=[999,1099],axis=False,legend=False,scaleBarLoc=1,figSize=(10, 3),fontSize=6)
for number in range(100):
    if np.max(Traces2[1]['tracesData'][number]['cell_'+str(number)+'_V_soma'])-np.min(Traces2[1]['tracesData'][number]['cell_'+str(number)+'_V_soma']) > 0.01:
        alltraces.append(Traces2[1]['tracesData'][number]['cell_'+str(number)+'_V_soma'])
        gmax1.append(np.max(Traces2[1]['tracesData'][number]['cell_'+str(number)+'_V_soma'])-np.min(Traces2[1]['tracesData'][number]['cell_'+str(number)+'_V_soma']))
#         print(number,np.max(Traces2[1]['tracesData'][number]['cell_'+str(number)+'_V_soma'])-np.min(Traces2[1]['tracesData'][number]['cell_'+str(number)+'_V_soma']))

figSize = (8,12)
fig = plt.figure(figsize=figSize)  # Open a new figure
for number in range(np.shape(alltraces)[0]):
    plt.plot(alltraces[number]-alltraces[number][0],color = 'lightgray',linewidth=2.0)

plt.title('PSP ->  %.2f ± %.2f mV' % (np.mean(gmax1),np.std(gmax1)), fontsize=14)
plt.plot(np.mean(alltraces, axis=0)-np.mean(alltraces, axis=0)[0],color = 'black', linewidth=4.0)
# plt.legend(loc='upper right', bbox_to_anchor=(0.95, 1.0))
plt.xlim(0,1000)
plt.ylim(-2.0,2.0)
plt.xlabel('Time (ms)', fontsize=16)
plt.ylabel('PSP (mV)', fontsize=16)
plt.xticks(range(0,1000,200), range(0,100,20), fontsize=14);
plt.yticks([-1.0,-1.0], fontsize=14); 

plt.savefig(cfg.filename + '.png', facecolor = 'white' , dpi=300)

print(np.mean(gmax1), np.size(gmax1))