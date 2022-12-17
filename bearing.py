import math
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.interpolate import splrep, splev, interp1d
import matplotlib.ticker as ticker
import streamlit as st

tanr_B3 = st.number_input('tan ro', min_value=0.0, max_value=1.0, value=0.55, step=0.05)
tanac_B4 = tanr_B3 + math.sqrt(1+(tanr_B3**2))
b_B5 = st.number_input('B0', min_value=0.1, max_value=10.0, value=4.0, step=0.1)
r_B6 = 0.5
if r_B6 == 0:
    r_B6 = 0.00000000000001
if r_B6 == 1:
    r_B6 = 0.9999999999999
fw_B7 = 1/r_B6*(1 - math.sqrt(1-(r_B6**2)))
tanw_B8 = fw_B7 * tanac_B4
ac_B9 = math.atan(tanac_B4)
w_B10 = math.atan(tanw_B8)
ac1_B11 = ac_B9 - w_B10
ac0_B12 = ac_B9 + w_B10
r0_B13 = math.sin(ac1_B11)/math.sin(ac0_B12+ac1_B11)*b_B5
deletall_B14 = 5
dr0_B15 = r0_B13/deletall_B14

fundamentopptegning = [[0, -abs(b_B5)], [0.01*b_B5, 0.01*b_B5]]

R1_B131 = r0_B13 * math.exp((math.pi/2-w_B10)*tanr_B3)
DR1_E131 = R1_B131/deletall_B14
DX1_E132 = DR1_E131*math.sin(ac_B9)*2
DY1_E133 = DR1_E131*math.cos(ac_B9)

theta_B50 = math.pi/2-w_B10
dtet1_B51 = theta_B50/deletall_B14

######
#Sone1
######

skare11 = range(1,6)
skare11_xh = []
skare11_xh.append(-abs(b_B5))
for i in skare11:
    skare11_xh.append(-abs((i)) * dr0_B15*math.cos(ac0_B12))

skare11_yh = []
skare11_yh.append(0)
for i in skare11:
    skare11_yh.append(-abs((i)) * dr0_B15*math.sin(ac0_B12))

skare11_xv = []
for i in range(0,6):
    skare11_xv.append((skare11_yh[i])/math.tan(ac1_B11)+skare11_xh[i])

skare11_yv = [0] * 6

skare12_xh = []
skare12_xh.append(0)
for i in range(1,6):
    skare12_xh.append(-abs(b_B5/deletall_B14*i))
#print(f'skare12_xh: {skare12_xh}')

skare12_xv = []
skare12_xv_0 = -abs(r0_B13)*math.cos(ac0_B12)
#print(f'skare12_xv_0:{skare12_xv_0}')
skare12_xv.append(skare12_xv_0)
for i in range(1,6):
    skare12_xv.append(skare12_xv_0-((((b_B5+skare12_xv_0)/deletall_B14*i))))
    print((b_B5+skare12_xv_0)/deletall_B14*i)
#print(f'skare12_xv: {skare12_xv}')

skare12_yh = [0] * 6
#print(f'skare12_yh: {skare12_yh}')
skare12_yv = []
skare12_yv_0 = -abs(r0_B13*math.sin(ac0_B12))
skare12_yv.append(skare12_yv_0)
for i in range(1,6):
    skare12_yv.append((deletall_B14-i)*skare12_yv_0/deletall_B14)
#print(f'skare12_yv: {skare12_yv}')

#####
#Sone2
#####

# Utrekning av polarkoordinater for spiraler
v = []
v.append(ac_B9+w_B10)
v.append(dtet1_B51+ac_B9+w_B10)
for i in range(2,6):
    v.append(i*dtet1_B51+ac_B9+w_B10)

theta_liste = []
for i in range(0,6):
    theta_liste.append(v[i]-(ac_B9+w_B10))

r_liste = []
for i in range(0,6):
    r_liste.append(r0_B13*math.exp(theta_liste[i]*tanr_B3))

#Utrekning for radier for spiral
radie_x0 = [0] * 6
radie_y0 = [0] * 6
radie_x1 = []
for i in range(0,6):
    radie_x1.append(r_liste[i]*math.cos(math.pi + v[i]))
radie_y1 = []
for i in range(0,6):
    radie_y1.append(r_liste[i]*math.sin(math.pi + v[i]))

#Utrekning for sone 3
skare31_xv = []
skare31_xv.append(0)
for i in range(1,6):
    skare31_xv.append(i * DR1_E131*math.sin(ac_B9))

skare31_xh = []
skare31_xh.append(2* R1_B131 *math.sin(ac_B9))
for i in range(1,6):
    skare31_xh.append(2*skare31_xv[i])

skare31_yh = [0] * 6

skare31_yv = []
skare31_yv.append(0)
for i in range(1,6):
    skare31_yv.append(-abs(i)*DR1_E131*math.cos(ac_B9))

skare32_xh = []
for i in range(0,6):
    skare32_xh.append((R1_B131+i*DR1_E131)*math.sin(ac_B9))


skare32_xv = []
skare32_xv.append(0)
for i in range(1,6):
    skare32_xv.append(i*DX1_E132)

skare32_yh = []
for i in range(0,6):
    skare32_yh.append(-abs(deletall_B14-i)*DY1_E133)

skare32_yv = [0] * 6

#Kapasiteter

tanr_r = []
tr_temp = 0

while tr_temp < 1.01:
    tanr_r.append(round(tr_temp,2))
    tr_temp += 0.05

nq_liste = []
for value in tanr_r:
    nq_liste.append(value + math.sqrt(1+(value**2)))

n_liste = []
for verdi in nq_liste:
    n_liste.append(verdi**2)

fw = []
fw.append(0)
for i in range(2, 12, 2):
    it = i/10
    fw.append((1-(math.sqrt(1-(it**2))))/it)


#Utrekning for Nq diagram
fw_ = (1-(math.sqrt(1-(r_B6**2))))/r_B6
nq_ = tanr_B3 + math.sqrt(1+tanr_B3**2)
n_ = nq_**2
Nq_ = (1+fw_**2)/(1+n_*fw_**2)*n_ * math.exp((math.pi-2*math.atan(fw_*nq_))*tanr_B3)
r_tanr_Nq = r_B6*tanr_B3*Nq_

#Utrekning for pil
v_ = -abs(math.atan(r_tanr_Nq/Nq_))
b_neg = -abs(b_B5)

pil_x = []
pil_x.append(b_B5*math.sin(v_)+(b_neg/2))
pil_x.append(-abs(b_B5/2))
pil_x.append((0.2*b_B5)*(math.sin(v_ + math.pi/6))+(b_neg/2))
pil_x.append(-abs(b_B5/2))
pil_x.append((0.2*b_B5)*(math.sin(v_ - math.pi/6))+(b_neg/2))



pil_y = []
pil_y.append(b_B5*math.cos(v_))
pil_y.append(0)
pil_y.append((0.2*b_B5)*(math.cos(v_ + math.pi/6)))
pil_y.append(0)
pil_y.append((0.2*b_B5)*(math.cos(v_ - math.pi/6)))





#Plotter ut Nq diagram
fig1, ax10 = plt.subplots(figsize=[4,8])
for value in fw:
    temp_nq = []
    for i in range(0, len(tanr_r)):
        temp_nq.append((1+value**2)/(1+n_liste[i]*value**2)*n_liste[i] * math.exp((math.pi-2*math.atan(value*nq_liste[i]))*tanr_r[i]))
    ax10.plot(tanr_r, temp_nq, color="black")
ax10.scatter(tanr_B3, Nq_)
ax10.set_yscale("log")
ax10.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y,pos: ('{{:.{:1d}f}}'.format(int(np.maximum(-np.log10(y),0)))).format(y)))
ax10.xaxis.grid()
ax10.yaxis.grid()
#plt.show()
#st.pyplot(fig1)

#Plotting

fig, ax1 = plt.subplots()

ax1.plot(fundamentopptegning[0], fundamentopptegning[1], color="black")

#Sone 1
for i in range(6):
    ax1.plot([skare11_xh[i], skare11_xv[i]],[skare11_yh[i], skare11_yv[i]], color='r')
for i in range(6):
    ax1.plot([skare12_xh[i], skare12_xv[i]],[skare12_yh[i], skare12_yv[i]], color='r')

#Radier for spiral
for i in range(6):
    ax1.plot([radie_x0[i], radie_x1[i]],[radie_y0[i], radie_y1[i]], color='b')

#Spiralen 
for i in range(1,6):
    x_temp = []
    y_temp = []
    for n in range(0,6):
        x_temp.append((r_liste[n]/deletall_B14*i) * math.cos(math.pi + v[n]))
        y_temp.append((r_liste[n]/deletall_B14*i) * math.sin(math.pi + v[n]))
    x_array = np.array(x_temp)
    y_array = np.array(y_temp)
    smuth = interp1d(x=x_array, y=y_array, kind=2)
    x2 = np.linspace(start=min(x_temp), stop=max(x_temp), num=1000)
    y2 = smuth(x2)
    ax1.plot(x2, y2, color='b')

#Sone 3
for i in range(6):
    ax1.plot([skare31_xh[i], skare31_xv[i]],[skare31_yh[i], skare31_yv[i]], color='g')
for i in range(6):
    ax1.plot([skare32_xh[i], skare32_xv[i]],[skare32_yh[i], skare32_yv[i]], color='g')

ax1.plot(pil_x, pil_y)
ax1.xaxis.grid()
ax1.yaxis.grid()
ax1.set_aspect(1)
ax1.set_ylabel("Vertikal (m)")
ax1.set_xlabel("Horisontal (m)")

#Pil

plt.show()
st.pyplot(fig)

