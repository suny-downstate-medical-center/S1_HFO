"""
script to load sim and plot
"""

from netpyne import sim
from matplotlib import pyplot as plt
import os
import pickle
import numpy as np
#------------------------------------------------------------------------------  
# S1 Cells
# Load 55 Morphological Names and Cell pop numbers -> L1:6 L23:10 L4:12 L5:13 L6:14
# Load 207 Morpho-electrical Names used to import the cells from 'cell_data/' -> L1:14 L23:43 L4:46 L5:52 L6:52
# Create [Morphological,Electrical] = number of cell metype in the sub-pop

with open('cells/S1-cells-distributions-Rat.txt') as mtype_file:
    mtype_content = mtype_file.read()       

popNumber = {}
cellNumber = {} 
popLabel = {} 
cellLabel = {}

for line in mtype_content.split('\n')[:-1]:
    cellname, mtype, etype, n, m = line.split()
    metype = mtype + '_' + etype[0:3]
    cellNumber[metype] = int(n)
    popLabel[metype] = mtype
    popNumber[mtype] = int(m)
    cellLabel[metype] = cellname

#------------------------------------------------------------------------------  
# Thalamic Cells

thalamicpops = ['ss_RTN_o', 'ss_RTN_m', 'ss_RTN_i', 'VPL_sTC', 'VPM_sTC', 'POm_sTC_s1']

cellNumber['ss_RTN_o'] = int(382 * (210**2/150**2)) # from mouse model (d = 150 um)
cellNumber['ss_RTN_m'] = int(382 * (210**2/150**2))
cellNumber['ss_RTN_i'] = int(765 * (210**2/150**2))
cellNumber['VPL_sTC'] = int(656 * (210**2/150**2))
cellNumber['VPM_sTC'] = int(839 * (210**2/150**2))
cellNumber['POm_sTC_s1'] = int(685 * (210**2/150**2))

for mtype in thalamicpops: # No diversity
	metype = mtype
	popLabel[metype] = mtype
	popNumber[mtype] = cellNumber[metype]

#------------------------------------------------------------------------------
# load data from S1 Raster
#------------------------------------------------------------------------------

## Load spkTimes and cells positions
with open('../data/spkTimes_v9_batch8.pkl', 'rb') as fileObj: simData = pickle.load(fileObj)
spkTimes = simData['spkTimes']
cellsTags = simData['cellsTags']

# create custom list of spike times
cellsVSName = {}
for cellLabel in spkTimes.keys():    
    cellme = cellLabel.split('_')[0:-1]    
    metype = cellme[0]
    for i in range(1,np.size(cellme)):
        metype += '_' + cellme[i]
                   
    if metype not in cellsVSName.keys():
        cellsVSName[metype] = []
        
    mtype = popLabel[metype]            
    cellsVSName[metype].append('presyn_'+cellLabel)

#------------------------------------------------------------------------------
cynradNumber = 1
fracmorphoradius = 1.0/2.0

excluderadius2a = (cynradNumber-1)*(0.5*fracmorphoradius)**2
excluderadius2b = (cynradNumber)*(0.5*fracmorphoradius)**2

Nmorpho = {}    
listmorphonumber = {}

print('radius from',420*np.sqrt(excluderadius2a),'to',420*np.sqrt(excluderadius2b),'micrometers')

#------------------------------------------------------------------------------
# create 1 vectstim pop per cell gid
for metype in cellsVSName.keys(): # metype
       
    for cellLabel in cellsVSName[metype]: # all cells in metype

        mtype = popLabel[metype]    
        ii = int(cellLabel.split('_')[-1])
        radiuscCell2 = (cellsTags[ii]['xnorm']-0.5)**2 + (cellsTags[ii]['znorm']-0.5)**2

        if metype[0] == 'L' and radiuscCell2 >= excluderadius2a and radiuscCell2 < excluderadius2b:   

            if metype not in listmorphonumber.keys():
                listmorphonumber[metype] = []

            listmorphonumber[metype].append(ii)     

            if metype not in Nmorpho.keys():
                Nmorpho[metype] = 0

            Nmorpho[metype] += 1

#------------------------------------------------------------------------------
Epopsall = ['L23_PC', 'L4_PC', 'L4_SS', 'L4_SP', 
             'L5_TTPC1', 'L5_TTPC2', 'L5_STPC', 'L5_UTPC',
             'L6_TPC_L1', 'L6_TPC_L4', 'L6_BPC', 'L6_IPC', 'L6_UTPC']
Ipops = []
Epops = [] 
S1pops = []
S1cells = []
popLabelEl = {}

for metype in  Nmorpho.keys(): # metype      
    if  Nmorpho[metype] > 0:  
        S1cells.append(metype)
        mtype = popLabel[metype]            
        if mtype in Epopsall:            
            if mtype not in Epops:
                Epops.append(mtype)
                S1pops.append(mtype)
                popLabelEl[mtype] = [] 
            popLabelEl[mtype].append(metype)            
        else:            
            if mtype not in Ipops:                
                Ipops.append(mtype)  
                S1pops.append(mtype)  
                popLabelEl[mtype] = [] 
            popLabelEl[mtype].append(metype)      

Ecells = [] 
Icells = [] 
for metype in S1cells: # metype      
    mtype = popLabel[metype]            
    if mtype in Epopsall:  
        Ecells.append(metype)      
    else:  
        Icells.append(metype)

#------------------------------------------------------------------------------  
#
#------------------------------------------------------------------------------  
popParamLabels = S1pops
cellParamLabels = S1cells

#--------------------------------------------------------------------------
# Recording 
#--------------------------------------------------------------------------
allpops = cellParamLabels

RP_L13 = []
RP_L45 = []
RP_L6 = []

for metype in S1cells:

    layernumber = float(metype[1:2])
    if cellNumber[metype]*0.01 > 0.0:
        if int(layernumber) <= 3:
            RP_L13.append(metype)
            # print(layernumber,int(layernumber),metype)
        elif int(layernumber) == 6:
            RP_L6.append(metype)
            # print(layernumber,int(layernumber),metype)
        else:
            RP_L45.append(metype)
            # print(layernumber,int(layernumber),metype)

###########################
######## MAIN CODE ########
###########################

if __name__ == '__main__':

    dataType = 'spont' #'speech' #'spont'

    if dataType == 'spont':
        filenames = ['../data/v109_batch3/v109_batch3_data.pkl']
        timeRange = [9000, 10000]

    layer_bounds= {'1':[0.0, 0.079], '2': [0.079,0.151], '3': [0.151,0.320], '23': [0.079,0.320], '4':[0.320,0.412], '5': [0.412,0.664], '6': [0.664,1.0]}

    allData = []

    for filename in filenames:

        sim.load(filename, instantiate=True, instantiateConns = False, instantiateStims = False, instantiateRxD = False, createNEURONObj = False)

        # standardd plots
        # sim.analysis.plotRaster(**{'include': ['allCells'], 'saveFig': True, 'showFig': False, 'labels': None, 'popRates': False,'orderInverse': True, 'timeRange': timeRange, 'figSize': (48,36), 'fontSize':4, 'lw': 2, 'markerSize':2, 'marker': '.', 'dpi': 300})
        # sim.analysis.plotRaster(**{'include': RP_L13, 'saveFig': filename[:-4]+'_RP_L13', 'showFig': False, 'popRates': 'minimal', 'orderInverse': True, 'timeRange': timeRange, 'orderBy':'y', 'fontSize':8, 'figSize': (24,12), 'lw': 4.0, 'markerSize': 4, 'marker': 'o', 'dpi': 300})
        sim.analysis.plotRaster(**{'include': RP_L45, 'saveFig': filename[:-4]+'_RP_L45.png', 'showFig': False, 'popRates': 'minimal', 'orderInverse': True, 'timeRange': timeRange, 'orderBy':'y', 'fontSize':8, 'figSize': (24,18), 'lw': 4.0, 'markerSize': 4, 'marker': 'o', 'dpi': 300})
        # sim.analysis.plotRaster(**{'include': RP_L6, 'saveFig': filename[:-4]+'_RP_L6', 'showFig': False, 'popRates': 'minimal', 'orderInverse': True, 'timeRange': timeRange, 'orderBy':'y', 'fontSize':8, 'figSize': (24,12), 'lw': 4.0, 'markerSize': 4, 'marker': 'o', 'dpi': 300})
        # sim.analysis.plotSpikeStats(stats=['rate'],figSize = (6,12), timeRange=[1500, 31500], dpi=300, showFig=0, saveFig=filename[:-4]+'_stats_30sec')
        sim.analysis.plotSpikeStats(include=,stats=['rate'],figSize = (6,12), timeRange=[9000, 10000], dpi=300, showFig=0, saveFig=filename[:-4]+'_stats_1sec.png')
        #sim.analysis.plotLFP(**{'plots': ['spectrogram'], 'electrodes': ['avg', [0], [1], [2,3,4,5,6,7,8,9], [10, 11, 12], [13], [14, 15], [16,17,18,19]], 'timeRange': timeRange, 'maxFreq': 50, 'figSize': (8,24), 'saveData': False, 'saveFig': filename[:-4]+'_LFP_spec_7s_all_elecs', 'showFig': False})

        for mtype in Epops:
            sim.analysis.plotSpikeStats(include=,stats=['rate'],figSize = (6,12), timeRange=[9000, 10000], dpi=300, showFig=0, saveFig=filename[:-4] + '_' + mtype + '_stats_1sec.png')

        for mtype in Epops:
            print('\n\n',mtype,'  N =',popNumber[mtype])
            sim.analysis.plotTraces(include=popLabelEl[mtype], timeRange=timeRange, overlay=True, oneFigPer='trace', subtitles=False, legend=False, ylim=[-110,50], 
            axis=False, scaleBarLoc=3, figSize=(24, 2), fontSize=15, saveFig= filename[:-4] + '_' + mtype+ '_Vt.png');
                
        sim.analysis.plotTraces(include=RP_L45, timeRange=timeRange, overlay=True, oneFigPer='trace', subtitles=False, legend=False, ylim=[-110,50], axis=False, scaleBarLoc=3, figSize=(24, 2), fontSize=15, saveFig= filename[:-4]+ '_RP_L45_Vt.png');
        
        sim.analysis.plotSpikeHist(include=Ecells[0:1], binSize=2, figSize=(16, 8), timeRange=[9500, 9650], dpi=300, saveFig=filename[:-4] + '_L23Epops_hist_1sec.png')
        
        sim.analysis.plotSpikeHist(include=[Icells[0:14],Icells[19:54]], binSize=5, figSize=(16, 8), timeRange=[9500, 9650], dpi=300, saveFig=filename[:-4] + '_L13Ipops_hist_1sec.png')

        sim.analysis.plotSpikeHist(include=[popLabelEl[pop] for pop in Ipops[6:15] if popNumber[pop] > 80], binSize=2, figSize=(16, 8), timeRange=[9400, 9700], dpi=300, saveFig=filename[:-4] + '_L23Ipops_hist_1sec.png')

        sim.analysis.plotSpikeHist(include=popLabelEl['L23_BP'], binSize=2, figSize=(16, 8), timeRange=[9400, 9700], dpi=300, saveFig=filename[:-4] + '_L23Ipops_hist_1sec.png')

        sim.analysis.plotSpikeHist(include=[Ecells[0:1],Ecells[1:4],Ecells[4:8],Ecells[8:]], binSize=2, figSize=(16, 8), timeRange=[9400, 9700], dpi=300, saveFig=filename[:-4] + '_L45Epops_hist_1sec.png')

        sim.analysis.plotSpikeHist(include=[Icells[54:83],Icells[83:125]], binSize=50, figSize=(16, 8), timeRange=[5000, 10000], dpi=300, saveFig=filename[:-4] + '_L45Ipops_hist_5sec.png')
        sim.analysis.plotSpikeHist(include=[Ecells[1:4],Ecells[4:8]], binSize=50, figSize=(16, 8), timeRange=[5000, 10000], dpi=300, saveFig=filename[:-4] + '_L45Epops_hist_5sec.png')

        sim.analysis.plotSpikeHist(include=[Icells[54:83],Icells[83:125]], binSize=5, figSize=(16, 8), timeRange=[9400, 9550], dpi=300, saveFig=filename[:-4] + '_L45Ipops_hist_150msec.png')
        sim.analysis.plotSpikeHist(include=[Ecells[1:4],Ecells[4:8]], binSize=5, figSize=(16, 8), timeRange=[9400, 9550], dpi=300, saveFig=filename[:-4] + '_L45Epops_hist_150msec.png')

        sim.analysis.plotSpikeHist(include=[Ecells[1:4],Icells[54:83],Ecells[4:8],Icells[83:125]], binSize=50, figSize=(16, 8), timeRange=[5000, 10000], dpi=300, saveFig=filename[:-4] + '_L45_hist_5sec.png')

        sim.analysis.plotSpikeHist(include=[Ecells[1:4],Icells[54:83],Ecells[4:8],Icells[83:125]], binSize=5, figSize=(16, 8), timeRange=[9400, 9550], dpi=300, saveFig=filename[:-4] + '_L45_hist_150msec.png')

        sim.analysis.plotSpikeHist(include=[Ecells[1:4],Icells[54:83],Ecells[4:8],Icells[83:125]], binSize=5, figSize=(16, 8), timeRange=[9485, 9535], 
        dpi=300, histData=filename[:-4] + '_L45_hist_50msec.json', saveFig=filename[:-4] + '_L45_hist_50msec.png')


        sim.analysis.plotSpikeHist(include=[Ecells[1:4]], binSize=5, figSize=(16, 8), timeRange=[9400, 9500], dpi=300, saveFig=filename[:-4] + '_L45_hist_150msec.png')


        sim.analysis.plotSpikeHist(include=[Ecells[8:],Icells[125:]], binSize=50, figSize=(16, 8), timeRange=[5000, 10000], dpi=300, saveFig=filename[:-4] + '_L6_hist_5sec.png')

        sim.analysis.plotSpikeHist(include=[Ecells[8:],Icells[125:]], binSize=5, figSize=(16, 8), timeRange=[9400, 9550], 
        dpi=300, saveFig=filename[:-4] + '_L6_hist_150msec.png')



        sim.analysis.plotSpikeHist(include=[Ecells,Icells], binSize=50, figSize=(16, 8), timeRange=[5000, 10000], 
        dpi=300, saveFig=filename[:-4] + '_hist_5sec.png')

        sim.analysis.plotSpikeHist(include=[Ecells,Icells], binSize=2, figSize=(16, 8), timeRange=[9485, 9535], 
        dpi=300, saveFig=filename[:-4] + '_hist_50msec.png')
        
        sim.analysis.plotRaster(**{'include': RP_L45, 'saveFig': filename[:-4]+'_RP_L45_150msec.png', 'showFig': False, 'popRates': 'minimal', 'orderInverse': True, 'timeRange':[9400, 9550] , 'orderBy':'y', 'fontSize':8, 'figSize': (24,18), 'lw': 4.0, 'markerSize': 4, 'marker': 'o', 'dpi': 300})
        
# Icells[0:14],Icells[15:54],

        for pops in cellParamLabels:
            print('\n\n',pops,'  N =',cellNumber[pops])
            sim.analysis.plotTraces(include=[pops], timeRange=timeRange, overlay=True, oneFigPer='trace', subtitles=False, legend=False, ylim=[-110,50], axis=False, scaleBarLoc=3, figSize=(24, 2), fontSize=15, saveFig=filename[:-4] + '_' + pops+ '_Vt.png');
        
        # sim.analysis.plotRaster(**{'include': S1cells, 'saveFig': True, 'showFig': False, 'labels': None, 'popRates': False,'orderInverse': True, 'timeRange': timeRange, 'figSize': (36,24), 'fontSize':4, 'lw': 5, 'markerSize':10, 'marker': '.', 'dpi': 300})
                
        # sim.analysis.plotLFP(**{'plots': ['locations'], 
        #         'figSize': (24,24), 
        #         'saveData': False, 
        #         'saveFig': True, 'showFig': False, 'dpi': 300})

        # sim.analysis.plotLFP(**{'plots': ['timeSeries'], 
        #         # 'electrodes': 
        #         # [[0,1,2,3]], #'avg', 
        #         'timeRange': timeRange, 
        #         'figSize': (24,12), 'saveFig': True, 'showFig': False})

        # sim.analysis.plotLFP(**{'plots': ['spectrogram'], 
        #         # 'electrodes': 
        #         # [[0,1,2,3]],
        #         'timeRange': timeRange, 
        #         'minFreq': 100, 
        #         'maxFreq': 500, 
        #         'figSize': (16,12), 
        #         'saveData': False, 
        #         'saveFig': True, 'showFig': False})

        # sim.analysis.plotLFP(**{'plots': ['PSD'], 
        #         # 'electrodes': 
        #         # [[0,1,2,3]],
        #         'timeRange': timeRange, 
        #         'minFreq': 100, 
        #         'maxFreq': 500, 
        #         'figSize': (8,12), 
        #         'saveData': False, 
        #         'saveFig': True, 'showFig': False})
