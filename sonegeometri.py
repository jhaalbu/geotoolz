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
    
    f_omega = (1-(math.sqrt(1-r**2)))
    print(f'f_omega:{f_omega}')
    omega = math.atan(f_omega)
    print(f'omega:{omega}')
    tan_alfa = math.tan(math.radians(45) + ro/2)
    print(f'tan_alfa:{tan_alfa}')
    tan_omega = f_omega * tan_alfa
    print(f'tan_omega:{tan_omega}')
    beta1 = math.radians(45) + ro/2 - omega
    print(f'beta1:{beta1}')
    beta2 = math.radians(45) + ro/2 + omega
    print(f'beta2:{beta2}')
    beta3 = math.radians(90) - ro
    print(f'beta3:{beta3}')
    beta4 = math.radians(45) - ro/2
    print(f'beta4:{beta4}')
    phi = math.radians(90) - omega
    print(f'phi:{phi}')
    r1 = b0 * (math.sin(beta1)/math.sin(beta2))
    print(f'r1:{r1}')
    r2 = r1 * math.exp(phi * math.tan(ro))
    print(f'r2:{r2}')

    return beta1, beta2, beta3, beta4, phi, r1, r2

geometri = sonegeometri(b0, qv, qh, ro, r)
print(geometri)

for i in geometri:
    print(math.degrees(i))
