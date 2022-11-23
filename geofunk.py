import math



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

def jordtrykksfaktor_ka(friksjonsvinkel, beta=0, r=0):
    '''
    Berekner aktiv jordstrykksfaktor
    
    Parameter:
        friksjonsvikel: friksjonsvinkel, bør kunne støtte både tangens til friksjonsvnikel og grader
        beta: helling bak skråning
        r: ruhet? TODO: Må sjekkes!
        
    Retur:
        Jordtrykksfaktor
    '''
    if friksjonsvinkel > 1:
        ro = friksjonsvinkel
        tanro = math.tan(math.radians(friksjonsvinkel))
    if friksjonsvinkel <= 1:
        tanro = friksjonsvinkel
        ro = math.degrees(math.atan(friksjonsvinkel))
    s = ((math.tan(math.radians(beta)))/(ro))
    t = ((1 + r) * (1 - s))
    ka = 1/(((math.sqrt(1 + (math.tan(tanro)) ** 2)) + math.atan(tanro) * math.sqrt(t)) ** 2)
    return ka

def jordtrykksfaktor_k0(friksjonsvinkel):
    '''
    Beregner hviletrykksfaktor
    
    Parameter:
        friksjonsvikel: friksjonsvinkel, støtter både tangens til friksjonsvnikel og grader

    Retur:
        Jordtrykksfaktor
    '''
    if friksjonsvinkel > 1:
        k0 =  1 - math.sin(math.radians(friksjonsvinkel))
    if friksjonsvinkel <= 1:
        k0 = 1 - math.sin(math.atan(friksjonsvinkel))
    return k0


def rb(Fh, B0, qv, a, tan_ro):
    '''
    Beregner rb TODO: Bedre beskrivelse
    
    Parameter:
        friksjonsvikel: dimensjonerende friksjonsvinkel, støtter både tangens til friksjonsvnikel og grader
        ruhet: fundamentruhet
        helling: helling framfor fundament


    Retur:
        Bæreevnefaktorer
    '''
    rb = (Fh/B0) / ((qv + a) * tan_ro)
    return rb

def n_fakt(tan_ro, ruhet, helling=10000):
    '''
    Beregner nq og n_Gamma faktorer for å berene bæreevne
    
    Parameter:
        friksjonsvikel: dimensjonerende friksjonsvinkel, støtter både tangens til friksjonsvnikel og grader
        ruhet: fundamentruhet
        helling: helling framfor fundament


    Retur:
        Bæreevnefaktorer
    '''
    tan_alpha = tan_ro + math.sqrt(1+tan_ro**2)
    N = tan_alpha**2
    r = math.atan(tan_ro)
    Kp = (2*N)/(N+1) * math.exp((math.pi/2 + r)*tan_ro)
    x0 = 2*(1-ruhet)*tan_ro
    r_r = math.atan(tan_ro)*180/math.pi
    ap = 0.25*math.pi + 0.5*r
    f_omega = 1/(ruhet+0.0001) * (1 - (math.sqrt(1 - (ruhet**2))))
    w_rad= math.atan(f_omega * math.tan(math.pi/4 + 0.5 * r))
    w = math.degrees(w_rad)
    s = (1/helling)/tan_ro
    aa_rad = math.pi/4 - r/2
    x0_list = []
    tanpsi = []
    psi = []
    c = []
    Rot = []
    xc = []
    diff = []
    n_gamma_list = []
    for i in range(20):
        if i == 0:
            x0_list.append(x0)
        else:
            x0_list.append(xc[i-1])
        tanpsi.append(x0_list[i]-tan_ro)
        psi.append(math.atan(tanpsi[i]))
        c.append((1+tanpsi[i]*tan_ro)*Kp*math.exp(2*psi[i]*tan_ro)-1)
        Rot.append((1-ruhet)**2 + (1-ruhet)/c[i])
        xc.append((1-ruhet+math.sqrt(Rot[i]))*tan_ro)
        diff.append((x0_list[i]-xc[i])**2)
        if diff[i] < 0.000001:
            n_gamma_list.append((2*c[i]*xc[i]+tan_ro)/(1+(tanpsi[i]**2)))
        else:
            n_gamma_list.append(1000)
    Nq = ((N+1)+(N-1)*math.cos(2*w_rad)) * math.exp((math.pi - 2*w_rad)*tan_ro)/2
    N_gamma = min(n_gamma_list)
        
    return Nq, N_gamma    

def reduksjonsfaktor(helling_forhold):
    if helling_forhold == 0:
        fsq = 1
        fsa = 1
    elif helling_forhold > 0 and helling_forhold <= 0.31:
        fsa = 1-(1.0667*helling_forhold)
        fsq = 1-(1.633*helling_forhold)
    elif helling_forhold > 0.31 and helling_forhold <= 0.41:
        fsa = 0.68-0.95*(helling_forhold-0.3)
        fsq = 0.51-1.3*(helling_forhold-0.3)
    elif helling_forhold > 0.41 and helling_forhold <= 0.51:
        fsa = 0.585-0.8*(helling_forhold-0.4)
        fsq = 0.38-1.2*(helling_forhold-0.4)
    elif helling_forhold > 0.51 and helling_forhold <= 0.61:
        fsa = 0.505-0.7*(helling_forhold-0.5)
        fsq = 0.26-0.8*(helling_forhold-0.5)
    elif helling_forhold > 0.61 and helling_forhold <= 0.71:
        fsa = 0.435-0.65*(helling_forhold-0.6)
        fsq = 0.18-0.65*(helling_forhold-0.6)
    elif helling_forhold > 0.71 and helling_forhold <= 0.75:
        fsa = 0.37-0.9*(helling_forhold-0.7)
        fsq = 0.115-0.7*(helling_forhold-0.7)
    else:
        fsa = 0
        fsq = 0

    return fsa, fsq

# def grunntrykk(lagpakke, djupne, gamma_eff, fsq, Nq, Ngamma, b0, attraksjon):
#     p_eff = lagpakke.loc[(lagpakke["Djupne"] == djupne), "Pv'"]
#     gamma_eff = 
#     return fsq * (Nq * p_eff) + (0.5 * Ngamma * gamma_eff * b0) + (Nq * fsa -1) * attraksjon

def virkelig_helling(vinkel_mot_terreng, vinkel_skjæring):
    tan_alpha = math.tan(math.radians(vinkel_skjæring))
    sin_beta = math.sin(math.radians(90-vinkel_mot_terreng))
    tan_delta = tan_alpha/sin_beta

    return round(math.degrees(math.atan(tan_delta)), 2)



#print(jordtrykksfaktor_ka(0.30))
#print(jordtrykksfaktor_k0(0.30))
#print(n_fakt(0.78/1.4, 0.17, 2))

print(virkelig_helling(45, 33))  
