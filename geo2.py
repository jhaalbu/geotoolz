# -*- coding: utf-8 -*-
"""
Created on Sat Nov  2 20:12:29 2019

@author: jhaal
"""

import math
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np 


class GeoLag(object):
    def __init__(self, jordart, mektighet=1, gamma=18):
        self.jordart = jordart
        self.mektighet = mektighet
        #self.ztopp = ztopp
        #self.zbunn = zbunn
        self.gamma = gamma
        #self.mektighet = zbunn - ztopp
        self.gamma_m = 1
        
        
#    def __str__(self):
#        return '''\
#        Jordart: %s 
#        Lagmektighet: %s
#        Tyngdetetthet: %s 
#        -------------------------\
#        ''' % (str(self.jordart), str(self.mektighet), str(self.gamma))
        
    
    def sett_gamma_m(self, gamma_m):
        self.gamma_m = gamma_m
        return
        
        
    def sett_styrke_parameter(self, phi, attraksjon=0, kohesjon=0, cu=0):
        '''
        Ipunt friksjonsvinkel til laget samt attraksjon og kohesjon
        Dersom ein av attraksjon eller kohesjon blir gitt blir andre rekna ut
        Returnerer tuouple med karekteristisk og dimmensjonerende styrkeparameter
        phi, tanphi, attraksjon, kohesjon
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
        
        self.ro = self.phi * self.gamma_m
        self.tanro = self.tanphi * self.gamma_m
        self.attraksjon_dim = self.attraksjon * self.gamma_m
        self.kohesjon_dim = self.kohesjon * self.gamma_m
        self.cu_dim = self.cu *self.gamma_m
        self.k0 = 1 - math.sin(math.radians(self.phi))
        return
    
    def sett_stivhet(self, m, M):
        self.m = m
        self.M = M
        return
    
       
    def passiv_jordtrykksfaktor(self, beta, r):
        '''
        Manglar implentasjon
        '''
        return
    

    
        

def ekvivalent_attraksjon(dm, l, sigma_m):
    '''
    Berekner ekvivalent attraksjon etter internrapport Eggestad i SVV
    internrapport 2242
    
    Parameter:
        dm: midlere korndiameter
        l: skjærflatas lengde
        sigma_m: effektiv normalspenning mot skjerflate
        
    Retur:
        Returnerer ekvivalent attraksjon i kPa
    '''
    
    return (250 * (dm/l) * (math.log10(sigma_m) + 10))


class geoLagPakke(object):
    '''
    Etablerer ein lagpakke av geolag for å plotte ut spenningsplot og utføre geotekniske berekningar
    
    Argument:
        lagliste: lag av geolag objekt instanser
        u: grunnvassnivå
    '''
    
    def __init__(self, lagliste, u):
        '''
        Initmetoden etablerer spenningsfordeling i lagpakken til vidare bruk i metoder
        '''
        
        self.lagliste = lagliste
        self.djupne = [0]
        self.pv = [0]
        self.pv_eff = [0]
        self.u_liste = [0]
        self.gamma = [0]
              
        
        for lag in self.lagliste:
            for i in range(lag.mektighet):
                if len(self.djupne) == 0:
                    self.djupne.append(1)
                else:
                    self.djupne.append(self.djupne[-1]+1)
        
        for lag in self.lagliste:
            for i in range(lag.mektighet):
                self.gamma.append(lag.gamma)
        
        for lag in self.lagliste:
            for i in range(lag.mektighet):
                self.pv.append(self.pv[-1] + lag.gamma)
        
        for i in self.djupne:
            if i < u:
                self.u_liste.append(0)
            else:
                self.u_liste.append(self.u_liste[-1]+10)
        del self.u_liste[-1] 
                
        self.lagdf = pd.DataFrame(self.djupne)
        self.lagdf.columns = ['Djupne']
        self.lagdf['Gamma'] = self.gamma
        self.lagdf['Pv'] = self.pv
        self.lagdf['U'] = self.u_liste
        self.lagdf["Pv'"] = self.lagdf['Pv'] - self.lagdf['U']
        

    def aktiv(self, beta=0, r=0):
        '''Rekner ut jordtrykkskoeffisient for laget
        
        Parameter:
            Beta: helling til terreng bak vegg/skråning
            delta: fronthelling
            r: ruhet vegg/jord
            
        Return:
            Gir tilbake aktiv jordtrykkskoeffisient
        
        TODO:
            KKORRIGERT HAR TRULEG FEIL FORMEL!!
        '''

        
        self.aktiv_trykk = [0]
        
        for lag in self.lagliste:
            s = ((math.tan(math.radians(beta)))/(lag.ro))
            t = ((1 + r) * (1 - s))
            ka = 1/(((math.sqrt(1 + (math.tan(lag.tanro)) ** 2)) + math.atan(lag.tanro) * math.sqrt(t)) ** 2)
            for i in range(lag.mektighet):
                self.aktiv_trykk.append(ka)
        #del self.aktiv_trykk[-1]             
        print('ka: ', self.aktiv_trykk)
        print(len(self.aktiv_trykk))
        self.lagdf['Ka'] = self.aktiv_trykk
        self.lagdf["Ph' (Ka)"] = self.lagdf["Pv'"] * self.lagdf['Ka']
        return self.aktiv_trykk

    def k0(self, beta=0, r=0):
        
        self.k0_spenning = [0]
        for lag in self.lagliste:
            for i in range(lag.mektighet):
                self.k0_spenning.append(lag.k0)        
        print('k0: ', self.k0_spenning)
        print(len(self.k0_spenning))
        self.lagdf['K0'] = self.k0_spenning
        self.lagdf["Ph' (K0)"] = self.lagdf["Pv'"] * self.lagdf['K0']
        return self.k0_spenning
        
    def spennings_plott(self):

        plt.figure(figsize=(5,8))
        plt.grid()
        plt.yticks(self.lagdf['Djupne'])
        plt.plot(self.lagdf['Pv'], self.lagdf['Djupne'], label='Totalspenning')
        plt.plot(self.lagdf["Pv'"], self.lagdf['Djupne'], label='Effektivspenning')
        plt.plot(self.lagdf['U'], self.lagdf['Djupne'], label='Poretrykk')
        
        plt.xlabel('Spenning (kPa)')
        plt.ylabel('Djupne (m)')
        plt.gca().invert_yaxis()
        plt.title("Spenningsplot")
        
        plt.legend()
    
        plt.show()
    
        return        

    def jordtrykks_plott(self):

        plt.figure(figsize=(5,8))
        plt.grid()
        plt.yticks(self.lagdf['Djupne'])
        #plt.plot(self.pv, self.djupne, label='Totalspenning')
        plt.plot(self.lagdf["Pv'"], self.lagdf['Djupne'], label='Effektivspenning')
        plt.plot(self.lagdf["U"], self.lagdf['Djupne'], label='U')
        #plt.plot(self.u_liste, self.djupne, label='Poretrykk')
        plt.plot(self.lagdf["Ph' (K0)"], self.lagdf['Djupne'], label="Ph' K0")
        plt.plot(self.lagdf["Ph' (Ka)"], self.lagdf['Djupne'], label="Ph' Ka")
        plt.xlabel('Spenning (kPa)')
        plt.ylabel('Djupne (m)')
        plt.gca().invert_yaxis()
        plt.title("Spenningsplot")
        
        plt.legend()
    
        plt.show()
    
        return               

    def jordtrykk(self, kfaktor=a):
        '''
        Gi inn jordtrykksfaktor som a = aktiv, 0 = k0 eller p som passiv
        Returnerer samla jordtrykk i kN 
        '''
        if kfaktor == a:
            for lag in self.lagliste:
                

leire = GeoLag('leire', 3, 18)
leire.sett_styrke_parameter(25, 3)
silt = GeoLag('silt', 5, 20)
silt.sett_styrke_parameter(32, 5)
morene = GeoLag('morene', 8, 19)
morene.sett_styrke_parameter(38, 10)

lagliste = [leire, silt, morene]

lagpakke = geoLagPakke(lagliste, 3)


lagpakke.spennings_plott()
print(lagpakke.k0())
print(lagpakke.aktiv())
print(lagpakke.lagdf)
lagpakke.jordtrykks_plott()