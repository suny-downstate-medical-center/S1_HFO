import h5py
import json
import numpy as np
import os
import sys
from matplotlib import pyplot as plt

rootFolder = '/home/fernando/Dropbox/SUNY/2022/S1_netpyne/sim/'
# rootFolder = os.getcwd()
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

def runnetpyne(cellnumber):

    os.chdir(rootFolder)
    from netpyne import sim
    from netpyne import specs
    import pickle

    cfg = specs.SimConfig()     
    
    cfg.duration = timesimulation ## Duration of the sim, in ms  
    cfg.dt = 0.025
    cfg.seeds = {'conn': 4321, 'stim': 1234, 'loc': 4321} 
    cfg.hParams = {'celsius': 34, 'v_init': -65}  
    cfg.verbose = False
    cfg.createNEURONObj = True
    cfg.createPyStruct = True
    cfg.cvode_active = False
    cfg.cvode_atol = 1e-6
    cfg.cache_efficient = True
    cfg.printRunTime = 0.5
    
    cfg.includeParamsLabel = False
    cfg.printPopAvgRates = True
    cfg.checkErrors = False
    
    allpops = ['L1_'+str(ii) for ii in range(1,13)]

    cfg.recordCells = allpops  # which cells to record from
    cfg.recordTraces = {'V_soma': {'sec':'soma_0', 'loc':0.5, 'var':'v'}}  ## Dict with traces to record
    cfg.recordStim = True
    cfg.recordTime = True
    cfg.recordStep = 0.025            

    cfg.simLabel = 'S1_single'
    cfg.saveFolder = '.'
    # cfg.filename =                	## Set file output name
    cfg.savePickle = False         	## Save pkl file
    cfg.saveJson = False           	## Save json file
    cfg.saveDataInclude = ['simConfig', 'netParams'] ## 'simData' , 'simConfig', 'netParams'
    cfg.backupCfgFile = None 		##  
    cfg.gatherOnlySimData = False	##  
    cfg.saveCellSecs = False			##  
    cfg.saveCellConns = False		##  

    #------------------------------------------------------------------------------
    # Current inputs 
    #------------------------------------------------------------------------------
    cfg.addIClamp = True

    cfg.IClamp = []
    cfg.IClampnumber = 0
    
    for popName in allpops:
        cfg.IClamp.append({'pop': popName, 'sec': 'soma_0', 'loc': 0.5, 'start': delaystim, 'dur': durationstim, 'amp': ampstim[cfg.IClampnumber]}) #pA
        cfg.IClampnumber=cfg.IClampnumber+1

    #------------------------------------------------------------------------------
    #------------------------------------------------------------------------------
    #------------------------------------------------------------------------------

    netParams = specs.NetParams()   # object of class NetParams to store the network parameters

    #------------------------------------------------------------------------------
    # Cell parameters
    #------------------------------------------------------------------------------
    #StochKv_deterministic.mod
    cellName = folder[cellnumber]
    cellTemplateName = loadTemplateName(cellnumber)
    cellRule = netParams.importCellParams(label=cellName + '_rule', somaAtOrigin=False,
        conds={'cellType': cellName, 'cellModel': 'HH_full'},
        fileName='cellwrapper3.py',
        cellName='loadCell',
        cellInstance = True,
        cellArgs={'cellName': cellName, 'cellTemplateName': cellTemplateName})

    #------------------------------------------------------------------------------
    # Population parameters
    #------------------------------------------------------------------------------

    netParams.popParams['L1_1'] = {'cellType': cellName, 'cellModel': 'HH_full', 'numCells': 1} 
    netParams.popParams['L1_2'] = {'cellType': cellName, 'cellModel': 'HH_full', 'numCells': 1} 
    netParams.popParams['L1_3'] = {'cellType': cellName, 'cellModel': 'HH_full', 'numCells': 1} 
    netParams.popParams['L1_4'] = {'cellType': cellName, 'cellModel': 'HH_full', 'numCells': 1} 
    netParams.popParams['L1_5'] = {'cellType': cellName, 'cellModel': 'HH_full', 'numCells': 1} 
    netParams.popParams['L1_6'] = {'cellType': cellName, 'cellModel': 'HH_full', 'numCells': 1} 
    netParams.popParams['L1_7'] = {'cellType': cellName, 'cellModel': 'HH_full', 'numCells': 1} 
    netParams.popParams['L1_8'] = {'cellType': cellName, 'cellModel': 'HH_full', 'numCells': 1} 
    netParams.popParams['L1_9'] = {'cellType': cellName, 'cellModel': 'HH_full', 'numCells': 1} 
    netParams.popParams['L1_10'] = {'cellType': cellName, 'cellModel': 'HH_full', 'numCells': 1} 
    netParams.popParams['L1_11'] = {'cellType': cellName, 'cellModel': 'HH_full', 'numCells': 1} 
    netParams.popParams['L1_12'] = {'cellType': cellName, 'cellModel': 'HH_full', 'numCells': 1} 

    #------------------------------------------------------------------------------
    # Current inputs (IClamp)
    #------------------------------------------------------------------------------
    for j in range(cfg.IClampnumber):
        key ='IClamp'
        params = getattr(cfg, key, None)
        key ='IClamp'+str(j+1)
        params = params[j]
        [pop,sec,loc,start,dur,amp] = [params[s] for s in ['pop','sec','loc','start','dur','amp']]

        # add stim source
        netParams.stimSourceParams[key] = {'type': 'IClamp', 'delay': start, 'dur': dur, 'amp': amp}
        
        # connect stim source to target
        netParams.stimTargetParams[key+'_'+pop] =  {
            'source': key, 
            'conds': {'pop': pop},
            'sec': sec, 
            'loc': loc}
    
    #------------------------------------------------------------------------------
    sim.createSimulateAnalyze(netParams, cfg)
    
    netpyneTraces = []
    netpyneTracesList = []
    for c in range(0,12):
        netpyneTraces.append(np.array(sim.simData['V_soma']['cell_'+ str(c)]))
        netpyneTracesList.append(list(sim.simData['V_soma']['cell_'+ str(c)]))        
 
    return netpyneTraces

def compareTraces(cellnumber):  

    import efel    

    netpyneTraces = runnetpyne(cellnumber)

    # plot traces
    fontsiz=18
    timeRange = [0, timesimulation]
    recordStep = 0.025
    # ~ ylim = [-100, 40]
    figSize = (24,24)
    fig = plt.figure(figsize=figSize)  # Open a new figure

    # fig.suptitle('%s' % (cellName), fontsize=15, fontweight='bold')
                    
    t = np.arange(timeRange[0], timeRange[1]+recordStep, recordStep) 
    
    for c in range(0,12):
        netpyneTrace = netpyneTraces[c]
        plt.subplot(12, 1, c+1)
        plt.ylabel('V (mV)', fontsize=fontsiz)
        plt.plot(t[:len(netpyneTrace)], netpyneTrace, linewidth=2.0, color='red', label='Step %d'%(int(c+0))+', NetPyNE')
        plt.xlabel('Time (ms)', fontsize=fontsiz)
        plt.xlim(0, timesimulation)
        # ~ plt.ylim(ylim)
        plt.grid(False)
        # plt.legend(loc='upper right', bbox_to_anchor=(0.20, 0.7))
    plt.ion()
    plt.tight_layout()
    
    plt.savefig('/home/fernando/Figures_step2sec/comparison_traces_soma_voltage_4steps_%s.png' % cellName, facecolor = 'white' , dpi=300)


    traces = []
    for c in range(12):
        
        netpyneTrace = netpyneTraces[c]
        trace = {}
        trace['T'] = t[:len(netpyneTrace)]
        trace['V'] = netpyneTrace
        trace['stim_start'] = [delaystim]
        trace['stim_end'] = [delaystim+durationstim]
        traces.append(trace)

    feature_items = ['Spikecount', 'mean_frequency', 'peak_time', 'peak_voltage', 'ISI_CV', 'AP_width', 'AP_amplitude','voltage_base']
    feature_values = efel.getFeatureValues(traces, feature_items, raise_warnings=False)


    json_file = {}
    IpA = 100.0

    for ii in range(12): 

        json_file['step_'+str(ii+1)] = {}

        json_values = efel.getFeatureValues([traces[ii]], ['Spikecount', 'mean_frequency', 'peak_time', 'peak_voltage', 'ISI_CV', 'AP_width', 
                                                               'AP_amplitude','voltage_base','all_ISI_values', 'ISI_CV', 'steady_state_voltage_stimend'], raise_warnings=False)[0]                              

        for feature_name, values in json_values.items():
            json_file['step_'+str(ii+1)][feature_name] = []
            try:
                for val in values:
                    json_file['step_'+str(ii+1)][feature_name].append(float('%.2f' % val))
            except:
                json_file['step_'+str(ii+1)][feature_name].append(0.00)


        json_file['step_'+str(ii+1)]['IpA'] = IpA  
        IpA = IpA + 100.0


    # Save json file directly from dictionary
    with open('/home/fernando/Figures_step2sec/info_efel_12steps_NetPyNE_%s.json' % cellName, 'w') as outfile:
        json.dump(json_file, outfile) #, indent = 5


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print ("Script need a cell number between 0 and 1034")
    elif int(sys.argv[1])>=0 and int(sys.argv[1])<=1034:
        print ("Netpyne Traces of:")
        cellnumber = int(sys.argv[1])
        cellName = folder[cellnumber]
        outFolder = rootFolder+'/cell_data/'+folder[cellnumber]
        cellTemplateName = loadTemplateName(cellnumber)
        print ("CellNumber = %d" % cellnumber)
        print ("CellName = %s" % cellName)
        print ("TemplateName = %s" % cellTemplateName)

        ampstim =  [0.1*ii for ii in range(1,13)]

        durationstim = 2000
        delaystim = 700
        timesimulation = 3000
            
        compareTraces(cellnumber)             
        
    else:
        raise Exception('Script need a cell number between 0 and 1034')
