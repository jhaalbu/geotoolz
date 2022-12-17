import math
'''
Metode fra kap 7.2.4 i NTNU kompendie 
Geoteknikk Beregningsmetoder - TBA4105
2016
kap 7.2.4
'''

b0 = 1
qv = 500
qh = 200
tan_ro = 0.577
ro = math.atan(tan_ro)
r = 0.5

def sonegeometri(b0, qv, qh, ro, r):
    tan_omega = ((1-(math.sqrt(1-r**2)))/r)*((math.tan(math.radians(45 + (math.degrees(ro)/2)))))
    omega = math.atan(tan_omega)
    tan_alfa = math.tan(math.radians(45) + ro/2)
    beta1 = math.radians(45) + ro/2 - omega
    beta2 = math.radians(45) + ro/2 + omega
    beta3 = math.radians(90) - ro
    beta4 = math.radians(45) - ro/2
    theta = math.radians(90) - omega
    r1 = b0 * (math.sin(beta1))/(math.sin(beta3))
    r2 = r1 * math.exp(theta * math.tan(ro))

    return beta1, beta2, beta3, beta4, theta, r1, r2

geometri = sonegeometri(b0, qv, qh, ro, r)

def tegn_fundament(b0, )

for i in geometri:
    print(math.degrees(i))
