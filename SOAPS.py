import argparse
import os
import sys

'''
This wrapper constructs shell command strings for each
  assembler from one set of arguments. This allows the user
  to easily run any combination of the three supported
  assemblers with control of assembler-shared-variables. 
  
  Note: Since these assemblers vary in their customizeablity,
  certain assembler options are not included. Specifically, 
  many SPAdes options were left out as the other assemblers 
  had no corresponding options. 
'''

##### Argument Parsing #####

#Setting up arguments
parser = argparse.ArgumentParser()
parser.add_argument("-pe",nargs='*',help="any number of paired end read files, given in order f_1 r_1 ... f_n r_n")
parser.add_argument("-ipe",help="single interlaced paired end read file")
parser.add_argument("-o",help="output directory")
parser.add_argument("-t",help="specify number of threads")
parser.add_argument("-klist",help="comma seperated list of k values(must be odd numbes, ordered smallest to largest). Only megahit and SPAdes affected. Will take priority over kstep for megahit")
parser.add_argument("-kstep",help="number we increment k-mer size each iteration. Must be 28 or lower. Only megahit and IDBA affected",type=int)
parser.add_argument("-contigmin",help="minimum contig length. Only megahit and IDBA affected",type=int)
#At least one of the assemblers must be chosen
parser.add_argument("--spades",help="run a SPAdes assembly instance",default=False,action="store_const", const=True)
parser.add_argument("--megahit",help="run a megahit assembly instance",default=False,action="store_const", const=True)
parser.add_argument("--idba",help="run an idba assembly instane",default=False,action="store_const", const=True)
args = parser.parse_args()

#Parsing argparse arguments
fwd,rev = [],[]
for idx, path in enumerate(args.pe):
    if((idx+1)%2==1):
        fwd.append(path) #forward file path
    else:
        rev.append(path) #reverse file path

interlaced = args.ipe #interlaced

out = args.o #output directory path
if(out[-1]=='/'):
    out = out[:-1]

t = args.t #number of threads
if(args.klist!=None):
    if(".csv" in args.klist): #can take csv file of k sizes as input
        kList = open(os.getcwd() + args.klist).read().replace('\n','')
else:
    kList = args.klist #Our list of k sizes can be used by megahit and SPAdes

kStep = args.kstep #kmer size increment value can be used by megahit and IDBA

contigMin = args.contigmin #minimum output contig length 

#which assemblers will be run (booleans)
spades = args.spades 
megahit = args.megahit
idba = args.idba



##### Running #####

spadesRun, megahitRun, idbaRun, fq2faRun = '','','','' #empty shell command strings

if(spades):
    spadesRun += "python3 "+os.getcwd()+"/SPAdes-3.10.1-Linux/bin/spades.py"
    if(interlaced==None): # multiple files
        i=0
        while(i<len(fwd)):
            spadesRun += " --pe"+str(i+1)+"-1 "+fwd[i]+" --pe"+str(i+1)+"-2 "+rev[i]
            i+=1
    else: # single interlaced file
        spadesRun += " -12 "+interlaced
    if(t!=None): # number of threads
        spadesRun += " -t "+t
    if(kList!=None): # list of k sizes
        spadesRun += " -k " +kList
    
    spadesRun+= " -o "+out+"/spades/"
    
    print("\nSPAdes"+"\n"+spadesRun)
    os.system(spadesRun)
if(megahit):
    megahitRun += os.getcwd() + "/megahit/megahit"
    if(interlaced==None): # paired end reads
        megahitRun += " -1 "
        for idx, f in enumerate(fwd):
            megahitRun += f 
            if(len(fwd)-1!=idx):
                megahitRun += ","
        megahitRun += " -2 "
        for idx, r in enumerate(rev): 
            megahitRun += r 
            if(len(rev)-1!=idx):
                megahitRun += ","
    if(t!=None): # number of threads
            megahitRun += " -t "+t
    megahitRun += " -o " + out+"/megahit"
    if(kList!=None): # list of k sizes
        megahitRun += " --k-list "+ kList
    elif(kStep!=None):
        megahitRun += " --k-step "+str(kstep)
    if(contigMin!=None):
            megahitRun += " --min-contig-len " + str(contigMin)
    print("\nmegahit"+"\n"+megahitRun)
    os.system(megahitRun)
if(idba):
    if(len(fwd)==1 and len(rev)==1):
        fq2faRun += os.getcwd()+ "/idba/bin/fq2fa --merge "+fwd[0]+" "+rev[0]+" "+out+"/idba/idba_merged.fa"
        print("\nfq2fa(IDBA)\n"+fq2faRun)
        os.system(fq2faRun)
    
        idbaRun += os.getcwd()+ "/idba/bin/idba_ud"
        if(t!=None): # number of threads
            idbaRun += " --num_threads "+t
        idbaRun += " -r "+out+"/idba/idba_merged.fa "+out+"/idba/"
        if(kStep!=None):
            idbaRun += " --step "+str(kstep)
        if(contigMin!=None):
            idbaRun += " --min_contig " + str(contigMin)
        print("\nIDBA\n"+idbaRun)
        os.system(idbaRun)
    else:
        print("\nIDBA\nIDBA does not support multi-read runs")
    


##### Parse Output #####    
    
#this section is meant to run quast.py on assembly output
# then create a report, which I had intended to parse and 
# add more info relevant to SOAPS
    
sys.exit(0)
