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


# In[ ]:


st.set_page_config(page_title="Análise com Market Profile", layout="wide", initial_sidebar_state="expanded")

st.title('Análise com Market Profile')

dados_obtidos = False

arquivo1 = st.sidebar.file_uploader("Escolha um arquivo .csv com os dados de abertura, máxima, fechamento e mínima aqui", accept_multiple_files = False)

if(arquivo1):

    dados_iniciais = pd.read_csv(arquivo1, engine='python', sep=None, encoding='ANSI')

    if("Abertura" in dados_iniciais.columns):

        if("Data" in dados_iniciais.columns):

            if("Máxima" in dados_iniciais.columns):

                if("Fechamento" in dados_iniciais.columns):

                    if("Mínima" in dados_iniciais.columns):

                        st.sidebar.text("Dados importados com sucesso!")

                        arquivo2 = st.sidebar.file_uploader("Escolha um arquivo .csv com os dados de volume aqui", accept_multiple_files = False)
                        
                        if(arquivo2):

                            dados_volume = pd.read_csv(arquivo2, engine='python', sep=None, encoding='ANSI')

                            if("Data" in dados_volume.columns):

                                if("Volume Financeiro" in dados_volume.columns):

                                    st.sidebar.text("Dados de volume importados com sucesso!")

                                    dados = pd.merge(dados_iniciais, dados_volume, on="Data")
                                    
                                    if(len(dados) > 0):
                                        
                                        dados_obtidos = True

                                else:

                                    st.sidebar.text("Arquivo inválido - sem dados de Volume'")

                            else:

                                st.sidebar.text("Arquivo inválido - sem dados da 'Data'")

                    else:

                        st.sidebar.text("Arquivo inválido - sem dados da 'Mínima'")

                else:

                    st.sidebar.text("Arquivo inválido - sem dados da 'Fechamento'")

            else:

                st.sidebar.text("Arquivo inválido - sem dados da 'Máxima'")

        else:

            st.sidebar.text("Arquivo inválido - sem dados da 'Data'")

    else:

        st.sidebar.text("Arquivo inválido - sem dados de 'Abertura'")


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

        dados_filtrados.at[cont, 'Date'] = dados.at[j, 'Data']
        dados_filtrados.at[cont, 'Open'] = dados.at[j, 'Abertura']
        dados_filtrados.at[cont, 'High'] = dados.at[j, 'Máxima']
        dados_filtrados.at[cont, 'Close'] = dados.at[j, 'Fechamento']
        dados_filtrados.at[cont, 'Low'] = dados.at[j, 'Mínima']
        dados_filtrados.at[cont, 'Volume'] = dados.at[j, 'Volume Financeiro']
        dados_filtrados.at[cont, 'Dia'] = dados.at[j, 'Dia']
        cont = cont + 1
    
    return dados_filtrados


# In[ ]:


def prepara_dados_dia(dados_filtrados_dia):
    
    dados_filtrados_dia.sort_values(by=['Date'], inplace = True, ascending=[True])
        
    dados_filtrados_dia = dados_filtrados_dia.reset_index(drop = True)

    if(len(dados_filtrados_dia) > 0):

        for k in dados_filtrados_dia.index: 

            dia = pd.to_datetime(dados_filtrados_dia['Dia'].min(), format = "%d/%m/%Y")

            dados_filtrados_dia.at[k, 'Open'] = str(dados_filtrados_dia.at[k, 'Open']).replace(',', '.')
            dados_filtrados_dia.at[k, 'High'] = str(dados_filtrados_dia.at[k, 'High']).replace(',', '.')
            dados_filtrados_dia.at[k, 'Low'] = str(dados_filtrados_dia.at[k, 'Low']).replace(',', '.')
            dados_filtrados_dia.at[k, 'Close'] = str(dados_filtrados_dia.at[k, 'Close']).replace(',', '.')

        dados_filtrados_dia = dados_filtrados_dia.astype({"Open": "float64", "High": "float64", "Low": "float64", "Close": "float64", "Volume": "int64"})

        dados_filtrados_dia['Date'] = pd.to_datetime( dados_filtrados_dia['Date'], format = "%d/%m/%Y %H:%M")

        dados_filtrados_dia = dados_filtrados_dia.set_index('Date')

        dados_filtrados_dia = dados_filtrados_dia[['Open', 'High', 'Low', 'Close', 'Volume']]
        
    return dia, dados_filtrados_dia


# In[ ]:


if(dados_obtidos):

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

            dia, dados_filtrados_dia = prepara_dados_dia(pd_dados_filtrados_dia)

            mp = MarketProfile(dados_filtrados_dia.iloc[:,0:5])

            mp_slice = mp[dados_filtrados_dia.index.min():dados_filtrados_dia.index.max()]

            poc = mp_slice.poc_price

            vah = mp_slice.value_area[1]
            val = mp_slice.value_area[0]                

            pocs_texto = []
            pocs = []
            datas_grafico = []
            cores = []
            
            datas_grafico.append(data_escolhida)

            cont = 0

            for a in range(len(dias)):

                if(cont >=5):

                    break

                else:

                    data_anterior = dia - timedelta(a+1)

                    data_anterior_str = data_anterior.date().strftime('%d/%m/%Y')
                    
                    datas_grafico.append(data_anterior_str)

                    df_dados_filtrados_dia_anterior = dados_filtrados.query("Dia == @data_anterior_str")

                    if(len(df_dados_filtrados_dia_anterior) > 0):

                        if(cont == 0):
                            
                            df_dados_filtrados_dia_anterior = df_dados_filtrados_dia_anterior.reset_index(drop = True)
                            
                            fechamento_dia_anterior = df_dados_filtrados_dia_anterior.at[0, 'Close']
                            
                            if(type(fechamento_dia_anterior) == str):
                                
                                fechamento_dia_anterior = float(fechamento_dia_anterior.replace(',', '.'))

                        dia_ant, dados_filtrados_dia_anterior = prepara_dados_dia(df_dados_filtrados_dia_anterior)

                        mp2 = MarketProfile(dados_filtrados_dia_anterior.iloc[:,0:5])

                        mp_slice2 = mp2[dados_filtrados_dia_anterior.index.min():dados_filtrados_dia_anterior.index.max()]

                        poc2 = mp_slice2.poc_price
                        
                        if(poc2 >= fechamento_dia_anterior):
                
                            cores.append("red")

                        else:

                            cores.append("green")

                        pocs.append(poc2)
                        pocs_texto.append("POC - " + str(data_anterior_str) + ": " + str(poc2))                        

                        cont = cont + 1
                        
            df_dados_filtrados_grafico_consolidado = pd.DataFrame()
                        
            for data_grafico in datas_grafico:
                
                df_dados_filtrados_grafico = dados_filtrados.query("Dia == @data_grafico")
                
                df_dados_filtrados_grafico_consolidado = pd.concat([df_dados_filtrados_grafico_consolidado, df_dados_filtrados_grafico])
            
            df_dados_filtrados_grafico_consolidado.sort_values(by=['Date'], inplace = True, ascending=[True])
            df_dados_filtrados_grafico_consolidado = df_dados_filtrados_grafico_consolidado.reset_index(drop = True)
            
            for k in df_dados_filtrados_grafico_consolidado.index: 

                df_dados_filtrados_grafico_consolidado.at[k, 'Open'] = str(df_dados_filtrados_grafico_consolidado.at[k, 'Open']).replace(',', '.')
                df_dados_filtrados_grafico_consolidado.at[k, 'High'] = str(df_dados_filtrados_grafico_consolidado.at[k, 'High']).replace(',', '.')
                df_dados_filtrados_grafico_consolidado.at[k, 'Low'] = str(df_dados_filtrados_grafico_consolidado.at[k, 'Low']).replace(',', '.')
                df_dados_filtrados_grafico_consolidado.at[k, 'Close'] = str(df_dados_filtrados_grafico_consolidado.at[k, 'Close']).replace(',', '.')
            
            df_dados_filtrados_grafico_consolidado = df_dados_filtrados_grafico_consolidado.astype({"Open": "float64", "High": "float64", "Low": "float64", "Close": "float64", "Volume": "int64"})
            
            df_dados_filtrados_grafico_consolidado['Date'] = pd.to_datetime(df_dados_filtrados_grafico_consolidado['Date'], format = "%d/%m/%Y %H:%M")
                        
            datas = df_dados_filtrados_grafico_consolidado['Date']
            abertura = df_dados_filtrados_grafico_consolidado['Open']
            maxima = df_dados_filtrados_grafico_consolidado['High']
            minima = df_dados_filtrados_grafico_consolidado['Low']
            fechamento = df_dados_filtrados_grafico_consolidado['Close']
            
            df_dados_filtrados_grafico_consolidado = df_dados_filtrados_grafico_consolidado.set_index('Date')

            df_dados_filtrados_grafico_consolidado = df_dados_filtrados_grafico_consolidado[['Open', 'High', 'Low', 'Close', 'Volume']]
            
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

            if(poc >= fechamento_dia_anterior):
                
                cor = "red"
                
            else:
                
                cor = "green"

            fig.add_hline(y=poc, line_width=2, line_color=cor, annotation_text="POC - " + str(data_escolhida) + ": " + str(poc), annotation_position="top right", annotation_font_size=12, annotation_font_color="black")
            
            if(vah >= fechamento_dia_anterior):
                
                cor = "red"
                
            else:
                
                cor = "green"

            fig.add_hline(y=vah, line_width=2, line_color=cor, annotation_text="VAH: " + str(vah), annotation_position="top right", annotation_font_size=12, annotation_font_color="blue")
            
            if(val >= fechamento_dia_anterior):
                
                cor = "red"
                
            else:
                
                cor = "green"
            
            fig.add_hline(y=val, line_width=2, line_color=cor, annotation_text="VAL: " + str(val), annotation_position="top right", annotation_font_size=12, annotation_font_color="blue")
            
            cont_pocs = 0

            for poc_ant in pocs:
                
                fig.add_hline(y=pocs[cont_pocs], line_width=2, line_color=cores[cont_pocs], annotation_text=pocs_texto[cont_pocs], annotation_position="top right", annotation_font_size=12, annotation_font_color="black")
                cont_pocs = cont_pocs + 1

            fig.update_xaxes(type="category")
            
            st.plotly_chart(fig, use_container_width = True)
            
            st.text("")
            st.text("")

            st.markdown("**Dados do dia selecionado:**")

            st.dataframe(df_dados_filtrados_grafico_consolidado.iloc[:,0:5], height = 730, width = 700)


# In[ ]:




