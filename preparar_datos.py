import pandas as pd
import numpy as np
def TransformaDF(df_original):
    df = df_original.copy()
    one_array = df.to_numpy()
    orig_shape = one_array.shape
    one_array = one_array.reshape(-1,)
    one_array = pd.to_numeric(one_array, errors='coerce')
    df = pd.DataFrame(one_array.reshape(orig_shape[0], orig_shape[1]), index=df.index, columns=df.columns)
    return df

df = pd.read_excel(f'dataset/rubi_temp.xlsx', index_col=0, parse_dates=True)
df = TransformaDF(df)
df['Mes'] = df.index.to_series().apply(lambda x: x.month)
df['Anno'] = df.index.to_series().apply(lambda x: x.year)

df.to_pickle('./dataset/rubi_temp_panel.pk')


# dfp = pd.read_csv('./dataset/potencia_rubi.csv', index_col=0, parse_dates=True)
# dfi = pd.read_csv('./dataset/irradiancia_rubi.csv', index_col=0, parse_dates=True)
#
# dfp.to_pickle('./dataset/potencia_rubi.pk')
# dfi.to_pickle('./dataset/irradiancia_rubi.pk')

print(df.head())
