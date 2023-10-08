import numpy as np
from scipy.linalg import expm
import time as tim
from multiprocessing import Pool
import pickle


Dimk, Hkk, Kryk = pickle.load(open('hkk.pkl', 'rb'))

Kryk = np.linalg.qr(Kryk.T)[0].T #wrong_one

def Ua(t):
        return expm(1j *t * Hkk *Dimk)#wrong
def rho_eigenkk(t):
        Ua_t = Ua(t)
        
        Kryk_0 = np.transpose([Kryk[0]])
        return (
            np.conj(np.transpose(Ua_t))
            @ Kryk_0
            @ np.conj([Kryk[0]])
            @ Ua_t
        )


#for jj in range(10):
def wsykenkk(Dimk, t, x, y):
    def Akk(a1, a2):
        result = np.zeros((Dimk, Dimk), dtype=np.complex128)
        
        for l in range(Dimk):
            for lp in range(Dimk):
                if (l+lp)%Dimk != (2*a1)%Dimk: continue
                fact = np.exp(2j * np.pi * (a2 * (l - lp) / Dimk))
                result += fact * np.transpose(np.conj(np.transpose([Kryk[lp]]))@ [Kryk[l]])
                #print(l,lp)
        return result
    return (np.abs(np.trace(Akk(x, y) @ rho_eigenkk(t))))/Dimk
       

import argparse as arg


parser = arg.ArgumentParser(description='Find Accuracy')
parser.add_argument('-i', '--particle', dest='particle', type=str, default='ele', help="particle")

if __name__ == '__main__':
    parser = arg.ArgumentParser(description='Find Accuracy')
    parser.add_argument('-i', '--itr', dest='itr', type=str, default='0', help="itr")
    args = parser.parse_args()
    itr = args.itr
    begin = tim.time()
    iterations = 1
    num_processes = 4 # Adjust as needed
    timexy = pickle.load(open('iter_' + itr + '.pkl', 'rb'))
    #with Pool(num_processes) as pool:
    datai = []
    for jj in range(iterations):
        s = []
        #for time in np.arange(0, 10, 0.1):
        with Pool(num_processes) as pool:
            wsykenkk_steps = pool.starmap(wsykenkk, timexy)
        #print(np.shape(np.array(wsykenkk_steps)))
    with open('data_out_' + itr + '.pkl', 'wb') as f:
        pickle.dump([timexy, wsykenkk_steps], f)
    end = tim.time()
    print('time: ' + str(end-begin) + ' sec')
