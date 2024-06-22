#!/usr/bin/env python
# coding: utf-8

# In[70]:


import datetime as dt
from datetime import timedelta
import pandas as pd
from datetime import datetime
import streamlit as st
from market_profile import MarketProfile
import plotly.graph_objs as go
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, ColumnsAutoSizeMode


# In[ ]:


st.set_page_config(page_title="Análise com Market Profile", layout="wide", initial_sidebar_state="expanded")

st.title('Análise com Market Profile')

arquivo = st.sidebar.file_uploader("Escolha um arquivo .csv aqui", accept_multiple_files = False)


# In[ ]:


def filtra_dados(dados):
    
    dados_filtrados = pd.DataFrame()
    dados_filtrados.insert(0, "Date", 0, allow_duplicates = False)
    dados_filtrados.insert(1, "Open", 0, allow_duplicates = False)
    dados_filtrados.insert(2, "High", 0, allow_duplicates = False)
    dados_filtrados.insert(3, "Close", 0, allow_duplicates = False)
    dados_filtrados.insert(4, "Low", 0, allow_duplicates = False)
    dados_filtrados.insert(5, "Volume", 0, allow_duplicates = False)
    dados_filtrados.insert(6, "Dia", 0, allow_duplicates = False)

    cont = 0

    for j in dados.index:

        if("30" in dados.at[j, "Hora"] or "00" in dados.at[j, "Hora"]):

            dados_filtrados.at[cont, 'Date'] = dados.at[j, 'Data']
            dados_filtrados.at[cont, 'Open'] = dados.at[j, 'Abertura']
            dados_filtrados.at[cont, 'High'] = dados.at[j, 'Máxima']
            dados_filtrados.at[cont, 'Close'] = dados.at[j, 'Fechamento']
            dados_filtrados.at[cont, 'Low'] = dados.at[j, 'Mínima']
            dados_filtrados.at[cont, 'Volume'] = dados.at[j, 'Volume']
            dados_filtrados.at[cont, 'Dia'] = dados.at[j, 'Dia']
            cont = cont + 1
    
    return dados_filtrados


# In[ ]:


def prepara_dados_dia(dados_filtrados_dia):
    
    dados_filtrados_dia.sort_values(by=['Date'], inplace = True, ascending=[True])
        
    dados_filtrados_dia = dados_filtrados_dia.reset_index(drop = True)

    if(len(dados_filtrados_dia) > 0):

        for k in dados_filtrados_dia.index: 
            
            datas = dados_filtrados_dia['Date']
            abertura = dados_filtrados_dia['Open']
            maxima = dados_filtrados_dia['High']
            minima = dados_filtrados_dia['Low']
            fechamento = dados_filtrados_dia['Close']

            dia = pd.to_datetime(dados_filtrados_dia['Dia'].min(), format = "%d/%m/%Y")

            dados_filtrados_dia.at[k, 'Open'] = str(dados_filtrados_dia.at[k, 'Open']).replace(',', '.')
            dados_filtrados_dia.at[k, 'High'] = str(dados_filtrados_dia.at[k, 'High']).replace(',', '.')
            dados_filtrados_dia.at[k, 'Low'] = str(dados_filtrados_dia.at[k, 'Low']).replace(',', '.')
            dados_filtrados_dia.at[k, 'Close'] = str(dados_filtrados_dia.at[k, 'Close']).replace(',', '.')

        dados_filtrados_dia = dados_filtrados_dia.astype({"Open": "float64", "High": "float64", "Low": "float64", "Close": "float64", "Volume": "int64"})

        dados_filtrados_dia['Date'] = pd.to_datetime( dados_filtrados_dia['Date'], format = "%d/%m/%Y %H:%M")

        dados_filtrados_dia = dados_filtrados_dia.set_index('Date')

        dados_filtrados_dia = dados_filtrados_dia[['Open', 'High', 'Low', 'Close', 'Volume']]
        
    return datas, abertura, maxima, minima, fechamento, dia, dados_filtrados_dia


# In[ ]:


if(arquivo):

    dados = pd.read_csv(arquivo, engine='python', sep=None)
    
    for i in dados.index:
    
        data = pd.to_datetime(dados.at[i, 'Data'], format = "%d/%m/%Y %H:%M")

        dados.at[i, 'Dia'] = data.strftime("%d/%m/%Y")
        dados.at[i, 'Hora'] = data.strftime("%H:%M")
    
    dados_filtrados = filtra_dados(dados)
    
    dias = dados_filtrados['Dia'].unique()
    
    data_escolhida = st.selectbox("Escolha um dia para ser a base dos cálculos: ", dias)
       
    if(data_escolhida != ""):
        
        pd_dados_filtrados_dia = dados_filtrados.query("Dia == @data_escolhida")
        
        if(len(pd_dados_filtrados_dia) > 0):

            datas, abertura, maxima, minima, fechamento, dia, dados_filtrados_dia = prepara_dados_dia(pd_dados_filtrados_dia)

            mp = MarketProfile(dados_filtrados_dia.iloc[:,0:5])
            
            mp_slice = mp[dados_filtrados_dia.index.min():dados_filtrados_dia.index.max()]
            
            poc = mp_slice.poc_price
            
            vah = mp_slice.value_area[1]
            val = mp_slice.value_area[0]                
                    
            candlestick = go.Candlestick(x=datas,
                                         open=abertura,
                                         high=maxima,
                                         low=minima,
                                         close=fechamento)

            layout = go.Layout(title=f'Gráfico de Candlestick',
                               xaxis=dict(title='Data'),
                               yaxis=dict(title='Preço'))

            fig = go.Figure(data=[candlestick], layout=layout)
            
            fig.update_layout(autosize=False, width=500, height=1000)
            
            fig.add_hline(y=poc, line_width=2, line_color="green", annotation_text="POC - " + data_escolhida)
            
            fig.add_hline(y=vah, line_width=2, line_color="purple", annotation_text="VAH")
            fig.add_hline(y=val, line_width=2, line_color="purple", annotation_text="VAL")
            
            pocs = []
            
            cont = 0
            
            for a in range(len(dias)):
                
                if(cont >=5):
                    
                    break
                    
                else:
                
                    data_anterior = dia - timedelta(a+1)

                    data_anterior_str = data_anterior.date().strftime('%d/%m/%Y')

                    df_dados_filtrados_dia_anterior = dados_filtrados.query("Dia == @data_anterior_str")

                    if(len(df_dados_filtrados_dia_anterior) > 0):

                        datas_ant, abertura_ant, maxima_ant, minima_ant, fechamento_ant, dia_ant, dados_filtrados_dia_anterior = prepara_dados_dia(df_dados_filtrados_dia_anterior)

                        mp2 = MarketProfile(dados_filtrados_dia_anterior.iloc[:,0:5])

                        mp_slice2 = mp2[dados_filtrados_dia_anterior.index.min():dados_filtrados_dia_anterior.index.max()]

                        poc2 = mp_slice2.poc_price

                        fig.add_hline(y=poc2, line_width=2, line_dash="dot", line_color="green", annotation_text="POC - " + str(data_anterior_str))

                        pocs.append("POC - " + str(data_anterior_str) + ": " + str(poc2))

                        cont = cont + 1

            st.plotly_chart(fig, use_container_width = True)
            
            st.markdown("**VAH:** " + str(vah))
            st.markdown("**POC -** " + "**" + data_escolhida + ":** " + str(poc))
            st.markdown("**VAL:** " + str(val))
            st.text("")
            st.markdown("**POCs Anteriores**")
            
            for poc_ant in pocs:
                
                st.markdown(poc_ant)
            
            st.text("")
            st.text("")
            
            st.markdown("**Dados do dia selecionado:**")
                     
            st.dataframe(dados_filtrados_dia.iloc[:,0:5], height = 730, width = 700)


# In[ ]:




