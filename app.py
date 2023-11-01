import streamlit as st
import pandas as pd
import altair as alt
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(layout="wide")

# Hide Streamlit footer  --------------------------
hide_streamlit_style = """
<style>
[data-testid="stToolbar"] {visibility: hidden !important;}
footer {visibility: hidden !important;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
#--------------------------------------------------

url = 'https://docs.google.com/spreadsheets/d/1V6ucyFGKWuSQzvI8lMzvvWJHrBS82echMVJH37kwgjE/gviz/tq?tqx=out:csv&sheet='

def load_data():
    url_googlesheet = url
    df_vd = pd.read_csv(
        f'{url_googlesheet}Range',
        decimal=','
    )
    df_w = pd.read_csv(
        f'{url_googlesheet}Weight'
    )
    df = df_vd.merge(
        df_w[['Car', 'Total']],
        left_on='Car',
        right_on='Car'
    )
    df_gcar = df.groupby('Car').agg(
        {
            'km': ['mean', 'min', 'max'],
            'Total': ['mean'],
            'Capacity': ['mean'],
            'Wh/km': ['mean'],
        }
    ).sort_values(by=('km', 'mean'), ascending=False)
    df_gcar.columns = df_gcar.columns.droplevel(0)
    df_gcar.columns = ['mean_km', 'min_km', 'max_km', 'weight', 'kw', 'Wh/km']
    df_gcar['car'] = df_gcar.index
    df_gcar['err_km'] = df_gcar['max_km'] - df_gcar['min_km']
    df_gcar = df_gcar[['car', 'mean_km', 'min_km', 'max_km', 'err_km', 'weight', 'kw', 'Wh/km']]
    df_gcar["Wh/km"] = df_gcar["Wh/km"] / 10

    col_dict = {
        "car": "Make Model",
        "mean_km": "Average Range (km)",
        "min_km": "Minimum Range (km)",
        "max_km": "Maximum Range (km)",
        "weight": "Weight (kg)",
        "kw": "Battery Capacity (kW)",
        "Wh/km": "Energy Consumption (kWh/100km)",
    }
    df_gcar.rename(columns=col_dict, inplace=True)

    return df_gcar


# Load data - as Pandas DataFrames
df = load_data()
df.to_json('./static/data.json', orient='records')


# Sidebar Selection
st.sidebar.markdown("### Select Car:")
df_ini = df["Make Model"]
select = st.sidebar.selectbox("[Make Model]", df_ini, index=1)
uid = df_ini[df_ini.index == select].index.values[0]

selection = alt.selection_point(
    bind='legend'
)
# highlight = alt.selection_single()

# Chart of Range vs Weight
chart_rw = alt.Chart(df).mark_circle(size=30, stroke='lightblue').encode(
    x = alt.X('Weight (kg)').scale(domain=(1000, 3200)),
    y = alt.Y('Average Range (km)').scale(domain=(0, 750)),
    # color="Dataset",
    tooltip=[
        "Make Model",
        "Average Range (km)",
        "Weight (kg)",
        "Battery Capacity (kW)",
        "Energy Consumption (kWh/100km)",
    ],
    size='Battery Capacity (kW)',
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
).interactive().add_params(selection)

highlighted_point_rw = alt.Chart(
    df[df["Make Model"] == uid]
).mark_circle(size=30, stroke='red').encode(
    x = alt.X('Weight (kg)').scale(domain=(1000, 3200)),
    y = alt.Y('Average Range (km)').scale(domain=(0, 750)),
    #color="Dataset",
    size='Battery Capacity (kW)',
    tooltip=[
        "Make Model",
        "Average Range (km)",
        "Weight (kg)",
        "Battery Capacity (kW)",
        "Energy Consumption (kWh/100km)",
    ],
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
).interactive().add_params(selection)

chart_rw_h = chart_rw + highlighted_point_rw

# Chart of Conasumption vs Weight
chart_cw = alt.Chart(df).mark_circle(size=30, stroke='lightblue').encode(
    x = alt.X('Weight (kg)').scale(domain=(1000, 3200)),
    y = alt.Y('Energy Consumption (kWh/100km)').scale(domain=(10, 45)),
    # color="Dataset",
    tooltip=[
        "Make Model",
        "Average Range (km)",
        "Weight (kg)",
        "Battery Capacity (kW)",
        "Energy Consumption (kWh/100km)",
    ],
    size='Battery Capacity (kW)',
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
).interactive().add_params(selection)

highlighted_point_cw = alt.Chart(
    df[df["Make Model"] == uid]
).mark_circle(size=30, stroke='red').encode(
    x = alt.X('Weight (kg)').scale(domain=(1000, 3200)),
    y = alt.Y('Energy Consumption (kWh/100km)').scale(domain=(10, 45)),
    #color="Dataset",
    size='Battery Capacity (kW)',
    tooltip=[
        "Make Model",
        "Average Range (km)",
        "Weight (kg)",
        "Battery Capacity (kW)",
        "Energy Consumption (kWh/100km)",
    ],
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
).interactive().add_params(selection)

chart_cw_h = chart_cw + highlighted_point_cw


# Layout Application 

container1 = st.container()
col1, col2 = st.columns(2)

with container1:
    with col1:
        # st.markdown("## iniuva Targets") 
        st.markdown("#### Range vs Weight")
        st.altair_chart(
           chart_rw_h, theme=None, use_container_width=True
        )

    with col2:
        st.markdown("#### Energy Consumption vs Weight")
        st.altair_chart(
           chart_cw_h, theme=None, use_container_width=True
        )

container2 = st.container()

with container2:
    df_sel = df[df["Make Model"] == uid]
    ss = df_sel.T
    ss.columns = ["Selected Car"]
    st.table(ss)

    st.markdown(
        "Credit goes to [Bjørn Nyland](https://www.youtube.com/user/bjornnyland) for performing extensive testing and making the [data publicly available](https://docs.google.com/spreadsheets/d/1V6ucyFGKWuSQzvI8lMzvvWJHrBS82echMVJH37kwgjE/edit?usp=sharing)."
    )