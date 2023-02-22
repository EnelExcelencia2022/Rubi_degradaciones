import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
import matplotlib.pyplot as plt
df_pot = pd.read_pickle('./dataset/potencia_jgto.pk')
df_wind = pd.read_pickle('./dataset/irradiancia_jgto.pk')

df_1 = df_pot.loc[df_pot['Mes']==2,:]
df_1 = df_1.loc[df_1['Anno']==2022,:]

df_2 = df_wind.loc[df_wind['Mes']==2,:]
df_2 = df_2.loc[df_2['Anno']==2022,:]


y = df_1.iloc[:,0].to_numpy()
x = df_2.iloc[:,0].to_numpy()

scaler_x = StandardScaler()
scaler_y = StandardScaler()

x_arr = x.reshape(-1,)
y_arr = y.reshape(-1,)

error_mask = (y_arr>0)*(x_arr>0)

if any(error_mask):
    x_arr = x_arr[error_mask].reshape(-1,1)
    y_arr = y_arr[error_mask].reshape(-1,1)
else:
    x_arr = np.ones(10).reshape(-1,1)
    y_arr = np.linspace(1,1100,10).reshape(-1,1)

x_norm = scaler_x.fit_transform(x_arr)
y_norm = scaler_y.fit_transform(y_arr).reshape(-1,)

modelo = SVR(kernel='rbf', C=1, epsilon=.1)
modelo.fit(x_norm, y_norm)

x_test= np.linspace(60,1100,100)
x_test_n = scaler_x.transform(x_test.reshape(-1,1))

y_hat_norm = modelo.predict(x_test_n)
y_hat = scaler_y.inverse_transform(y_hat_norm.reshape(-1,1)).reshape(-1,)

#d1 = np.gradient(y_hat, x_test.reshape(-1,))
#d2 = np.gradient(d1, x_test.reshape(-1,))

#point_codo = d2.argmin()
#x_point = x_test[point_codo]
#y_point = y_hat[point_codo]
#Cuando y_hat==800
y_point= 800
x_point = np.interp(y_point, y_hat, x_test)

curva_fit = np.array((x_test, y_hat))
int_point = np.array([x_point, y_point])

fig, axs = plt.subplots(figsize=(10,10))
axs.scatter(x,y)
axs.plot(x_test, y_hat, 'r-')
plt.show()
