
import math
import numpy as np
import matplotlib.pyplot as plt

class SoneGeometri:
    def __init__(self, fundament, jordprofil, poisjon_fundament=(0,0)):
        self.b0 = fundament.b0
        self.botn_fundament = fundament.z
        self.tykkelse_fundament = fundament.tykkelse
        self.gamma_m = fundament.gamma_m
        self.tan_phi_lag1 = jordprofil.get_tan_phi_lag(0)
        self.phi_lag1 = jordprofil.get_phi_lag(0)

        self.ro = math.radians(self.phi_lag1)
        self.tan_omega = ((1-(math.sqrt(1-r**2)))/r)*((math.tan(math.radians(45 + (math.degrees(ro)/2)))))
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
        r1_z = -abs(self.r1*math.sin(self.beta2))
        r1_x = -abs(self.r1*math.cos(self.beta2))
        r2_z = -abs(self.r2*math.sin(self.beta4))
        r2_x = abs(self.r2*math.cos(self.beta4))

    def tegn_fundament(self, b0, tykkelse_fundament, botn_fundament=0, ax1=None):
        '''
        Tegner opp fundament
        '''
        botn_fundament
        b0_negativ = -abs(b0)
        if ax1 is None:
            ax1 = plt.gca()
        ax1.plot([0,b0_negativ,b0_negativ,0,0], [tykkelse_fundament,tykkelse_fundament,0,0, tykkelse_fundament])
        return ax1



    def tegn_aktiv_rankine(b0, r1, beta2, bunn_fund_z=0, høgre_bunn_fund_x=0,ax1=None):
        r_1 = r1_punkt(beta2, r1)
        venstre_bunn_fund_x = -b0
        
        if ax1 is None:
            ax1 = plt.gca()
        ax1.plot([venstre_bunn_fund_x, r_1[0]], [bunn_fund_z, r_1[1]], color="b")
        ax1.plot([høgre_bunn_fund_x, r_1[0]], [bunn_fund_z, r_1[1]], color="b")
        return ax1

    def tegn_passive_rankine(b0, beta4, r2, bunn_fund_z=0, høgre_bunn_fund_x=0, ax1=None):
        if ax1 is None:
            ax1 = plt.gca()
        r_2 = r2_punkt(beta4, r2)
        ytterpunkt_passive_rankine_x = 2 * r_2[0]
        ax1.plot([høgre_bunn_fund_x, r_2[0]], [bunn_fund_z, r_2[1]], color="b")
        ax1.plot([ytterpunkt_passive_rankine_x, r_2[0]], [bunn_fund_z, r_2[1]], color="b")
        return ax1

    def tegn_prandtl(r1, theta, beta4, ro, ax1=None):
        if ax1 is None:
            ax1 = plt.gca()
        xliste = []
        yliste = []
        for i in range(0, int(math.degrees(theta))+1, 2):
            temp_stråle = stråle_r2(r1, (theta - math.radians(i)), ro)
            temp_kordinater = r2_punkt((beta4 + math.radians(i)), temp_stråle)
            xliste.append(temp_kordinater[0])
            yliste.append(temp_kordinater[1])

        ax1.plot(xliste, yliste, color="b")
        return ax1

    def tegn_sonegeometri(b0, qv, qh, ro, r, ax1=None):
        geometri = sonegeometri(b0, qv, qh, ro, r)
        beta1, beta2, beta3, beta4, theta, r1, r2 = geometri
        if ax1 is None:
            ax1 = plt.gca()

        ax1 = tegn_aktiv_rankine(b0, r1, beta2, bunn_fund_z=0, høgre_bunn_fund_x=0,ax1=None)
        ax1 = tegn_passive_rankine(b0, beta4, r2, bunn_fund_z=0, høgre_bunn_fund_x=0, ax1=None)
        ax1 = tegn_prandtl(r1,theta, beta4, ro)

        return ax1