import numpy as np
from scipy.linalg import expm
import time as tim
from multiprocessing import Pool
import os
import argparse as arg
import pickle

parser = arg.ArgumentParser(description='Find Accuracy')
parser.add_argument('-c', '--cores', dest='cores', type=str, default='307', help="cores")
parser.add_argument('-d', '--dimk', dest='dimk', type=str, default='307', help="dimk")

args = parser.parse_args()

Dimk = int(args.dimk)
cores = int(args.cores)
outdir = 'tmp_' + str(Dimk) + '/'
def Generate_GUE(n):
    """Creates nxn GUE"""
    i = complex(0,1)
    Lambda_real = np.random.normal(scale=1/n,size=[n,n])
    Lambda_im = np.random.normal(scale=1/n,size=[n,n])
    Lambda = Lambda_real + Lambda_im * i
    G = (Lambda+Lambda.T.conjugate())/2
    return G
Hkk = Generate_GUE(Dimk)
Kryik = np.zeros(Dimk) 
Kryik[0] = 1.
Kryk = []
for i in range(0, Dimk):
        Kryk.append(np.dot(np.linalg.matrix_power(Hkk, i), Kryik))
        #print(i)
Kryk = np.array(Kryk)


os.makedirs(outdir + 'log', exist_ok=True)
os.system('cp run.sh ' + outdir)
os.system('cp run.py ' + outdir)

with open(outdir + "hkk.pkl","wb") as f:
    pickle.dump([Dimk, Hkk, Kryk],f)

timexy = [(Dimk,time,x,y) for time in np.arange(0, 7.5, 0.15) for x in range(Dimk) for y in range(Dimk)]
step = int(len(timexy)/cores)
for j in range(cores):
    timexy_step = timexy[j*step:(j+1)*step]
    with open(outdir + "iter_" + str(j) + ".pkl","wb") as f:
        pickle.dump(timexy_step, f)

os.system("cd " + outdir + "; tar -zcvf input.tar.gz *.pkl")

condorOutDir1="/eos/user/p/psuryade/ritam/out_" + str(Dimk)
os.system("xrdfs root://eosuser.cern.ch mkdir -p %s"%(condorOutDir1))
condorLogDir = 'log/'
common_command = \
'Universe   = vanilla\n\
should_transfer_files = YES\n\
when_to_transfer_output = ON_EXIT\n\
Transfer_Input_Files = input.tar.gz, run.sh, run.py\n\
x509userproxy = /afs/cern.ch/user/p/psuryade/private/ritam/x509up_u135619\n\
use_x509userproxy = true\n\
RequestCpus = 4\n\
+BenchmarkJob = True\n\
#+JobFlavour = "testmatch"\n\
+MaxRuntime = 259200\n\
Output = %slog_$(cluster)_$(process).stdout\n\
Error  = %slog_$(cluster)_$(process).stderr\n\
Log    = %slog_$(cluster)_$(process).condor\n\n'%(condorLogDir, condorLogDir, condorLogDir)

jdlFile = open(outdir + 'submit.jdl','w')
jdlFile.write('Executable =  run.sh \n')
jdlFile.write(common_command)
jdlFile.write("X=$(step)\n")
run_command =  'Arguments  = $INT(X) \nQueue ' + str(cores) + '\n\n'
jdlFile.write(run_command)
jdlFile.close() 
