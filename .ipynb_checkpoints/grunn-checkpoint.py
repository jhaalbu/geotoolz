import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
#import geofunk

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
        Setter styrkeparametere for laget.

        Parameters
        ----------
        phi : float
            Friksjonsvinkel for laget, i grader.
        attraksjon : float, optional
            Attralsjon i kPa, blir rekna ut dersom kohesjon er gitt. The default is 0.
        kohesjon : float, optional
            kohesjon i kPa, blir rekna ut dersom attraksjon er gitt. The default is 0.
        cu : float, optional
            Udrenert skjærfasthet i kPa. The default is 0.

        Returns
        -------
        None.

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
        '''
        Setter stivhet for laget. Returnerer ingen ting. Det bør den kanskje gjere?

        Parameters
        ----------
        m : int, optional
            modultall. The default is 0.
        M : TYPE, optional
            stivhetsmodul. The default is 0.

        Returns
        -------
        None.

        '''
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
    
    def primerkonsolidering_tid(self, cv):
        '''

        Parameters
        ----------
        cv : float
            konsolideringskoeffisient (m^2/år)

        Returns
        -------
        tp: float
            tiden for 95% konsolidering (år).

        '''
        h = (self.mektighet/2)/100
        self.tp = h**2 / cv
        return self.tp
        
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
        self.df['fill'] = 0
        #print(self.df)

    def setning_uendelig(self, q):
        self.df['delta_p'] = q
        self.df = self.df.assign(toyning=lambda x:(1/x.m) * np.log((x.sigma_v0 + q)/x.sigma_v0))
        self.df = self.df.replace([np.inf, -np.inf], 0)
        self.df['delta_sigma'] = self.df['toyning'] * 0.01
        self.df['sigma'] = self.df['delta_p'] + self.df['sigma_v0']
        self.df['toyning_prosent'] = self.df['toyning']*100
        return
    
    def setning_endelig(self, q, b, l):
        z0 = np.pi*((b*l)/(b+l))
        self.df['delta_p'] = q * (1-(self.df.index / z0))
        self.df.loc[self.df['delta_p']<0,'delta_p']=0
        self.df = self.df.assign(toyning=lambda x:(1/x.m) * np.log((x.sigma_v0 + x.delta_p)/x.sigma_v0))
        self.df = self.df.replace([np.inf, -np.inf], 0)
        self.df['toyning_prosent'] = self.df['toyning']*100
        self.df['delta_sigma'] = self.df['toyning'] * 0.01
        self.df['sigma'] = self.df['delta_p'] + self.df['sigma_v0']
        return
        
    def total_setning(self):
        return round(self.df['delta_sigma'].sum(),3)
    
    def plot_toyning(self, ax1=None):
        if ax1 is None:
            ax1 = plt.gca()
        
        ax1.plot(self.df.sigma_v0, self.df.index, color='r', label="\u03C3\u2080'")
        ax1.plot(self.df.delta_p, self.df.index, color='g', label="\u0394\u03C3")
        ax1.plot(self.df.sigma, self.df.index, color='cyan', label="\u03C3")
        ax1.legend()
        ax1.invert_yaxis()
        ax2 = ax1.twiny()
        #ax2.plot(self.df.fill, self.df.index)
        ax2.plot(self.df.toyning_prosent[1:], self.df.index[1:], label="\u03B5")
        #ax2.fill_between(self.df.toyning_prosent[1:], self.df['fill'], step="pre", alpha=0.4)
        ax2.legend()
        ax2.set_xlim(0, self.df.toyning_prosent.max())
        ax1.set_ylabel("Djupne (cm)")
        ax2.set_xlabel("Tøyning (%)")
        ax1.set_xlabel("Spenning (kPa)")
        
        return ax1, ax2





    
