import pandas as pd
import pandas_datareader.data as web
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


###### Initialization, Starting Functions ######
st.set_page_config(page_title='US Treasury Yield Curve', page_icon='💵', layout='wide')

@st.cache(ttl=60*12)
def download_data(tickers, start_date, end_date):
    df = web.DataReader(tickers, 'fred', start_date, end_date)
    return df

###### FRED Symbols, and Data Download ######

treasuries = ['DGS1MO', 'DGS3MO', 'DGS6MO', 'DGS1', 'DGS2', 'DGS3', 'DGS5', 'DGS7', 'DGS10', 'DGS20', 'DGS30']

end_date = dt.date.today()
start_date = end_date - dt.timedelta(365*5)

yields = download_data(treasuries, start_date, end_date)
yields = yields.dropna()

###### Yield Curve ######
yield_curve_today = yields[::-1].transpose().reset_index()
idx = range(len(yield_curve_today.columns))
idx = idx[1:]
idx = idx[::-1]

date_select = st.select_slider('**Adjust slider to explore previous yields (5 year history)**',
    options=idx,
    value=idx[-1])
st.write('Showing data for', str(yield_curve_today.columns[date_select])[:11])


yield_curve_today = yield_curve_today.iloc[:,[0,date_select]]
yield_curve_today.columns = ['Treasury Duration','Yield']
yield_curve_today['Treasury Duration'] = ['1-month', '3-month', '6-month', '1-year', '2-year', '3-year', '5-year', '7-year', '10-year', '20-year', '30-year']

###### Yield Investion Matrix ######
inversion_matrix = pd.DataFrame()

for i in range(len(yield_curve_today)):
  diff = yield_curve_today['Yield'] - yield_curve_today['Yield'].iloc[i]
  inversion_matrix = inversion_matrix.append(diff)

inversion_matrix.columns = yield_curve_today['Treasury Duration']
inversion_matrix.set_index(yield_curve_today['Treasury Duration'], inplace = True)

inversion_matrix['1-month'][:] = 0
inversion_matrix['3-month'][1:] = 0 
inversion_matrix['6-month'][2:] = 0 
inversion_matrix['1-year'][3:] = 0 
inversion_matrix['2-year'][4:] = 0
inversion_matrix['3-year'][5:] = 0
inversion_matrix['5-year'][6:] = 0 
inversion_matrix['7-year'][7:] = 0 
inversion_matrix['10-year'][8:] = 0 
inversion_matrix['20-year'][9:] = 0 
inversion_matrix['30-year'][10:] = 0 

###### Layout ######

st.table(yield_curve_today.set_index('Treasury Duration').transpose())

col1, col2 = st.columns([1,1])

with col1:
    fig_yield_curve = px.line(yield_curve_today, x='Treasury Duration', y='Yield')
    st.plotly_chart(fig_yield_curve, use_container_width=True)

with col2:
    fig_inversion_matrix = px.imshow(inversion_matrix, color_continuous_scale='RdYlGn', text_auto=True, zmin=-1, zmax=1)
    st.plotly_chart(fig_inversion_matrix, use_container_width=True)
