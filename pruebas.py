import pandas as pd
import numpy as np
#import PIconnect
#from PIconnect.PIConsts import AuthenticationMode

wtg_num = 1.4
df_tags_pitch = pd.read_excel('./dataset/rubi_tag_ref.xlsx', sheet_name='temp_panel')
df_tags_pitch['cab_id'] = df_tags_pitch.iloc[:,1].apply(lambda x: int(x.split('chnRUBI50.')[1].split('.')[0]))
#self.df_tags_pitch['blade_id'] = self.df_tags_pitch.iloc[:,1].apply(lambda x: int(x.split('Pth')[1].split('AngVal')[0]))
#Lista de tags de pitch correspondientes a la turbina seleccionada wtg_num
lista_tags_pitch = df_tags_pitch[df_tags_pitch['cab_id']==int(wtg_num//1)].iloc[:,1]
print(lista_tags_pitch[0])
#
# PI.PIConfig.DEFAULT_TIMEZONE = 'Etc/GMT+5'
# PI_SERVER = 'PEREDGMOY1001'
# INTERVAL = '15m'
#
# with PI.PIServer(server=PI_SERVER, username='PE72247430', password='Enero##2023##',
#     authentication_mode=AuthenticationMode.WINDOWS_AUTHENTICATION) as server:
#     #avance:
#     #for tag_name in self.lista_tags_pitch: #3 tag's x turbina
#     query = server.search(lista_tags_pitch)
#     print(query)
#     pit_data_i = query[0].interpolated_values(start_d, end_d, self.INTERVAL)
#     pit_data_i = pit_data_i.to_numpy() # 1, 100, np.nan,
#     pit_data_i = pd.to_numeric(pit_data_i, errors='coerce')
#         #datos_pitch.append(pit_data_i)
# return pit_data_i
