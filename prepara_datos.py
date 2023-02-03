import pandas as pd
import numpy as np

def TransformaDF(df_original):
    df = df_original.copy()
    one_array = df.to_numpy()
    orig_shape = one_array.shape
    one_array = one_array.reshape(-1,)
    one_array = pd.to_numeric(one_array, errors='coerce')
    df = pd.DataFrame(one_array.reshape(orig_shape[0], orig_shape[1]), index=df.index.tz_localize(None), columns=df.columns)
    return df

df_pot = pd.read_excel('./dataset/potencia_rubi.xlsx', index_col=0, parse_dates=True)
df_wind = pd.read_excel('./dataset/irradiancia_rubi.xlsx', index_col=0, parse_dates=True)

df_pot['Mes'] = df_pot.index.to_series().apply(lambda x: x.month)
df_pot['Anno'] = df_pot.index.to_series().apply(lambda x: x.year)

df_wind['Mes'] = df_pot.index.to_series().apply(lambda x: x.month)
df_wind['Anno'] = df_pot.index.to_series().apply(lambda x: x.year)
#pc ref:
#self.df_mu = pd.read_excel('./dataset/wayra_pc_ref.xlsx', sheet_name='media').drop_duplicates().sort_values('BIN')
#self.df_low = pd.read_excel('./dataset/wayra_pc_ref.xlsx', sheet_name='lowlim').drop_duplicates().sort_values('BIN')
df_pot = TransformaDF(df_pot)
df_wind = TransformaDF(df_wind)

df_pot.to_csv('./potencia_rubi.csv')
df_wind.to_csv('./irradiancia_rubi.csv')
