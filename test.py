import grunn

lag1 = grunn.JordLag("Silt", 5, 19)
lag2 = grunn.JordLag("Sand", 7, 18)
lag3 = grunn.JordLag("Leire", 9, 19.4)
lag1.sett_styrke_parameter(30, attraksjon=3, kohesjon=0, cu=0)
lag1.sett_stivhet(m=40)
print(lag1)
print(lag1.df)

jordlagliste = [lag1, lag2, lag3]
print(jordlagliste)
profil1 = grunn.JordProfil(jordlagliste)
print(profil1.jordarter)
