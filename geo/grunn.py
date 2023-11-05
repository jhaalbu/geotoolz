import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import geo.geofunk as geofunk


class JordLag(object):
    def __init__(
        self,
        lagnavn,
        mektighet_cm=None,
        gamma=None,
        startdybde_cm=None,
        sluttdybde_cm=None,
    ) -> None:
        """
        Etablerer eit jordlag

        Perameters
        ----------
        lagnavn
        """
        self.lagnavn = lagnavn
        self.startdybde_cm = startdybde_cm
        self.sluttdybde_cm = sluttdybde_cm
        self.gamma = gamma
        if self.startdybde_cm == None:
            self.mektighet_cm = mektighet_cm
        else:
            self.mektighet_cm = self.sluttdybde_cm - self.startdybde_cm
        self.df = pd.DataFrame({"lagdjupne": range(0, (self.mektighet_cm) + 1)})
        self.df["lagnavn"] = self.lagnavn
        self.df["gamma"] = self.gamma / 100

    def __str__(self) -> str:
        return f"{self.lagnavn}, Mektighet: {self.mektighet_cm}"

    def sett_styrke_parameter(
        self, phi_grader=0, tanphi=0, attraksjon=0, kohesjon=0, cu=0
    )-> None:
        """
        Setter styrkeparametere for laget.

        Parameters
        ----------
        phi_grader : float
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

        """
        self.phi_grader = phi_grader
        self.tanphi = tanphi
        if self.phi_grader == 0:
            self.phi_grader = round(math.degrees(math.atan(self.tanphi)))
        if self.tanphi == 0:
            self.tanphi = round(math.tan(math.radians(self.phi_grader)), 2)
        # self.phi_grader = phi_grader
        print(f'phi_grader: {self.phi_grader}, tanphi: {self.tanphi}')
        self.attraksjon = attraksjon
        self.kohesjon = kohesjon
        self.cu = cu

        if kohesjon == 0 and attraksjon != 0:
            self.kohesjon = attraksjon * self.tanphi
        if attraksjon == 0 and kohesjon != 0:
            self.attraksjon = kohesjon / self.tanphi

        self.df["phi_grader"] = self.phi_grader
        self.df["tanphi"] = self.tanphi
        self.df["attraksjon"] = self.attraksjon
        return

    def sett_stivhet(self, m=0, M=0):
        """
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

        """
        self.m = m
        self.M = M
        if self.m == 0 and self.M != 0:
            self.df["M"] = self.M
            return
        elif self.M == 0 and self.m != 0:
            self.df["m"] = self.m
            return
        else:
            return

    def primerkonsolidering_tid(self, cv):
        """

        Parameters
        ----------
        cv : float
            konsolideringskoeffisient (m^2/år)

        Returns
        -------
        tp: float
            tiden for 95% konsolidering (år).

        """
        h = (self.mektighet_cm / 2) / 100
        self.tp = h**2 / cv
        return self.tp


# TODO: I jordprofilklassen er det ein bug som gjer at det blir ein cm ekstra per lag
#       Antar denne buggen kjem fra at alle lag startar med 0 cm, ein ekstra cm her
#TODO: Ta ut setning fra jordprofil, eit ting om gangen?
#TODO: Men setning kan returnere eit profilobjekt med setninger rekna ut?
class JordProfil:
    def __init__(self, jordarter, u=1.0) -> None:
        self.jordarter = jordarter
        self.u = u
        self.df = pd.concat(
            [jordlag.df for jordlag in self.jordarter],
            keys=[jordlag.lagnavn for jordlag in self.jordarter],
        )
        self.df["djupne"] = range(0, len(self.df))
        self.df["djupne_meter"] = self.df["djupne"] / 100
        self.df = self.df.set_index("djupne")
        self.df["u"] = 0
        self.df.loc[self.df["djupne_meter"] > self.u, "u"] = (
            self.df["djupne_meter"] * 10 - self.u * 10
        )
        self.df["sigma_v0"] = (
            self.df["gamma"].cumsum().shift(1, fill_value=0) - self.df["u"]
        )
        self.df["fill"] = 0
        # print(self.df)

    def __str__(self):
        jordlagbeskrivelse = f"Lag i Jordprofilet\n"
        for lag in self.jordarter:
            jordlagbeskrivelse += f"Lag med navn: {lag.lagnavn} med mektihget: {lag.mektighet_cm/100} m\n Parametere:  \n phi_grader={lag.phi_grader}, tanphi={lag.tanphi}, attraksjon={lag.attraksjon}, kohesjon={lag.kohesjon}, cu={lag.cu} \n"

        return jordlagbeskrivelse

    def get_tan_phi_lag(self, lagnavn="", lagnr=0):
        if not lagnavn:
            return self.jordarter[lagnr].tanphi
        if lagnr == 0:
            for lag in self.jordarter:
                if lag.lagnavn == lagnavn:
                    return lag.tanphi

    def get_phi_lag(self, lagnavn="", lagnr=0):
        if not lagnavn:
            return self.jordarter[lagnr].phi_grader
        if lagnr == 0:
            for lag in self.jordarter:
                if lag.lagnavn == lagnavn:
                    return lag.phi_grader

    def get_gamma_lag(self, lagnavn="", lagnr=0):
        if not lagnavn:
            return self.jordarter[lagnr].gamma
        if lagnr == 0:
            for lag in self.jordarter:
                if lag.lagnavn == lagnavn:
                    return lag.gamma

    def get_attraksjon_lag(self, lagnavn="", lagnr=0):
        if not lagnavn:
            return self.jordarter[lagnr].attraksjon
        if lagnr == 0:
            for lag in self.jordarter:
                if lag.lagnavn == lagnavn:
                    return lag.attraksjon

    def plot_jordprofil(self, ax1=None):
        if ax1 is None:
            ax1 = plt.gca()
        ax1.plot()

    def setning_uendelig(self, q):
        self.df["delta_p"] = q
        self.df = self.df.assign(
            toyning=lambda x: (1 / x.m) * np.log((x.sigma_v0 + q) / x.sigma_v0)
        )
        self.df = self.df.replace([np.inf, -np.inf], 0)
        self.df["delta_sigma"] = self.df["toyning"] * 0.01
        self.df["sigma"] = self.df["delta_p"] + self.df["sigma_v0"]
        self.df["toyning_prosent"] = self.df["toyning"] * 100
        return

    def setning_endelig(self, q, b, l):
        z0 = np.pi * ((b * l) / (b + l))
        self.df["delta_p"] = q * (1 - (self.df.index / z0))
        self.df.loc[self.df["delta_p"] < 0, "delta_p"] = 0
        self.df = self.df.assign(
            toyning=lambda x: (1 / x.m) * np.log((x.sigma_v0 + x.delta_p) / x.sigma_v0)
        )
        self.df = self.df.replace([np.inf, -np.inf], 0)
        self.df["toyning_prosent"] = self.df["toyning"] * 100
        self.df["delta_sigma"] = self.df["toyning"] * 0.01
        self.df["sigma"] = self.df["delta_p"] + self.df["sigma_v0"]
        return

    def total_setning(self):
        return round(self.df["delta_sigma"].sum(), 3)

    def plot_toyning(self, ax1=None):
        if ax1 is None:
            ax1 = plt.gca()

        ax1.plot(self.df.sigma_v0, self.df.index, color="r", label="\u03C3\u2080'")
        ax1.plot(self.df.delta_p, self.df.index, color="g", label="\u0394\u03C3")
        ax1.plot(self.df.sigma, self.df.index, color="cyan", label="\u03C3")
        ax1.legend()
        ax1.invert_yaxis()
        ax2 = ax1.twiny()
        # ax2.plot(self.df.fill, self.df.index)
        ax2.plot(self.df.toyning_prosent[1:], self.df.index[1:], label="\u03B5")
        # ax2.fill_between(self.df.toyning_prosent[1:], self.df['fill'], step="pre", alpha=0.4)
        ax2.legend()
        ax2.set_xlim(0, self.df.toyning_prosent.max())
        ax1.set_ylabel("Djupne (cm)")
        ax2.set_xlabel("Tøyning (%)")
        ax1.set_xlabel("Spenning (kPa)")

        return ax1, ax2


class Fundament(object):
    def __init__(
        self,
        b,
        z,
        fv,
        fh,
        gamma_m,
        jordprofil,
        x_avsett=0,
        fundament_tykkelse=0.2,
        m=None,
    ):
        self.b = b
        self.z = z
        self.fv = fv
        self.fh = fh
        self.m = m
        self.gamma_m = gamma_m
        self.fundament_tykkelse = fundament_tykkelse
        self.jordprofil = jordprofil
        self.gamma = jordprofil.get_gamma_lag(lagnr=0)
        self.tan_fi_d = jordprofil.get_tan_phi_lag(lagnr=0) / self.gamma_m
        self.u = jordprofil.u
        self.attraksjon = jordprofil.get_attraksjon_lag(lagnr=0)
        self.x_avsett_fund = x_avsett

        # TODO: Antar førebels at grunnvasstand er rett under fundament
        self.gamma_eff = self.gamma - 10

        if m == None or m == 0:
            self.b0 = self.b
        else:
            self.b0 = self.b - (2 * (self.m / self.fv))

        self.bunn_fundament = -abs(z)
        self.qv = self.fv / self.b0
        self.tau = self.fh / self.b0

    def sett_delta_fv(self):
        self.delta_fv = (self.gamma * self.z * self.b0) / self.b0
        self.qv = self.qv + self.delta_fv
        return self.qv

    def sett_rb(self):
        self.rb = self.tau / ((self.qv + self.attraksjon) * self.tan_fi_d)
        return self.rb

    def nq_ngamma_faktor(self):
        self.nq, self.n_gamma = geofunk.n_fakt(self.tan_fi_d, self.rb)
        return self.nq, self.n_gamma
    
    def nc_faktor(self):
        self.nc = geofunk.nc_fakt(self.tan_fi_d, self.rb)
        return self.nc

    def reduksjonsfaktor_v220(self, terrenghelling):
        self.fsq = (1-(0.55*terrenghelling))**5
        self.fsa = math.e**(-2*math.tan(terrenghelling)*self.tan_fi_d)
        return self.fsa, self.fsq

    # def reduksjonsfaktor_v220(self, terrenghelling):
    #     self.terrenghelling = terrenghelling
    #     # self.fsa, self.fsq = geofunk.reduksjonsfaktor_v220(self.helling_forhold, self.tan_fi_d)
    #     self.fsa = 0.73
    #     self.fsq = 0.36
    #     return self.fsa, self.fsq

    #TODO: Må finne gamma under fundament, ta inn geolag for å gjere dette?? Rekne ut på nytt, og for neste lag dersom sonegeometri går ned i lag?

    def sigma_v(self, terrenghelling):
        self.sett_rb()
        self.nq_ngamma_faktor()
        self.reduksjonsfaktor_v220(terrenghelling)
        self.p_merka = self.gamma * self.z
        self.sigma_v_ = (
            self.fsq
            * (
                (self.nq * self.p_merka)
                + (0.5 * self.n_gamma * self.gamma_eff * self.b0)
            )
        ) + (((self.nq * self.fsa) - 1) * self.attraksjon)
        return round(self.sigma_v_, 1)

    def tegn_fundament(self, ax1=None):
        """
        Tegner opp fundament
        """

        dx = self.rb  # Since rb varies between 0 and 1, it can represent the horizontal component directly
        dy = -np.sqrt(1 - self.rb**2)  # The vertical component based on Pythagorean theorem
        arrow_length = self.b0
        arrow_start = (self.x_avsett_fund-(self.b0/2)-(dx*self.b0), (self.bunn_fundament+self.fundament_tykkelse*2)+abs(dy)*arrow_length*1.05)


        b0_negativ = -abs(self.b)
        if ax1 is None:
            ax1 = plt.gca()
        ax1.plot(
            [0, b0_negativ, b0_negativ, 0, 0],
            [
                self.bunn_fundament + self.fundament_tykkelse,
                self.bunn_fundament + self.fundament_tykkelse,
                self.bunn_fundament,
                self.bunn_fundament,
                self.bunn_fundament + self.fundament_tykkelse,
            ],
        )
        ax1.arrow(arrow_start[0], arrow_start[1], dx * arrow_length, dy * arrow_length, head_width=arrow_length*0.05, head_length=arrow_length*0.1, fc='blue', ec='blue')
        ax1.set_aspect('equal')

        return ax1
