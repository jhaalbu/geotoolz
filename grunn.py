import pandas as pd
import numpy as np
import math
import geofunk

class JordLag(object):

    def __init__(self, lagnavn, mektighet=None, gamma=None, startdybde=None, sluttdybde=None) -> None:
        self.lagnavn = lagnavn
        self.startdybde = startdybde
        self.sluttdybde = sluttdybde
        self.gamma = gamma/100
        if self.startdybde == None:
            self.mektighet = mektighet
        else:
            self.mektighet = self.sluttdybde - self.startdybde
        self.df = pd.DataFrame({"lagdjupne": range(0, (self.mektighet)+1)})
        self.df["lagnavn"] = self.lagnavn
        self.df["gamma"] = self.gamma

    def __str__(self) -> str:
        return f"Jordart: {self.lagnavn}, Mektighet: {self.mektighet}"

    
    def sett_styrke_parameter(self, phi, attraksjon=0, kohesjon=0, cu=0):
        '''
        Ipunt friksjonsvinkel til laget samt attraksjon og kohesjon
        Dersom ein av attraksjon eller kohesjon blir gitt blir andre rekna ut
        '''
        self.phi = phi
        self.attraksjon = attraksjon
        self.kohesjon = kohesjon
        self.tanphi = math.tan(math.radians(self.phi))
        self.cu = cu
        
        if kohesjon == 0 and attraksjon != 0:
            self.kohesjon = attraksjon * self.tanphi
        if attraksjon == 0 and kohesjon !=0:
            self.attraksjon = kohesjon/self.tanphi
        
        self.df['phi'] = self.phi
        self.df['tanphi'] = self.tanphi
        self.df['attraksjon'] = self.attraksjon
        return
        
    def sett_stivhet(self, m=0, M=0):
        self.m = m
        self.M = M
        if self.m == 0 and self.M != 0:
            self.df['M'] = self.M
            return
        elif self.M == 0 and self.m != 0:
            self.df['m'] = self.m
            return
        else:
            return
#TODO: I jordprofilklassen er det ein bug som gjer at det blir ein cm ekstra per lag
#       Antar denne buggen kjem fra at alle lag startar med 0 cm, ein ekstra cm her
class JordProfil(object):

    def __init__(self, jordarter, u=1.0) -> None:
        self.jordarter = jordarter
        self.u = u
        self.df = pd.concat([jordlag.df for jordlag in self.jordarter],
                            keys=[jordlag.lagnavn for jordlag in self.jordarter])
        self.df['djupne'] = range(0, len(self.df))
        self.df['djupne_meter'] = self.df["djupne"]/100
        self.df = self.df.set_index('djupne')
        self.df['u'] = 0
        self.df.loc[self.df["djupne_meter"] > self.u, 'u'] = self.df['djupne_meter'] * 10 - self.u*10
        self.df["sigma_v0"] = self.df['gamma'].cumsum().shift(1, fill_value=0) - self.df['u']
        #print(self.df)

    def setning_uendelig(self, q):
        self.df['delta_p'] = q
        self.df = self.df.assign(toyning=lambda x:(1/x.m) * np.log((x.sigma_v0 + q)/x.sigma_v0))
        self.df = self.df.replace([np.inf, -np.inf], 0)
        self.df['delta_sigma'] = self.df['toyning'] * 0.01
        return
    
    def setning_endelig(self, q, b, l):
        z0 = np.pi*((b*l)/(b+l))
        print(f'z0 = {z0}')
        self.df['delta_p'] = q * (1-(self.df.index / z0))
        self.df.loc[self.df['delta_p']<0,'delta_p']=0
        self.df = self.df.assign(toyning=lambda x:(1/x.m) * np.log((x.sigma_v0 + x.delta_p)/x.sigma_v0))
        self.df = self.df.replace([np.inf, -np.inf], 0)
        self.df['delta_sigma'] = self.df['toyning'] * 0.01
        return
        
    def total_setning(self):
        return round(self.df['delta_sigma'].sum(),3)





    
