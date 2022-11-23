import grunn

lag1 = grunn.JordLag("Leire", 400, 18)
#lag2 = grunn.JordLag("Sand", 470, 16)
#lag3 = grunn.JordLag("Leire", 2090, 19.4)
lag1.sett_styrke_parameter(30, attraksjon=3, kohesjon=0, cu=0)
#lag2.sett_styrke_parameter(34, attraksjon=2, kohesjon=0, cu=0)
#lag3.sett_styrke_parameter(27, attraksjon=5, kohesjon=0, cu=0)
lag1.sett_stivhet(m=10)
#lag2.sett_stivhet(m=10)
#lag3.sett_stivhet(m=10)


#jordlagliste = [lag1, lag2, lag3]
jordlagsliste = [lag1]
#print(jordlagliste)
profil1 = grunn.JordProfil(jordlagsliste, 0)
profil1.setning_endelig(60, b=1000, l=1000)
print(profil1.df)
print(profil1.total_setning())
profil2 = grunn.JordProfil(jordlagsliste, 0)
profil2.setning_uendelig(60)
print(profil2.df)
print(profil2.total_setning())
