import streamlit as st
import plotly.graph_objects as go
import wbgapi as wb
from datetime import date
import time
from model import *

st.set_page_config(layout="wide")
st.title("Country Economic Analysis and Forecasting")
st.write("\n")
st.write("\n")
st.write("\n")

def plot_actual_predicted(df, df_pred, plot_title, column, y_title = 'US$'):
    # Create the actual data trace
    actual_trace = go.Scatter(
        x=df['years'],
        y=df[column],
        mode='lines',
        name='Actual'
    )

    # Create the predicted data trace
    predicted_trace = go.Scatter(
        x=df_pred['years'],
        y=df_pred['predicted_mean'],
        mode='lines',
        name='Predicted'
    )

    # Create the line trace joining actual and predicted
    line_trace = go.Scatter(
        x=[df['years'].iloc[-1], df_pred['years'].iloc[0]],
        y=[df[column].iloc[-1], df_pred['predicted_mean'].iloc[0]],
        mode='lines',
        name='Joining Line'
    )

    # Create the layout
    layout = go.Layout(
        xaxis=dict(title='Year'),
        yaxis=dict(title=y_title),
        title= plot_title,
        showlegend=True
    )

    # Create the figure
    fig = go.Figure(data=[actual_trace, predicted_trace, line_trace], layout=layout)
    config = {'staticPlot': True}

    # Display the figure using Streamlit
    st.plotly_chart(fig, use_container_width=True, config=config)

economylist = []
economyID = []

for i in wb.economy.list():
    economylist.append(i['value'].lower())
    economyID.append(i['id'])

if 'economylist' not in st.session_state:
    st.session_state['economylist'] = economylist

if 'economyID' not in st.session_state:
    st.session_state['economyID'] = economyID

input = st.text_input('Input Country Here')
forcast = st.text_input('Input Future Year (not more than 50 years in the future)')

if input:
    result = -1

    for index, value in enumerate(st.session_state['economylist']):
        if value == input.lower():
            result = index
            break

    if result != -1:

        if forcast:
            checker = forcast.isdigit()
            today = date.today()
            year = today.year

            if checker is True and int(forcast) > year:
                diff = year - int(forcast)

                if diff <= 50:
                    ECONOMY, GDP_df, EXP_df, IMP_df, UMP_df = model(st.session_state['economyID'][result], 2000, year, forcast_years = diff)
                    progress_text = "Beep Boop Loading Plots"
                    my_bar = st.progress(0, text=progress_text)

                    for percent_complete in range(100):
                        time.sleep(0.01)
                        my_bar.progress(percent_complete + 1, text=progress_text)
                    time.sleep(1)
                    my_bar.empty()

                    col1, col2 = st.columns(2)
                    
                    with col1:    
                        plot_actual_predicted(ECONOMY, GDP_df, 'GDP', 'NY.GDP.MKTP.CD')
                        plot_actual_predicted(ECONOMY, IMP_df, 'Total Imports', 'NE.IMP.GNFS.CD')
                    
                    with col2:          
                        plot_actual_predicted(ECONOMY, UMP_df, 'Unemployment Rate', 'SL.UEM.TOTL.ZS', y_title = 'Percent(%)')
                        plot_actual_predicted(ECONOMY, EXP_df, 'Total Exports', 'NE.EXP.GNFS.CD')
                else:
                    st.write("Not more than 50 years")

            else:
                st.write("Invalid input")

    else:
        st.write("Country not found")
