
import math
import numpy as np
import matplotlib.pyplot as plt
import geofunk

class SoneGeometri:
    def __init__(self, fundament, jordprofil, x_avsett_fund=0):
        self.b0 = fundament.b0
        self.botn_fundament = fundament.z
        self.tykkelse_fundament = fundament.fundament_tykkelse
        self.gamma_m = fundament.gamma_m
        self.tan_phi_lag1 = jordprofil.get_tan_phi_lag(0)
        self.phi_lag1 = jordprofil.get_phi_lag(0)
        self.x_avsett_fund = x_avsett_fund
        self.bunn_fundament_z = fundament.bunn_fundament
        self.rb = fundament.rb
        self.z_avsett = fundament.z

        self.ro = math.radians(self.phi_lag1) / self.gamma_m
        self.tan_omega = ((1-(math.sqrt(1-self.rb**2)))/self.rb)*((math.tan(math.radians(45 + (math.degrees(self.ro)/2)))))
        self.omega = math.atan(self.tan_omega)
        self.tan_alfa = math.tan(math.radians(45) + self.ro/2)
        self.beta1 = math.radians(45) + self.ro/2 - self.omega
        self.beta2 = math.radians(45) + self.ro/2 + self.omega
        self.beta3 = math.radians(90) - self.ro
        self.beta4 = math.radians(45) - self.ro/2
        self.theta = math.radians(90) - self.omega
        self.r1 = self.b0 * (math.sin(self.beta1))/(math.sin(self.beta3))
        self.r2 = self.r1 * math.exp(self.theta * math.tan(self.ro))

        #TODO: Implemptere justering for botn fundament, berre legge til z?
        self.r1_z = -abs(self.r1*math.sin(self.beta2))
        self.r1_x = -abs(self.r1*math.cos(self.beta2))
        self.r2_z = -abs(self.r2*math.sin(self.beta4))
        self.r2_x = abs(self.r2*math.cos(self.beta4))


    def tegn_aktiv_rankine(self, ax1=None):
        venstre_bunn_fund_x = -self.b0
        
        if ax1 is None:
            ax1 = plt.gca()
        ax1.plot([venstre_bunn_fund_x, self.r1_x], [self.bunn_fundament_z, self.r1_z], color="b")
        ax1.plot([self.x_avsett_fund, self.r1_x], [self.bunn_fundament_z, self.r1_z], color="b")
        return ax1

    def tegn_passive_rankine(self, ax1=None):
        if ax1 is None:
            ax1 = plt.gca()
 
        ytterpunkt_passive_rankine_x = 2 * self.r2_x
        ax1.plot([self.x_avsett_fund, self.r2_x], [self.bunn_fundament_z, self.r2_z], color="b")
        ax1.plot([ytterpunkt_passive_rankine_x, self.r2_x], [self.bunn_fundament_z, self.r2_z], color="b")
        return ax1

    def tegn_prandtl(self, ax1=None):
        if ax1 is None:
            ax1 = plt.gca()
        xliste = []
        yliste = []
        for i in range(0, int(math.degrees(self.theta))+1, 2):
            temp_stråle = geofunk.stråle_r2(self.r1, (self.theta - math.radians(i)), self.ro)
            temp_kordinater = geofunk.r2_punkt((self.beta4 + math.radians(i)), temp_stråle, self.bunn_fundament_z)
            xliste.append(temp_kordinater[0])
            yliste.append(temp_kordinater[1])

        ax1.plot(xliste, yliste, color="b")
        return ax1

    def tegn_sonegeometri(self, ax1=None):
        if ax1 is None:
            ax1 = plt.gca()

        ax1 = self.tegn_aktiv_rankine()
        ax1 = self.tegn_passive_rankine()
        ax1 = self.tegn_prandtl()

        return ax1