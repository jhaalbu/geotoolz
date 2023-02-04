import math
import matplotlib.pyplot as plt
'''
Metode fra kap 7.2.4 i NTNU kompendie 
Geoteknikk Beregningsmetoder - TBA4105
2016
kap 7.2.4
'''
def tegn_fundament(b0, tykkelse_fundament, botn_fundament=0, ax1=None):
    '''
    Tegner opp fundament
    '''
    botn_fundament
    b0_negativ = -abs(b0)
    if ax1 is None:
        ax1 = plt.gca()
    ax1.plot([0,b0_negativ,b0_negativ,0,0], [tykkelse_fundament,tykkelse_fundament,0,0, tykkelse_fundament])
    return ax1


def sonegeometri(b0, qv, qh, ro, r):
    tan_omega = ((1-(math.sqrt(1-r**2)))/r)*((math.tan(math.radians(45 + (math.degrees(ro)/2)))))
    omega = math.atan(tan_omega)
    tan_alfa = math.tan(math.radians(45) + ro/2)
    beta1 = math.radians(45) + ro/2 - omega
    beta2 = math.radians(45) + ro/2 + omega
    beta3 = math.radians(90) - ro
    beta4 = math.radians(45) - ro/2
    theta = math.radians(90) - omega
    r1 = stråle_r1(b0, beta1, beta3)
    r2 = stråle_r2(r1, theta, ro)
    return beta1, beta2, beta3, beta4, theta, r1, r2

def stråle_r1(b0, beta1, beta3):
    return b0 * (math.sin(beta1))/(math.sin(beta3))

def stråle_r2(r1, theta, ro):
    return r1 * math.exp(theta * math.tan(ro))

def r1_punkt(beta2, r1, botn_fundament=0):
    '''
    TODO: Justering for fundament anna enn y=0
    '''
    # if beta2 > math.radians(90):
    #     beta2 = beta2 - math.radians(90) 
    z = r1*math.sin(beta2)
    x = r1*math.cos(beta2)
    
    return -x,-z

def r2_punkt(beta4, r2, botn_fundament=0):
    '''
    TODO: Kva med fundament anna enn y=0
    '''
    z = r2*math.sin(beta4)
    x = r2*math.cos(beta4)
    return x,-z

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

 

# for i in geometri:
#     print(math.degrees(i))
def main(b):
    b0 = 1
    qv = 500 
    qh = 200
    tan_ro = 0.577
    ro = math.atan(tan_ro)
    r = 0.2

    # geometri = sonegeometri(b0, qv, qh, ro, r)
    # beta1, beta2, beta3, beta4, theta, r1, r2 = geometri

    # fig, ax1 = plt.subplots()

    # ax1 = tegn_aktiv_rankine(b0, r1, beta2)
    # ax1 = tegn_passive_rankine(b0, beta4, r2)
    # ax1 = tegn_prandtl(r1,theta, beta4, ro)

    ax1 = tegn_sonegeometri(b0, qv, qh, ro, r, ax1=None)

    plt.show()

if  __name__ == "__main__":
    main()