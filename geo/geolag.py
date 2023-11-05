# -*- coding: utf-8 -*-
"""
Created on Sat Nov  2 20:12:29 2019

@author: jhaal
"""

import math
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np 
import geo.geofunk

class GeoLag(object):
    def __init__(self, jordart, ztopp, zbunn, gamma=18):
        self.jordart = jordart
        #self.mektighet = mektighet
        self.ztopp = ztopp #cm
        self.zbunn = zbunn #cm
        self.gamma = gamma
        self.mektighet = zbunn - ztopp #cm
        print(self.mektighet)
        self.gamma_m = 1

    def __repr__(self):
        return "Jordlag fra GeoLag objekt"

    def __str__(self):
       return f'Jordart: {str(self.jordart)} , Mektighet: {str(self.mektighet)} cm, '
       
    #    ('''\
    #    Jordart: %s 
    #    Lagmektighet: %s
    #    Tyngdetetthet: %s 
    #    -------------------------\
    #    ''' % (str(self.jordart), str(self.mektighet), str(self.gamma)))
        
    
    def sett_gamma_m(self, gamma_m):
        self.gamma_m = gamma_m
        return
        
        
    def sett_styrke_parameter(self, phi, attraksjon=0, kohesjon=0, cu=0, r=0, beta=0):
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
        self.k0 = geofunk.jordtrykksfaktor_k0(self.ro)
        self.ka = geofunk.jordtrykksfaktor_ka(self.ro)
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
        
        Parameter:
        Tar inn ei liste av geolaginstanser, grunnvannsnivå samt metode kan velges til å
        vere enten 1 som gir jevn graf uten sprang ved lagskifte, eller hakkete graf der det er sprang runt lagskifte
        TODO: Implementere mulighet for å gi z verdier eller mektighet for lagpakke
        '''
        self.lagliste = lagliste
        self.u = u

        #Finner total lagpakketjukkelse
        lagpakke = 0
        for lag in self.lagliste:
            lagpakke += lag.mektighet

        self.lagdf = pd.DataFrame({'Djupne' : range(lagpakke)})
        self.lagdf['Meter'] = self.lagdf['Djupne']/100
        self.lagdf['U'] = 0
        #Velger ut del av dataframe som er under grunnvannstand
        self.lagdf['U'].loc[self.lagdf['Meter'] > self.u] = self.lagdf['Meter'] * 10 - self.u *10
        self.lagdf['Pv'] = 0
        self.lagdf['Gamma'] = 0
        for lag in self.lagliste:
            print(lag)
            print(lag.gamma)
            self.lagdf['Gamma'].loc[((self.lagdf['Djupne'] >= lag.ztopp) & (self.lagdf['Djupne'] <= lag.zbunn))] = lag.gamma
        self.lagdf['Vekt'] = self.lagdf['Gamma'] * 0.01
        self.lagdf['Pv'] = self.lagdf.Vekt.cumsum()
        self.lagdf["Pv'"] = self.lagdf['Pv'] - self.lagdf['U']
        #print(self.lagdf)

        

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
        
        self.lagdf['Ka'] = 0
        for lag in self.lagliste:
            self.lagdf['Ka'].loc[((self.lagdf['Djupne'] >= lag.ztopp) & (self.lagdf['Djupne'] <= lag.zbunn))] = lag.ka
   
        self.lagdf["Ph' (Ka)"] = self.lagdf["Pv'"] * self.lagdf['Ka']
        return 'Ka utført'

    def k0(self, beta=0, r=0):
        print(self.lagdf)
        self.lagdf['K0'] = 0
        print(self.lagdf)
        for lag in self.lagliste:
            self.lagdf['K0'].loc[((self.lagdf['Djupne'] >= lag.ztopp) & (self.lagdf['Djupne'] <= lag.zbunn))] = lag.k0
        #print(len(self.k0_spenning))
        self.lagdf["Ph' (K0)"] = self.lagdf["Pv'"] * self.lagdf['K0']
        print(self.lagdf)
        return 'K0 utført'
        
    def spennings_plott(self):

        plt.figure(figsize=(5,8))
        plt.grid()
        plt.yticks(range(1, int(len(self.lagdf)/100)+1))
        plt.plot(self.lagdf['Pv'], self.lagdf['Meter'], label='Totalspenning')
        plt.plot(self.lagdf["Pv'"], self.lagdf['Meter'], label='Effektivspenning')
        plt.plot(self.lagdf['U'], self.lagdf['Meter'], label='Poretrykk')
        
        plt.xlabel('Spenning (kPa)')
        plt.ylabel('Meter (m)')
        plt.gca().invert_yaxis()
        plt.title("Spenningsplot")
        
        plt.legend()
    
        plt.show()
    
        return        

    def jordtrykks_plott(self):

        plt.figure(figsize=(5,8))
        plt.grid()
        plt.yticks(range(1, int(len(self.lagdf)/100)))
        #plt.plot(self.pv, self.djupne, label='Totalspenning')
        plt.plot(self.lagdf["Pv'"], self.lagdf['Meter'], label='Effektivspenning')
        plt.plot(self.lagdf["U"], self.lagdf['Meter'], label='U')
        #plt.plot(self.u_liste, self.djupne, label='Poretrykk')
        plt.plot(self.lagdf["Ph' (K0)"], self.lagdf['Meter'], label="Ph' K0")
        plt.plot(self.lagdf["Ph' (Ka)"], self.lagdf['Meter'], label="Ph' Ka")
        plt.xlabel('Spenning (kPa)')
        plt.ylabel('Djupne (m)')
        plt.gca().invert_yaxis()
        plt.title("Spenningsplot")
        
        plt.legend()
    
        plt.show()
    
        return               

    # def jordtrykk(self, kfaktor=a):
    #     '''
    #     Gi inn jordtrykksfaktor som a = aktiv, 0 = k0 eller p som passiv
    #     Returnerer samla jordtrykk i kN 
    #     '''
    #     if kfaktor == a:
    #         for lag in self.lagliste:
                

# leire = GeoLag('leire', 0, 300, 15)
# leire.sett_styrke_parameter(25, 3)
# silt = GeoLag('silt', 300, 800, 25)
# silt.sett_styrke_parameter(32, 5)
# morene = GeoLag('morene', 800, 1500, 40)
# morene.sett_styrke_parameter(38, 10)


