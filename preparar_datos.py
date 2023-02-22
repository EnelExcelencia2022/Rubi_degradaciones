import pandas as pd
import numpy as np
# def TransformaDF(df_original):
#     df = df_original.copy()
#     one_array = df.to_numpy()
#     orig_shape = one_array.shape
#     one_array = one_array.reshape(-1,)
#     one_array = pd.to_numeric(one_array, errors='coerce')
#     df = pd.DataFrame(one_array.reshape(orig_shape[0], orig_shape[1]), index=df.index, columns=df.columns)
#     return df
#
# df = pd.read_excel(f'dataset/jgto_pot_dc.xlsx', index_col=0, parse_dates=True)
# print(df.head())
# df = TransformaDF(df)
# df['Mes'] = df.index.to_series().apply(lambda x: x.month)
# df['Anno'] = df.index.to_series().apply(lambda x: x.year)
#
# df.to_pickle('./dataset/jgto_pot_dc.pk')


# dfp = pd.read_csv('./dataset/potencia_rubi.csv', index_col=0, parse_dates=True)
# dfi = pd.read_csv('./dataset/irradiancia_rubi.csv', index_col=0, parse_dates=True)
#
# dfp.to_pickle('./dataset/potencia_rubi.pk')
# dfi.to_pickle('./dataset/irradiancia_rubi.pk')



#curva de potencia:
df_mu = pd.read_excel('./pc_ref_sas.xlsx', sheet_name=2)
df_low = pd.read_excel('./pc_ref_sas.xlsx', sheet_name=1)

df_mu.drop_duplicates(inplace=True)
df_low.drop_duplicates(inplace=True)

df_mu.sort_values('bin',ascending=True)
df_low.sort_values('bin',ascending=True)

df_out = pd.merge(df_mu, df_low, on='bin')
df_out.to_csv('./pc_ref.csv')
