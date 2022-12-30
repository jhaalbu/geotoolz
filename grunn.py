import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import geofunk

class JordLag(object):

    def __init__(self, lagnavn, mektighet=None, gamma=None, startdybde=None, sluttdybde=None) -> None:
        '''
        Etablerer eit jordlag

        Perameters
        ----------
        lagnavn
        '''
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
        self.df["gamma"] = self.gamma/100

    def __str__(self) -> str:
        return f"Jordart: {self.lagnavn}, Mektighet: {self.mektighet}"

    
    def sett_styrke_parameter(self, phi=0, tanphi=0, attraksjon=0, kohesjon=0, cu=0):
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
        self.tanphi = tanphi
        if self.phi == 0:
            self.phi = round(math.degrees(math.atan(self.tanphi)))
        if self.tanphi == 0:
            self.tanphi = round(math.tan(math.radians(self.phi)),2)
        #self.phi = phi
        self.attraksjon = attraksjon
        self.kohesjon = kohesjon
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
class JordProfil():

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
    
    def __str__(self):
        jordlagbeskrivelse = f"Lag i Jordprofilet\n"
        for lag in self.jordarter:
            jordlagbeskrivelse += f"Lag med navn: {lag.lagnavn} med mektihget: {lag.mektighet/100} m\n Parametere:  \n phi={lag.phi}, tanphi={lag.tanphi}, attraksjon={lag.attraksjon}, kohesjon={lag.kohesjon}, cu={lag.cu} \n"
            
        return jordlagbeskrivelse

    def get_tan_phi_lag(self, lagnavn='', lagnr=0):
        if not lagnavn:
            return self.jordarter[lagnr].tanphi
        if lagnr == 0:
            for lag in self.jordarter:
                if lag.lagnavn == lagnavn:
                    return lag.tanphi
    
    def get_phi_lag(self, lagnavn='', lagnr=0):
        if not lagnavn:
            return self.jordarter[lagnr].phi
        if lagnr == 0:
            for lag in self.jordarter:
                if lag.lagnavn == lagnavn:
                    return lag.phi

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




class Fundament(object):

    def __init__(self, b, z, fv, fh, gamma_m, tykkelse, m=None):
        self.b = b
        self.z = z
        self.fv = fv
        self.fh = fh
        self.m = m
        self.gamma_m = gamma_m
        self.tykkelse = tykkelse
        
 
        if m == None or m == 0:
            self.b0 = self.b
        else:
            self.b0 = self.b - (2 * (self.m/self.fv))
        
        print(self.b0)
        self.qv = self.fv/self.b0
        self.tau = self.fh/self.b0

    def sett_delta_fv(self, gamma,u):
        self.gamma = gamma
        self.u = u
        self.delta_fv = (self.gamma*self.z*self.b0)/self.b0
        self.qv = self.qv + self.delta_fv
        return self.qv

    def sett_rb(self, tan_fi_d, attraksjon):
        self.tan_fi_d = tan_fi_d
        self.attraksjon = attraksjon
        self.rb = self.tau / ((self.qv + self.attraksjon) * self.tan_fi_d)
        return self.rb
    
    def nq_ngamma_faktor(self, helling=100000):
        self.helling = helling
        self.nq, self.n_gamma = geofunk.n_fakt(self.tan_fi_d, self.rb, self.helling)
        return self.nq, self.n_gamma

    def reduksjonsfaktor_v220(self, helling_forhold):
        self.helling_forhold = helling_forhold
        #self.fsa, self.fsq = geofunk.reduksjonsfaktor_v220(self.helling_forhold, self.tan_fi_d)
        self.fsa = 0.73
        self.fsq = 0.36
        return self.fsa, self.fsq

#TODO: Må finne gamma under fundament, ta inn geolag for å gjere dette?? 


    def sigma_v(self):
        self.p_merka = self.gamma * self.z
        self.sigma_v_ = (self.fsq * ((self.nq*self.p_merka)+(0.5*self.n_gamma*self.gamma*self.b0))) + (((self.nq * self.fsa)-1)*self.attraksjon)
        return self.sigma_v_
    
    def sigma_v2(self):
        self.p_merka = self.gamma * self.z
        self.sigma_v_2 = (0.36 * ((self.nq*self.p_merka)+(0.5*self.n_gamma*(self.gamma-10)*self.b0))) + (((self.nq * 0.73)-1)*self.attraksjon)
        return self.sigma_v_2

    