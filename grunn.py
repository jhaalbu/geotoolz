import pandas as pd
import math
import geofunk

class JordLag(object):

    def __init__(self, lagnavn, mektighet=None, gamma=None, startdybde=None, sluttdybde=None) -> None:
        self.lagnavn = lagnavn
        self.startdybde = startdybde
        self.sluttdybde = sluttdybde
        self.gamma = gamma
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

class JordProfil(object):

    def __init__(self, jordarter) -> None:
        self.jordarter = jordarter
        self.df = pd.concat([jordlag.df for jordlag in self.jordarter],
                            keys=[jordlag.lagnavn for jordlag in self.jordarter])
        self.df['djupne'] = range(0, len(self.df))
        self.df = self.df.set_index('djupne')
        print(self.df)





    
