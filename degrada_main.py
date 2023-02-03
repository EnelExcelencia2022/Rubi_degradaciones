# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'degrada.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import openpyxl
import pandas as pd
import numpy as np
import datetime

from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler

import pickle as pk
import os

import time
import usuario_pi
import degrada_ui

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import PIconnect as PI
from System.Net import NetworkCredential
from PIconnect.PIConsts import AuthenticationMode
#comentario 1
plt.style.use('ggplot')
#
# class Worker(QRunnable):
#
#     def __init__(self, fn, *args, **kwargs):
#         super(Worker, self).__init__()
#         # Store constructor arguments (re-used for processing)
#         self.fn = fn
#         self.args = args
#         self.kwargs = kwargs
#
#     @pyqtSlot()
#     def run(self):
#         '''
#         Initialise the runner function with passed args, kwargs.
#         '''
#         self.fn(*self.args, **self.kwargs)
#
# class PantallaPeque(QWidget):
#     def __init__(self, dictionario):
#         super().__init__()
#         layout = QVBoxLayout()
#         self.tableWidget = QTableWidget()
#
#         self.tableWidget.setRowCount(len(dictionario.keys()))
#         self.tableWidget.setColumnCount(2)
#         self.tableWidget.setHorizontalHeaderLabels(['Atributo', 'Valor'])
#
#         for i, (k, v) in enumerate(dictionario.items()):
#             self.tableWidget.setItem(i,0, QTableWidgetItem(k))
#             self.tableWidget.setItem(i,1, QTableWidgetItem(v))
#         self.tableWidget.move(0,0)
#
#
#         layout.addWidget(self.tableWidget)
#         self.setLayout(layout)

#Clase para la barra de herramientas de la grafica de matplotlib:
class NavigationToolbar(NavigationToolbar):
    # only display the buttons we need
    NavigationToolbar.toolitems = (
        ('Home', 'Reset original view', 'home', 'home'),
        ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
        ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
        ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
        ('Customize', 'Edit axis, curve and image parameters', 'qt4_editor_options', 'edit_parameters'),
        (None, None, None, None)
        # ('Save', 'Save the figure', 'filesave', 'save_figure'),
    )

class PandasModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                column=index.column()
                return str(self._data.iloc[index.row()][index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None

class CustomDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("HELLO!")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Something happened, is that OK?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)



class DegradaApp:
    def __init__(self, ui_obj):
        print('Cargando datos')
        self.ui_obj = ui_obj
        self.usuario_logeado = False
        self.df_pot = pd.read_pickle('./dataset/data_potencia.pkl')
        self.df_wind = pd.read_pickle('./dataset/data_viento.pkl')

        #pc ref:
        #self.df_mu = pd.read_excel('./dataset/wayra_pc_ref.xlsx', sheet_name='media').drop_duplicates().sort_values('BIN')
        #self.df_low = pd.read_excel('./dataset/wayra_pc_ref.xlsx', sheet_name='lowlim').drop_duplicates().sort_values('BIN')
        #self.df_pot = self.TransformaDF(self.df_pot)
        #self.df_wind = self.TransformaDF(self.df_wind)
        #pot_tags, wind_tags
        self.pot_tags = self.df_pot.columns[:-2]
        self.wind_tags = self.df_wind.columns[:-2]

        # INPUTS:
        #Lista de años disponibles
        self.YEAR_LIST = np.sort(list(self.df_pot.loc[:,'Anno'].unique()))
        #lista de meses:
        self.MONTH_LIST = np.sort(list(self.df_pot.loc[:,'Mes'].unique()))
        #Lista de WTG's:
        self.WTG_LIST = np.arange(1,len(self.pot_tags)+1)
        #MONTH_LIST, YEAR_LIST, WTG_LIST

        #DEFAULT:
        self.MES_I = datetime.datetime.now().month
        self.MES_J = datetime.datetime.now().month
        self.ANNO_I = 2022
        self.ANNO_J = 2021

        #Reemplazar datos faltantes
        self.df_pot.fillna(0, inplace=True)
        self.df_wind.fillna(0, inplace=True)

        #print('Transformando datos')

        #self.df_wind = self.df_wind.apply(self.EliminaErrores, axis=1)
        #self.df_pot = self.df_pot.apply(self.EliminaErrores, axis=1)

        #self.df_wind[['Anno','Mes']] = self.df_wind[['Anno','Mes']].astype('int')
        #self.df_pot[['Anno','Mes']] = self.df_pot[['Anno','Mes']].astype('int')

        #self.df_pot.to_pickle('./dataset/data_potencia.pkl')
        #self.df_wind.to_pickle('./dataset/data_viento.pkl')

        self.pot_arr = self.df_pot.to_numpy()
        self.wind_arr = self.df_wind.to_numpy()
        self.mes_idx = -2
        self.anno_idx = -1
        print('Cargando')
        #df_wind.info()

    def TransformaDF(self, df_original):
        df = df_original.copy()
        one_array = df.to_numpy()
        orig_shape = one_array.shape
        one_array = one_array.reshape(-1,)
        one_array = pd.to_numeric(one_array, errors='coerce')
        df = pd.DataFrame(one_array.reshape(orig_shape[0], orig_shape[1]), index=df.index.tz_localize(None), columns=df.columns)
        return df

    #TRANSFORMA DATOS NEGATIVOS A CERO PARA MEJORAR LAS GRAFICAS
    def EliminaErrores(self, serie1):
        serie1.loc[serie1<0] = 0
        return serie1

    def CalculaLP(self, puntos_x, puntos_y):
        df_ref = pd.read_excel('./dataset/wayra_pc_ref.xlsx', sheet_name='media')
        df_inf = pd.read_excel('./dataset/wayra_pc_ref.xlsx', sheet_name='lowlim')
        df_ref.drop_duplicates(inplace=True)
        df_inf.drop_duplicates(inplace=True)
        df_ref.sort_values('BIN', ascending=True)
        df_inf.sort_values('BIN', ascending=True)

        y_ideal = np.interp(puntos_x, df_ref.iloc[:,0], df_ref.iloc[:,1])
        y_low = np.interp(puntos_x, df_inf.iloc[:,0], df_inf.iloc[:,1])
        diff_arr = y_ideal - puntos_y
        diff_arr = np.nan_to_num(diff_arr)
        diff_arr = diff_arr[np.where(y_low>puntos_y)]

        prod_bruta = puntos_y.sum()/4000
        lp_total = round(diff_arr.sum()/4000,4)
        lp_per  = round(diff_arr.sum()/4000,4)/prod_bruta
        return lp_total, lp_per

    def analizaCurva(self, x, y, wtg_idx = 1):
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
            y_arr = np.linspace(1,16,10).reshape(-1,1)

        x_norm = scaler_x.fit_transform(x_arr)
        y_norm = scaler_y.fit_transform(y_arr).reshape(-1,)

        modelo = SVR(kernel='rbf', C=50, epsilon=.001)
        modelo.fit(x_norm, y_norm)

        x_test= np.linspace(4,13,100)
        x_test_n = scaler_x.transform(x_test.reshape(-1,1))

        y_hat_norm = modelo.predict(x_test_n)
        y_hat = scaler_y.inverse_transform(y_hat_norm.reshape(-1,1)).reshape(-1,)

        d1 = np.gradient(y_hat, x_test.reshape(-1,))
        d2 = np.gradient(d1, x_test.reshape(-1,))

        point_codo = d2.argmin()
        x_point = x_test[point_codo]
        y_point = y_hat[point_codo]

        curva_fit = np.array((x_test, y_hat))
        int_point = np.array([x_point, y_point])

        return curva_fit, int_point

    def EjecutaDiferencias(self, Tupla_I, Tupla_J):
        wtg_i, mes_i, anno_i = Tupla_I[0], Tupla_I[1], Tupla_I[2]
        wtg_j, mes_j, anno_j = Tupla_J[0], Tupla_J[1], Tupla_J[2]

        wind_i, pot_i = self.Getcurva(wtg_i, mes_i, anno_i) #filtra datos por wtg, mes y anno
        wind_j, pot_j = self.Getcurva(wtg_j, mes_j, anno_j) #filtra datos por wtg, mes y anno

        curva_y1, point_1 = self.analizaCurva(wind_i, pot_i, wtg_i)
        curva_y2, point_2 = self.analizaCurva(wind_j, pot_j, wtg_j)

        diff = point_1[0] - point_2[0]
        #diff_per = diff/point_2[0]

        lp_i, lp_p_i = self.CalculaLP(wind_i, pot_i)
        lp_j, lp_p_j = self.CalculaLP(wind_j, pot_j)
        diff_per = lp_p_i - lp_p_j
        return curva_y1, point_1, curva_y2, point_2, diff, diff_per*100

    def Ejecuta_analisis_app(self):
        self.todos_turbinas = self.ui_obj.checkBox_turbina.isChecked()
        if self.todos_turbinas:
            self.Ejecuta_analisis_mes()
        else:
            self.Ejecuta_turbina()

    def Ejecuta_turbina(self):
        self.MES_I = int(self.ui_obj.comboBox_MES_I.currentText())
        self.MES_J = int(self.ui_obj.comboBox_MES_J.currentText())
        self.ANNO_I = int(self.ui_obj.comboBox_ANNO_I.currentText())
        self.ANNO_J = int(self.ui_obj.comboBox_ANNO_J.currentText())

        #Anno I  Vs Anno J:
        self.curvas_wtgs_act = []
        self.puntos_wtg_act = []
        self.curvas_wtgs_past = []
        self.puntos_wtg_past = []
        self.diff_chache_list = []
        self.diff_per_chache_list = []

        self.Turbina_eval = int(self.ui_obj.comboBox_wtg.currentText()) # 1 al 42
        output_dict = {'WTG':[],
                       'delta Vel. [m/s]':[],
                       'delta Degr. [%]':[]
                      #'delta Norma':[]
                      }
        turbina_idx = self.Turbina_eval - 1 # 0 al 41
        tupla_1 = (turbina_idx, self.MES_I, self.ANNO_I)
        tupla_2 = (turbina_idx, self.MES_J, self.ANNO_J)
        curva_y1, point_1, curva_y2, point_2, diff, diff_per = self.EjecutaDiferencias(tupla_1, tupla_2)
        #diff_pw = (point_1[1]-point_2[1])
        #diff_Norm = np.sqrt(diff_pw**2 + diff_pw**2)
        #diff_Norm = np.sign(diff_per)*diff_Norm
        output_dict['WTG'].append(str(self.Turbina_eval))
        output_dict['delta Vel. [m/s]'].append(round(diff,4))
        output_dict['delta Degr. [%]'].append(round(diff_per,4))
        #output_dict['delta Norma'].append(round(diff_Norm,4))

        self.curvas_wtgs_act.append(curva_y1)
        self.puntos_wtg_act.append(point_1)
        self.curvas_wtgs_past.append(curva_y2)
        self.puntos_wtg_past.append(point_2)
        self.diff_chache_list.append(diff)
        self.diff_per_chache_list.append(diff_per)

        #PB_v += 1
        self.ui_obj.progressBar.setValue(100)

        df_out = pd.DataFrame(output_dict)
        df_out.sort_values(df_out.columns[-1], ascending=False, inplace=True)

        self.dict_data = {'curva1' : self.curvas_wtgs_act,
                         'punto1' : self.puntos_wtg_act,
                         'curva2' : self.curvas_wtgs_past,
                         'punto2' : self.puntos_wtg_past
                        }


        self.df_summ = pd.DataFrame(output_dict)
        self.df_summ.sort_values(self.df_summ.columns[1], ascending=False, inplace=True)
        TABLA_model = PandasModel(self.df_summ)
        self.ui_obj.tableView_TABLA.setModel(TABLA_model)

        #print(self.WTG_LIST)
        #len(self.WTG_LIST)
        self.ui_obj.comboBox_WTG_I.setCurrentIndex(np.where(self.WTG_LIST==int(self.df_summ.iloc[0,0]))[0][0])
        self.ui_obj.comboBox_WTG_J.setCurrentIndex(np.where(self.WTG_LIST==int(self.df_summ.iloc[0,0]))[0][0])
        self.ui_obj.comboBox_MES_I_GR.setCurrentIndex(np.where(self.MONTH_LIST==self.MES_I)[0][0])
        self.ui_obj.comboBox_MES_J_GR.setCurrentIndex(np.where(self.MONTH_LIST==self.MES_J)[0][0])
        self.ui_obj.comboBox_ANNO_I_GR.setCurrentIndex(np.where(self.YEAR_LIST==self.ANNO_I)[0][0])
        self.ui_obj.comboBox_ANNO_J_GR.setCurrentIndex(np.where(self.YEAR_LIST==self.ANNO_J)[0][0])

        self.GraficaCurvas_IZQ()


    def Ejecuta_analisis_mes(self):
        #calcula desplazamiento del presente mes vs el anno pasado:

        self.MES_I = int(self.ui_obj.comboBox_MES_I.currentText())
        self.MES_J = int(self.ui_obj.comboBox_MES_J.currentText())
        self.ANNO_I = int(self.ui_obj.comboBox_ANNO_I.currentText())
        self.ANNO_J = int(self.ui_obj.comboBox_ANNO_J.currentText())

        #Anno I  Vs Anno J:
        self.curvas_wtgs_act = []
        self.puntos_wtg_act = []
        self.curvas_wtgs_past = []
        self.puntos_wtg_past = []
        self.diff_chache_list = []
        self.diff_per_chache_list = []

        output_dict = {'WTG':[],
                       'delta Vel. [m/s]':[],
                       'delta Degr. [%]':[]
                      #'delta Norma':[]
                      }

        PB_v = 0 #inicio del valor de progession bar
        VALOR_PB = PB_v/self.WTG_LIST.shape[0]

        for wtg_idx, wtg_num in enumerate(self.WTG_LIST):
            #Analisis:
            tupla_1 = (wtg_idx, self.MES_I, self.ANNO_I)
            tupla_2 = (wtg_idx, self.MES_J, self.ANNO_J)
            curva_y1, point_1, curva_y2, point_2, diff, diff_per = self.EjecutaDiferencias(tupla_1, tupla_2)
            #diff_pw = (point_1[1]-point_2[1])
            #diff_Norm = np.sqrt(diff_pw**2 + diff_pw**2)
            #diff_Norm = np.sign(diff_per)*diff_Norm
            output_dict['WTG'].append(str(wtg_num))
            output_dict['delta Vel. [m/s]'].append(round(diff,4))
            output_dict['delta Degr. [%]'].append(round(diff_per,4))
            #output_dict['delta Norma'].append(round(diff_Norm,4))

            self.curvas_wtgs_act.append(curva_y1)
            self.puntos_wtg_act.append(point_1)
            self.curvas_wtgs_past.append(curva_y2)
            self.puntos_wtg_past.append(point_2)
            self.diff_chache_list.append(diff)
            self.diff_per_chache_list.append(diff_per)

            PB_v += 1
            self.ui_obj.progressBar.setValue(int(PB_v/self.WTG_LIST.shape[0]))

        self.ui_obj.progressBar.setValue(100)

        df_out = pd.DataFrame(output_dict)
        df_out.sort_values(df_out.columns[-1], ascending=False, inplace=True)

        self.dict_data = {'curva1' : self.curvas_wtgs_act,
                         'punto1' : self.puntos_wtg_act,
                         'curva2' : self.curvas_wtgs_past,
                         'punto2' : self.puntos_wtg_past
                        }


        self.df_summ = pd.DataFrame(output_dict)
        self.df_summ.sort_values(self.df_summ.columns[1], ascending=False, inplace=True)
        TABLA_model = PandasModel(self.df_summ)
        self.ui_obj.tableView_TABLA.setModel(TABLA_model)

        self.ui_obj.comboBox_WTG_I.setCurrentIndex(np.where(self.WTG_LIST==int(self.df_summ.iloc[0,0]))[0][0])
        self.ui_obj.comboBox_WTG_J.setCurrentIndex(np.where(self.WTG_LIST==int(self.df_summ.iloc[0,0]))[0][0])
        self.ui_obj.comboBox_MES_I_GR.setCurrentIndex(np.where(self.MONTH_LIST==self.MES_I)[0][0])
        self.ui_obj.comboBox_MES_J_GR.setCurrentIndex(np.where(self.MONTH_LIST==self.MES_J)[0][0])
        self.ui_obj.comboBox_ANNO_I_GR.setCurrentIndex(np.where(self.YEAR_LIST==self.ANNO_I)[0][0])
        self.ui_obj.comboBox_ANNO_J_GR.setCurrentIndex(np.where(self.YEAR_LIST==self.ANNO_J)[0][0])

        self.GraficaCurvas_IZQ()
        #with open('./data_dict.pkl', 'wb') as f:
        #    pk.dump(dict_data, f)

    def Getcurva(self, WTG_I, MES_I, ANNO_I):
        mascara_pwr_i = (self.pot_arr[:,self.mes_idx]==MES_I) * (self.pot_arr[:,self.anno_idx]==ANNO_I)
        mascara_wnd_i = (self.wind_arr[:,self.mes_idx]==MES_I)*(self.wind_arr[:,self.anno_idx]==ANNO_I)
        #pot_i = self.pot_arr[mascara_pwr_i, :][:, WTG_I]
        #wind_i = self.wind_arr[mascara_wnd_i, :][:, WTG_I]
        pot_i = self.pot_arr[mascara_pwr_i, WTG_I]
        wind_i = self.wind_arr[mascara_wnd_i, WTG_I]
        return wind_i, pot_i

    def GetPitchxWTG(self):
        wtg_num = int(self.ui_obj.comboBox_WTG_I.currentText())
        #conseguir datos del pitch:
        #descargar 1er batch de pitch:
        #serie 1 -> mes a evaluar
        start_d = datetime.datetime(self.ANNO_I, self.MES_I, 1, 0)
        if self.MES_I==12:
            mes_end_d = 1
            anno_end_d = self.ANNO_I + 1
            end_d = datetime.datetime(anno_end_d, mes_end_d, 1, 0)
        else:
            end_d = datetime.datetime(self.ANNO_I, self.MES_I+1, 1, 0)
        datos_pitch_I = []
        datos_pitch_I_raw = self.Descargar_datos_Pitch(wtg_num, start_d, end_d)
        wind_i, pot_i = self.Getcurva(wtg_num, self.MES_I, self.ANNO_I)
        for data_blade in datos_pitch_I_raw:
            #print(np.array(list(zip(wind_i, data_blade)))) #[[wind, pitch], [wind, pitch], [wind, pitch], ..., [wind, pitch]]
            datos_pitch_I.append(np.array(list(zip(wind_i, data_blade)))[:,1]) # [[wind, pitch], [wind, pitch], [wind, pitch], ..., [wind, pitch]]
        #serie 2:
        start_d = datetime.datetime(self.ANNO_J, self.MES_J, 1, 0)
        if self.MES_J==12:
            mes_end_d = 1
            anno_end_d = self.ANNO_J + 1
            end_d = datetime.datetime(anno_end_d, mes_end_d, 1, 0)
        else:
            end_d = datetime.datetime(self.ANNO_J, self.MES_J+1, 1, 0)
        datos_pitch_J = []
        datos_pitch_J_raw = self.Descargar_datos_Pitch(wtg_num, start_d, end_d)
        wind_j, pot_j = self.Getcurva(wtg_num, self.MES_J, self.ANNO_J)
        for data_blade in datos_pitch_J_raw:
            #print(np.array(list(zip(wind_i, data_blade)))) #[[wind, pitch], [wind, pitch], [wind, pitch], ..., [wind, pitch]]
            datos_pitch_J.append(np.array(list(zip(wind_j, data_blade)))[:,1])

        return datos_pitch_I, datos_pitch_J

    def GraficaCurvas_DER(self):
        if not(self.usuario_logeado):
            self.MostrarDialogo()
        self.figure2.clear()
        # create an axis
        axs = self.figure2.add_subplot(111)
        #fig, axs = plt.subplots(figsize=(8,6))
        COLOR_1 = 'tab:red'
        COLOR_2 = 'tab:blue'

        COLOR_1_alt = 'red'
        COLOR_2_alt = 'blue'

        ejex_name = self.ui_obj.comboBox_ejex.currentText()
        ejey_name = self.ui_obj.comboBox_ejey.currentText()
        self.WTG_I = int(self.ui_obj.comboBox_WTG_I.currentText())

        WTG_IDX_act = self.WTG_I - 1
        WTG_IDX_pst = self.WTG_J - 1

        wind_data_i, pot_data_i = self.Getcurva(WTG_IDX_act, self.MES_I, self.ANNO_I)
        wind_data_j, pot_data_j = self.Getcurva(WTG_IDX_pst, self.MES_J, self.ANNO_J)

        pitch_data_i, pitch_data_j = self.GetPitchxWTG()
        pala_num = int(self.ui_obj.comboBox_pala.currentText())-1
        idx = 0

        if ejex_name=='Velocidad':
            ejex_data_i = wind_data_i
            ejex_data_j = wind_data_j
        elif ejex_name=='Potencia':
            ejex_data_i = pot_data_i
            ejex_data_j = pot_data_j


        if ejey_name=='Velocidad':
            ejey_data_i = wind_data_i
            ejey_data_j = wind_data_j
        elif ejey_name=='Potencia':
            ejey_data_i = pot_data_i
            ejey_data_j = pot_data_j

        if ejex_name=='Pitch':
            ejex_data_i = pitch_data_i[pala_num] #Lista
            ejex_data_j = pitch_data_j[pala_num]

        if ejey_name=='Pitch':
            ejey_data_i = pitch_data_i[pala_num]
            ejey_data_j = pitch_data_j[pala_num]

        axs.scatter(ejex_data_j, ejey_data_j, color=COLOR_2, s=2, alpha=.4,
                    label=f'S1: WTG {self.WTG_I} - Mes {self.MES_J}/{self.ANNO_J}') # J
        axs.scatter(ejex_data_i, ejey_data_i, color=COLOR_1, s=2, alpha=.4,
                    label=f'S2: WTG {self.WTG_I} - Mes {self.MES_I}/{self.ANNO_I}') # I


        #axs.set_ylim([0,700])
        #axs.set_xlim([0,20])
        #axs.set_xticks(range(0,19,2))
        #axs.set_yticks(range(0,3500,500))
        #axs.set_xlabel('Velocidad de viento [m/s]', color='black', size=10)
        #axs.set_ylabel('Potencia [KW]', color='black', size=10)

        axs.legend(fontsize=10)
        self.canvas2.draw()


    def GraficaCurvas_IZQ(self):

        self.WTG_I = int(self.ui_obj.comboBox_WTG_I.currentText())
        if self.ui_obj.checkBox_BLOQUEAR.isChecked():
            self.WTG_J = self.WTG_I
            self.ui_obj.comboBox_WTG_J.setCurrentIndex(np.where(self.WTG_LIST==self.WTG_I)[0][0])
        else:
            self.WTG_J = int(self.ui_obj.comboBox_WTG_J.currentText())

        WTG_IDX_act = self.WTG_I - 1
        WTG_IDX_pst = self.WTG_J - 1

        data_act = self.Getcurva(WTG_IDX_act, self.MES_I, self.ANNO_I)
        data_past = self.Getcurva(WTG_IDX_pst, self.MES_J, self.ANNO_J)

        if len(self.dict_data['curva1'])>1:
            curva_y1, point_1 = self.dict_data['curva1'][WTG_IDX_act], self.dict_data['punto1'][WTG_IDX_act]
            curva_y2, point_2 = self.dict_data['curva2'][WTG_IDX_pst], self.dict_data['punto2'][WTG_IDX_pst]
            diff = self.diff_chache_list[WTG_IDX_act]
            diff_per = self.diff_per_chache_list[WTG_IDX_act]

        else:
            curva_y1, point_1 = self.dict_data['curva1'][0], self.dict_data['punto1'][0]
            curva_y2, point_2 = self.dict_data['curva2'][0], self.dict_data['punto2'][0]
            diff = self.diff_chache_list[0]
            diff_per = self.diff_per_chache_list[0]

        #diff = point_1[0] - point_2[0]
        #diff_per = diff/point_2[0]

        self.figure.clear()
        # create an axis
        axs = self.figure.add_subplot(111)
        #fig, axs = plt.subplots(figsize=(8,6))

        COLOR_1 = 'tab:red'
        COLOR_2 = 'tab:blue'

        COLOR_1_alt = 'red'
        COLOR_2_alt = 'blue'

        axs.scatter(data_past[0], data_past[1], color=COLOR_2, s=1.5, alpha=.4)
        axs.scatter(data_act[0], data_act[1], color=COLOR_1, s=1.5, alpha=.4)

        axs.plot(curva_y2[0], curva_y2[1], color=COLOR_2_alt, alpha=.75,
                    label=f'S1: WTG {self.WTG_J} - Mes {self.MES_J}/{self.ANNO_J}')
        axs.plot(curva_y1[0], curva_y1[1], color=COLOR_1_alt, alpha=.75,
                    label=f'S2: WTG {self.WTG_I} - Mes {self.MES_I}/{self.ANNO_I}')

        axs.plot([point_1[0], point_1[0]], [0, point_1[1]], color=COLOR_1_alt, linestyle='--', alpha=.5)
        axs.plot([0, point_1[0]], [ point_1[1], point_1[1]], color=COLOR_1_alt, linestyle='--', alpha=.5)
        axs.plot([point_2[0], point_2[0]], [0, point_2[1]], color=COLOR_2_alt, linestyle='--', alpha=.5)
        axs.plot([0, point_2[0]], [ point_2[1], point_2[1]], color=COLOR_2_alt, linestyle='--', alpha=.5)

        axs.text(x=0, y=2500, s=f''' S1: ({round(point_2[0],2)},  {round(point_2[1],2)})\n S2: ({round(point_1[0],2)},  {round(point_1[1],2)})''',
                fontsize=9)

        axs.set_ylim([0,3500])
        axs.set_xlim([0,18])
        axs.set_xticks(range(0,19,2))
        axs.set_yticks(range(0,3500,500))
        axs.set_xlabel('Velocidad de viento [m/s]', color='black', size=10)
        axs.set_ylabel('Potencia [KW]', color='black', size=10)

        axs.legend(loc='lower right', fontsize=9)
        self.canvas.draw()
        #plt.show()
        #axs.plot(curva_y1)

    #def ActualizaFechas(self):
    #    self.MES_I = int(self.ui_obj.comboBox_MES_I.currentText())
    #    self.MES_J = int(self.ui_obj.comboBox_MES_J.currentText())
    #    self.ANNO_I = int(self.ui_obj.comboBox_ANNO_I.currentText())
    #    self.ANNO_J = int(self.ui_obj.comboBox_ANNO_J.currentText())

    def ItemTabla_clicked(self, clickedIndex):
        row=clickedIndex.row()
        wtg_selected = int(self.df_summ.iloc[row,0])
        self.ui_obj.comboBox_WTG_I.setCurrentIndex(np.where(self.WTG_LIST==wtg_selected)[0][0])
        self.GraficaCurvas_IZQ()

    def ActualizarDatos_PI(self):
        if not(self.usuario_logeado):
            self.MostrarDialogo()
        self.SetupPI()
        self.Last_update = self.df_pot.index.max()
        self.now_datetime = datetime.datetime.now()

        wtg_pot_list = []
        wtg_win_list = []

        with PI.PIServer(server=self.PI_SERVER, username=self.PI_USER, password=self.PI_PASS,
                        authentication_mode=AuthenticationMode.WINDOWS_AUTHENTICATION) as server:
            #tag:
            #Descargar datos de potencia:
            for tag_name in self.pot_tags:
                query = server.search(tag_name)
                #print(query)
                pot_data_i = query[0].interpolated_values(self.Last_update, self.now_datetime, self.INTERVAL)
                wtg_pot_list.append(pot_data_i)

            for tag_name in self.wind_tags:
                query = server.search(tag_name)
                #print(query)
                win_data_i = query[0].interpolated_values(self.Last_update, self.now_datetime, self.INTERVAL)
                wtg_win_list.append(win_data_i)

        df_pot_new = pd.DataFrame(wtg_pot_list).T.iloc[1:,:]

        df_pot_new['Mes'] = df_pot_new.index.to_series().apply(lambda x: x.month)
        df_pot_new['Anno'] = df_pot_new.index.to_series().apply(lambda x: x.year)
        df_pot_new = self.TransformaDF(df_pot_new)
        df_pot_new = df_pot_new.apply(self.EliminaErrores, axis=1)
        df_pot_new[['Anno','Mes']] = df_pot_new[['Anno','Mes']].astype('int')

        self.df_pot = pd.concat([self.df_pot, df_pot_new])


        df_win_new = pd.DataFrame(wtg_win_list).T.iloc[1:,:]

        df_win_new['Mes'] = df_win_new.index.to_series().apply(lambda x: x.month)
        df_win_new['Anno'] = df_win_new.index.to_series().apply(lambda x: x.year)
        df_win_new = self.TransformaDF(df_win_new)
        df_win_new = df_win_new.apply(self.EliminaErrores, axis=1)
        df_win_new[['Anno','Mes']] = df_win_new[['Anno','Mes']].astype('int')

        self.df_wind = pd.concat([self.df_wind, df_win_new])

        fecha_min = self.df_pot.index.min().strftime('%d/%m/%Y')
        fecha_max = self.df_pot.index.max().strftime('%d/%m/%Y')
        self.ui_obj.lbl_actual.setText(f'Datos actualizados desde {fecha_min} al {fecha_max}')

        self.df_pot.to_pickle('./dataset/data_potencia.pkl')
        self.df_wind.to_pickle('./dataset/data_viento.pkl')

        self.pot_arr = self.df_pot.to_numpy()
        self.wind_arr = self.df_wind.to_numpy()

        #self.PIR_NUM = 1
    def Descargar_datos_Pitch(self, wtg_num, start_d, end_d):
        #son 3 angulos p/wtg:
        self.df_tags_pitch = pd.read_excel('./dataset/wayra_tag_ref.xlsx', sheet_name='pitch')
        self.df_tags_pitch['wtg_id'] = self.df_tags_pitch.iloc[:,1].apply(lambda x: int(x.split('MWTG')[1].split('.')[0]))
        self.df_tags_pitch['blade_id'] = self.df_tags_pitch.iloc[:,1].apply(lambda x: int(x.split('Pth')[1].split('AngVal')[0]))
        #Lista de tags de pitch correspondientes a la turbina seleccionada wtg_num
        self.lista_tags_pitch = self.df_tags_pitch[self.df_tags_pitch['wtg_id']==wtg_num].iloc[:,1].to_list()
        datos_pitch = [] #3 arreglos x turbina
        with PI.PIServer(server=self.PI_SERVER, username=self.PI_USER, password=self.PI_PASS,
            authentication_mode=AuthenticationMode.WINDOWS_AUTHENTICATION) as server:
            #avance:
            for tag_name in self.lista_tags_pitch: #3 tag's x turbina
                query = server.search(tag_name)
                #print(query)
                pit_data_i = query[0].interpolated_values(start_d, end_d, self.INTERVAL)
                pit_data_i = pit_data_i.to_numpy() # 1, 100, np.nan,
                pit_data_i = pd.to_numeric(pit_data_i, errors='coerce')
                datos_pitch.append(pit_data_i)
        return datos_pitch

    def SetupPI(self):
        PI.PIConfig.DEFAULT_TIMEZONE = 'Etc/GMT+5'
        self.PI_SERVER = 'PEREDGMOY1001'
        self.INTERVAL = '15m'
        # Datos de Cabina y query:
        #self.END_D = datetime.datetime.now()
        #self.START_D = self.END_D - datetime.timedelta(days=30)
        #Carga de datos:
        #TAGS:

    def DescargaTabla(self):
        ahora_dt = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
        self.df_summ.to_excel(f'./RESULTADOS/resultado_{ahora_dt}.xlsx', index=False)
        path = "./RESULTADOS"
        path = os.path.realpath(path)
        os.startfile(path)

    def DescargaGrafica(self):
        self.WTG_I = int(self.ui_obj.comboBox_WTG_I.currentText())
        self.WTG_J = int(self.ui_obj.comboBox_WTG_J.currentText())

        WTG_IDX_act = self.WTG_I - 1
        WTG_IDX_pst = self.WTG_J - 1

        mascara_pwr_i = (self.pot_arr[:,self.mes_idx]==self.MES_I) * (self.pot_arr[:,self.anno_idx]==self.ANNO_I)
        mascara_wnd_i = (self.wind_arr[:,self.mes_idx]==self.MES_I)*(self.wind_arr[:,self.anno_idx]==self.ANNO_I)
        pot_i = self.df_pot.iloc[mascara_pwr_i, WTG_IDX_act]
        wind_i = self.df_wind.iloc[mascara_wnd_i, WTG_IDX_act]

        mascara_pwr_j = (self.pot_arr[:,self.mes_idx]==self.MES_J) * (self.pot_arr[:,self.anno_idx]==self.ANNO_J)
        mascara_wnd_j = (self.wind_arr[:,self.mes_idx]==self.MES_J)*(self.wind_arr[:,self.anno_idx]==self.ANNO_J)
        pot_j = self.df_pot.iloc[mascara_pwr_j, WTG_IDX_pst]
        wind_j = self.df_wind.iloc[mascara_wnd_j, WTG_IDX_pst]

        df_puntos1 = pd.concat([wind_i, pot_i], axis=1)
        df_puntos2 = pd.concat([wind_j, pot_j], axis=1)
        df_puntos = pd.concat([df_puntos2, df_puntos1])

        data_act = self.Getcurva(WTG_IDX_act, self.MES_I, self.ANNO_I)
        data_past = self.Getcurva(WTG_IDX_pst, self.MES_J, self.ANNO_J)

        curva_y1, point_1 = self.dict_data['curva1'][WTG_IDX_act], self.dict_data['punto1'][WTG_IDX_act]
        curva_y2, point_2 = self.dict_data['curva2'][WTG_IDX_pst], self.dict_data['punto2'][WTG_IDX_pst]

        ahora_dt = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')

        file_name = f'./RESULTADOS/grafica_{ahora_dt}_WTG_{self.WTG_I}.xlsx'
        #df.to_excel(writer, sheet_name=key)
        #writer.save()
        #writer.close()
        #
        #
        df_curva_1 = pd.DataFrame({'velocidad':curva_y1[0],
                                    'Potencia': curva_y1[1]
                                    })
        df_curva_2 = pd.DataFrame({'velocidad':curva_y2[0],
                                    'Potencia': curva_y2[1]
                                    })
        with pd.ExcelWriter(file_name) as writer:
            df_puntos.to_excel(writer, sheet_name=f'PI_data')
            df_curva_1.to_excel(writer, sheet_name=f'Curva_{self.MES_I}_{self.ANNO_I}')
            df_curva_2.to_excel(writer, sheet_name=f'Curva_{self.MES_J}_{self.ANNO_J}')
        #
        #writer.save()
        #writer.close()

        path = "./RESULTADOS"
        path = os.path.realpath(path)
        os.startfile(path)
        #df_curvas =

    def BloquearOpcionesGR(self):
        if self.ui_obj.checkBox_BLOQUEAR.isChecked():
            #self.WTG_J = self.WTG_I
            self.ui_obj.comboBox_WTG_J.setEnabled(False)
            #self.ui_obj.comboBox_WTG_J.setCurrentIndex(np.where(self.WTG_LIST==self.WTG_I)[0][0])
        else:
            self.ui_obj.comboBox_WTG_J.setEnabled(True)
            #self.WTG_J = int(self.ui_obj.comboBox_WTG_J.currentText())

    def MostrarDialogo(self):
        Dialog = QtWidgets.QDialog()
        ui = usuario_pi.Ui_Dialog()
        ui.setupUi(Dialog)
        #Dialog.exec_()
        if Dialog.exec():
            print(f'Bienvenido {ui.lineEdit.text()}')
            self.PI_USER = ui.lineEdit.text()
            self.PI_PASS = ui.lineEdit_2.text()
            self.SetupPI()
            self.ui_obj.label_usuario.setText(f'Bienvenido {self.PI_USER}')
            self.usuario_logeado = True
            #print('Actualizando datos...')
            # try:
            #     self.ActualizarDatos_PI()
            # except:
            #     print('error al actualizar')
        else:
            print('Actualizacion cancelada')


        # self.dlg_obj = CustomDialog()
        # if self.dlg_obj.exec():
        #     print('Ejecutar')
        # else:
        #     print('Cancel')

    def setupUi(self, MainWindow):
        self.mainwindow = MainWindow
        self.ui_obj.setupUi(MainWindow)
        fecha_min = self.df_pot.index.min().strftime('%d/%m/%Y')
        fecha_max = self.df_pot.index.max().strftime('%d/%m/%Y')
        self.ui_obj.lbl_actual.setText(f'Datos actualizados desde {fecha_min} al {fecha_max}')

        self.ui_obj.comboBox_ANNO_I.addItems([str(x) for x in self.YEAR_LIST])
        self.ui_obj.comboBox_ANNO_I.setCurrentIndex(np.where(self.YEAR_LIST == self.ANNO_I)[0][0])
        #self.ui_obj.comboBox_ANNO_I.activated.connect(self.ActualizaFechas)

        self.ui_obj.comboBox_ANNO_J.addItems([str(x) for x in self.YEAR_LIST])
        self.ui_obj.comboBox_ANNO_J.setCurrentIndex(0)
        #self.ui_obj.comboBox_ANNO_J.activated.connect(self.ActualizaFechas)

        self.ui_obj.comboBox_MES_I.addItems([str(x) for x in self.MONTH_LIST])
        self.ui_obj.comboBox_MES_I.setCurrentIndex(np.where(self.MONTH_LIST == self.MES_I)[0][0])
        #self.ui_obj.comboBox_MES_I.activated.connect(self.ActualizaFechas)

        self.ui_obj.comboBox_MES_J.addItems([str(x) for x in self.MONTH_LIST])
        self.ui_obj.comboBox_MES_J.setCurrentIndex(np.where(self.MONTH_LIST == self.MES_J)[0][0])
        #self.ui_obj.comboBox_MES_J.activated.connect(self.ActualizaFechas)

        self.ui_obj.comboBox_WTG_I.addItems([str(x) for x in self.WTG_LIST])
        self.ui_obj.comboBox_WTG_I.activated.connect(self.GraficaCurvas_IZQ)

        self.ui_obj.comboBox_WTG_J.addItems([str(x) for x in self.WTG_LIST])
        self.ui_obj.comboBox_WTG_J.activated.connect(self.GraficaCurvas_IZQ)

        self.ui_obj.comboBox_wtg.addItems([str(x) for x in self.WTG_LIST])
        #self.ui_obj.comboBox_wtg.activated.connect(self.GraficaCurvas_IZQ)
        self.ui_obj.comboBox_pala.addItems([str(x) for x in range(1,4)])
        #self.ui_obj.comboBox_MES_J.activated.connect(self.ActualizaFechas)

        self.ui_obj.comboBox_MES_I_GR.addItems([str(x) for x in self.MONTH_LIST])
        self.ui_obj.comboBox_MES_J_GR.addItems([str(x) for x in self.MONTH_LIST])
        self.ui_obj.comboBox_ANNO_I_GR.addItems([str(x) for x in self.YEAR_LIST])
        self.ui_obj.comboBox_ANNO_J_GR.addItems([str(x) for x in self.YEAR_LIST])

        self.lista_ejey = ['Potencia', 'Velocidad']
        self.lista_ejex = ['Potencia', 'Velocidad']
        self.df_tags_names = pd.read_excel('./dataset/wayra_tag_ref.xlsx', sheet_name=0)
        self.lista_ejey.extend(self.df_tags_names.iloc[:,0].to_list())
        self.lista_ejex.extend(self.df_tags_names.iloc[:,0].to_list())
        self.ui_obj.comboBox_ejey.addItems(self.lista_ejey)
        self.ui_obj.comboBox_ejex.addItems(self.lista_ejex)

        self.ui_obj.progressBar.setValue(0)

        self.ui_obj.pushButton_EJECUTAR.clicked.connect(self.Ejecuta_analisis_app)
        self.ui_obj.pushButton_ACTUALIZAR.clicked.connect(self.ActualizarDatos_PI)
        self.ui_obj.pushButton_login.clicked.connect(self.MostrarDialogo)
        self.ui_obj.pushButton_DESCARGAR_TABLA.clicked.connect(self.DescargaTabla)
        self.ui_obj.pushButton_DESCARGA_GR_IZ.clicked.connect(self.DescargaGrafica)
        self.ui_obj.pushButton_graf_der.clicked.connect(self.GraficaCurvas_DER)

        self.ui_obj.checkBox_BLOQUEAR.stateChanged.connect(self.BloquearOpcionesGR)

        self.ui_obj.tableView_TABLA.clicked.connect(self.ItemTabla_clicked)

        #self.figure, self.axs = plt.subplots(figsize=(8,8))
        #ax.imshow(np.random.random((50,50)));
        #self.figure.canvas.draw()
        #labels = ['-10','0','22','20','30','40'] or
        #labels[2]=22
        #ax.set_xticklabels(labels)

        self.figure = plt.figure(figsize=(5, 5), dpi=100, layout='tight')
        self.canvas = FigureCanvas(self.figure)
        self.toolbar1 = NavigationToolbar(self.canvas, self.mainwindow)
        #self.ui_obj.verticalLayout_izq.addWidget(self.toolbar1)
        self.ui_obj.verticalLayout_izq.addWidget(self.canvas)


        self.figure2 = plt.figure(figsize=(5, 5), dpi=100, layout='tight')
        self.canvas2 = FigureCanvas(self.figure2)

        #Toolbar for matplotlib graph
        self.toolbar2 = NavigationToolbar(self.canvas2, self.mainwindow)
        #self.canvas = self.figure.canvas
        # Create a placeholder widget to hold our toolbar and canvas.
        #widget = QtWidgets.QWidget()
        #widget.setLayout(self.ui_obj.verticalLayout_izq)
        #self.mainwindow.setCentralWidget(widget)

        #self.canvas = self.figure.canvas
        self.ui_obj.verticalLayout_der.addWidget(self.toolbar2)
        self.ui_obj.verticalLayout_der.addWidget(self.canvas2)

        #self.ui_obj.comboBox_ANNO_I.activated.connect(self.ActualizaFechas)



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = degrada_ui.Ui_MainWindow()
    ui_app = DegradaApp(ui)
    print('Ejecutando...')
    ui_app.setupUi(MainWindow)
    print('Configurando UI')
    MainWindow.show()
    print('Mostando')
    sys.exit(app.exec_())
