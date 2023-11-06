import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import geo.geofunk as geofunk
import math
import geo.grunn as grunn


def plot_nfakt(tan_ro, r, nq, ngamma):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=[6, 6])
    r_liste = [x / 100 for x in range(0, 100, 10)]
    tan_fi_d = [x / 100 for x in range(10, 100, 1)]
    ax1.scatter(tan_ro, nq, color="red")
    ax2.scatter(tan_ro, ngamma, color="red")
    for r_ in r_liste:
        nqliste = []
        ngammaliste = []
        for d in tan_fi_d:
            nq_i, ngamma_i = geofunk.n_fakt(d, r_)
            nqliste.append(nq_i)
            ngammaliste.append(ngamma_i)
        ax1.plot(tan_fi_d, nqliste, color="black")
        ax2.plot(tan_fi_d[0:-10], ngammaliste[0:-10], color="black")
        ax1.annotate(
            f"r={r_}", xy=(max(tan_fi_d) - 0.05, max(nqliste)), size=8, rotation=50
        )
        ax2.annotate(
            f"r={r_}",
            xy=((max(tan_fi_d[0:-10]) - 0.05), (max(ngammaliste[0:-10]))),
            size=8,
            rotation=50,
        )
    ax1.set_yscale("log")
    ax2.set_yscale("log")
    ax2.yaxis.set_major_formatter(
        ticker.FuncFormatter(
            lambda y, pos: (
                "{{:.{:1d}f}}".format(int(np.maximum(-np.log10(y), 0)))
            ).format(y)
        )
    )
    ax1.yaxis.set_major_formatter(
        ticker.FuncFormatter(
            lambda y, pos: (
                "{{:.{:1d}f}}".format(int(np.maximum(-np.log10(y), 0)))
            ).format(y)
        )
    )
    ax1.xaxis.grid()
    ax2.xaxis.grid()
    ax1.yaxis.grid()
    ax2.yaxis.grid()
    ax1.text(
        0.01,
        0.99,
        f"tan \u03C1={round(tan_ro,2)}\nr={round(r,1)}\nN$_{{{'q'}}}$={round(nq,1)}",
        ha="left",
        va="top",
        transform=ax1.transAxes,
    )
    gamma = "\u03B3"
    ax2.text(
        0.01,
        0.99,
        f"tan \u03C1={round(tan_ro,2)}\nr={round(r,1)}\nN$_{{{gamma}}}$={round(ngamma,1)}",
        ha="left",
        va="top",
        transform=ax2.transAxes,
    )
    ax1.set(xlabel="tan \u03C1", ylabel="N$_{q}$")
    ax2.set(xlabel="tan \u03C1", ylabel="N$_{\u03B3}$")
    fig.tight_layout()
    return fig


class SoneGeometri:
    def __init__(self, fundament, jordprofil):
        self.b0 = fundament.b0
        self.botn_fundament = fundament.z
        self.tykkelse_fundament = fundament.fundament_tykkelse
        self.gamma_m = fundament.gamma_m
        self.tan_phi_lag1 = jordprofil.get_tan_phi_lag(0)
        self.phi_lag1 = jordprofil.get_phi_lag(0)
        self.x_avsett_fund = fundament.x_avsett_fund
        self.bunn_fundament_z = fundament.bunn_fundament
        self.rb = fundament.rb

        self.ro = math.radians(self.phi_lag1) / self.gamma_m
        if self.rb == 0.0:
            self.rb = 0.0001
        self.tan_omega = ((1 - (math.sqrt(1 - self.rb**2))) / self.rb) * (
            (math.tan(math.radians(45 + (math.degrees(self.ro) / 2))))
        )
        self.omega = math.atan(self.tan_omega)
        self.tan_alfa = math.tan(math.radians(45) + self.ro / 2)
        self.beta1 = math.radians(45) + self.ro / 2 - self.omega
        self.beta2 = math.radians(45) + self.ro / 2 + self.omega
        self.beta3 = math.radians(90) - self.ro
        self.beta4 = math.radians(45) - self.ro / 2
        self.theta = math.radians(90) - self.omega
        self.r1 = self.b0 * (math.sin(self.beta1)) / (math.sin(self.beta3))
        self.r2 = self.r1 * math.exp(self.theta * math.tan(self.ro))

        # TODO: Implemptere justering for botn fundament, berre legge til z?
        self.r1_z = -abs(self.r1 * math.sin(self.beta2)) + self.bunn_fundament_z
        self.r1_x = -abs(self.r1 * math.cos(self.beta2))
        self.r2_z = -abs(self.r2 * math.sin(self.beta4)) + self.bunn_fundament_z
        self.r2_x = abs(self.r2 * math.cos(self.beta4))

    def tegn_aktiv_rankine(self, ax1=None):
        venstre_bunn_fund_x = -self.b0

        if ax1 is None:
            ax1 = plt.gca()
        ax1.plot(
            [venstre_bunn_fund_x, self.r1_x],
            [self.bunn_fundament_z, self.r1_z],
            color="b",
        )
        ax1.plot(
            [self.x_avsett_fund, self.r1_x],
            [self.bunn_fundament_z, self.r1_z],
            color="b",
        )
        ax1.plot(
            [venstre_bunn_fund_x, self.x_avsett_fund],
            [self.bunn_fundament_z, self.bunn_fundament_z],
            color="b",
        )
        ax1.set_aspect('equal')
        return ax1

    def tegn_passive_rankine(self, ax1=None):
        if ax1 is None:
            ax1 = plt.gca()

        ytterpunkt_passive_rankine_x = 2 * self.r2_x
        ax1.plot(
            [self.x_avsett_fund, self.r2_x],
            [self.bunn_fundament_z, self.r2_z],
            color="b",
        )
        ax1.plot(
            [ytterpunkt_passive_rankine_x, self.r2_x],
            [self.bunn_fundament_z, self.r2_z],
            color="b",
        )
        ax1.plot(
            [self.x_avsett_fund, ytterpunkt_passive_rankine_x],
            [self.bunn_fundament_z, self.bunn_fundament_z],
            color="b",
        )
        ax1.set_aspect('equal')
        return ax1

    def tegn_prandtl(self, ax1=None):
        if ax1 is None:
            ax1 = plt.gca()
        xliste = []
        yliste = []
        for i in range(0, int(math.degrees(self.theta)) + 1, 2):
            temp_stråle = geofunk.stråle_r2(
                self.r1, (self.theta - math.radians(i)), self.ro
            )
            temp_kordinater = geofunk.r2_punkt(
                (self.beta4 + math.radians(i)), temp_stråle, self.bunn_fundament_z
            )
            xliste.append(temp_kordinater[0])
            yliste.append(temp_kordinater[1])

        ax1.plot(xliste, yliste, color="b")
        ax1.set_aspect('equal')
        return ax1

    def tegn_sonegeometri(self, ax1=None):
        if ax1 is None:
            ax1 = plt.gca()

        ax1 = self.tegn_aktiv_rankine()
        ax1 = self.tegn_passive_rankine()
        ax1 = self.tegn_prandtl()
        ax1.set_aspect('equal')
        return ax1


def tegn_fundament_terreng(fundament, helling, terrenghoyde=0, ax1=None):
    """
    Tegner opp terreng ved bæreevneberening

    Krøkkete metode
    #TODO: Bør fikses opp
    """

    if ax1 is None:
        ax1 = plt.gca()

    x_punkter = []
    z_punkter = [terrenghoyde, terrenghoyde]

    fundamentpunkt_x_mot_helling = fundament.x_avsett_fund
    start_terreng_x = -abs(fundament.x_avsett_fund - 1.5 * fundament.b)
    slutt_terreng_x = abs(
        (fundament.x_avsett_fund + 4 * fundament.b)
    )  # bunn av bakke dersom helling
    bunn_terreng_z = -abs(-abs((fundament.x_avsett_fund - (fundament.b0/2) + 5 * fundament.b) * helling))
    x_punkter.append(start_terreng_x)
    x_punkter.append(fundamentpunkt_x_mot_helling)
    x_punkter.append(slutt_terreng_x + (fundament.b0/2))
    z_punkter.append(bunn_terreng_z)
    ax1.plot(x_punkter, z_punkter)
    ax1.set_aspect('equal')
    return ax1

def plot_samla(fundament, jordprofil, terrenghelling):
    fig, ax1 = plt.subplots(figsize=[8,8])
    sonegeo = SoneGeometri(fundament,jordprofil)
    ax1 = fundament.tegn_fundament()
    ax1 = sonegeo.tegn_sonegeometri()
    ax1 = tegn_fundament_terreng(fundament, terrenghelling)
    #ax1.set_ylim(-abs(sonegeo.r2_z +sonegeo.r2_z*0.7), abs(sonegeo.r1_z))
    ax1.set_xlabel('Lengde langs snitt (m)')
    ax1.set_ylabel('Dybde (m)')
    ax1.grid()
    ax1.set_aspect('equal')
    return fig

def finn_solebredde(z, fv_fund, fh, gamma_m, terrenghelling, jordprofil, plot):
    fundamenter = []
    
    qv = []
    
    sigma = []
    
    saalebredde = np.arange(0.01, 20, 0.01)
    for i in saalebredde:
        fund = grunn.Fundament(i, z, fv_fund, fh, gamma_m, jordprofil)
        fund.sett_delta_fv()
        fund.sigma_v(terrenghelling)
        fundamenter.append(fund)
        qv.append(fund.qv)
        sigma.append(fund.sigma_v_)
    
    print(f'qv={qv}')
    #print(f'fundamenter={fundamenter}')
    print(f'sigma={sigma}')    
    qv_arr = np.array(qv)
    sigma_arr = np.array(sigma)
    idx = np.argwhere(np.diff(np.sign(qv_arr - sigma_arr))).flatten()
    print(f'idx={idx}')
    qv_norm = round(qv[idx[0]], 0)
    b0_min = round(saalebredde[idx[0]],1)
    if plot:
        fig, ax1 = plt.subplots(figsize=[8,4])
        ax1.plot(saalebredde, qv, label='q$_{v}$')
        ax1.plot(saalebredde, sigma, label='\u03C3$_{v}$')
        ax1.plot(saalebredde[idx[0]], qv[idx[0]], 'ro')
        ax1.set_ylim(0, qv_norm*3)
        ax1.set_xlim(0, b0_min*2)
        ax1.set_xlabel('Sålebredde (m)')
        ax1.set_ylabel('Spenning (kPa)')
        ax1.grid()
        ax1.legend()
        ax1.annotate(f'B$_{{{0}}} = {b0_min}$m', xy=(saalebredde[idx[0]], qv[idx[0]]), xycoords='data', xytext=(saalebredde[idx[0]]*1.1, qv[idx[0]]*1.5), arrowprops=dict(arrowstyle="->"))
        return b0_min, fig
    else: 
        return b0_min