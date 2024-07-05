import streamlit as st
import streamlit_analytics as sta
import pandas as pd
import math
import kaleido
from math import sqrt
from plotly import figure_factory 

st.markdown(
    """
    <style>
.css-m70y {display:none}{
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <style>
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

s1 = dict(selector='th', props=[('text-align', 'center')])
s2 = dict(selector='td', props=[('text-align', 'center')])
# you can include more styling paramteres, check the pandas docs


# Load CSV data
df_stats = pd.read_csv('stats.csv',encoding='latin-1')  # CSV with name, attack, defense, hp
df_levels = pd.read_csv('cp_mod.csv',encoding='latin-1')  # CSV with level, percent

col1,  col2,col3, col4 = st.columns([2,1,2,2])

with col1:
    # UI for selecting name, attack2, defense2, hp2, level2
    streamlit_analytics.start_tracking()
    name2 = st.selectbox('Pokemon', df_stats['Name'])
    streamlit_analytics.stop_tracking()
    attack2 =st.slider('Attack IV', 0, 15, 15)
    defense2 = st.slider('Defense IV', 0, 15, 15)
    hp2 = st.slider('HP IV', 0, 15, 15)
    #level2 = st.slider('Select Level', 0, 51, 25)
    if st.button('Generate CP Table'):
        run_calc = True
    else:
        run_calc = False

if run_calc:
    results = []
    for level in range(1,52):
    # Find records in the CSVs
        character_stats = df_stats[df_stats['Name'] == name2].iloc[0]
        level_percent = df_levels[df_levels['Level'] == level].iloc[0]['CPM']
    
        # Calculation
        total_attack = ((character_stats['Attack'] + attack2) * level_percent)
        total_defense = (sqrt((character_stats['Defense'] + defense2 ) * level_percent))
        total_hp = (sqrt((character_stats['HP'] + hp2) * level_percent))
    
        cp = max(math.floor((total_attack * total_defense * total_hp) / 10),10)
        results.append({'Level': level, 'CP': cp})
        
        
    results_df = pd.DataFrame(results)
    #results_df.set_index('Level', inplace=True)
    with col3:
        
        table1 = results_df[0:25].style.hide(axis="index").set_table_styles([s1,s2]).to_html()     
        st.write(f'{table1}', unsafe_allow_html=True)
        #st.sidebar.write("CP Values by Level", results_df)
        #st.markdown(results_df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        #st.write(results_df)
    with col4 :
        
        table2 = results_df[25:52].style.hide(axis="index").set_table_styles([s1,s2]).to_html()     
        st.write(f'{table2}', unsafe_allow_html=True)
    with col1:
        @st.cache_data
        def convert_df(df):
           return df.to_csv(index=False).encode('utf-8')
        
        def createImage(df):
            fig = figure_factory.create_table(results_df)
            fig.update_layout(autosize=True)
            fig.write_image(str(name2 + ".png"), scale=2, engine="kaleido")

        csv = convert_df(results_df)
        
        createImage(results_df)
        with open(str(name2 + ".png"), "rb") as file:
            st.download_button(
                "Download as Image",
                data=file,
                file_name= str(name2 + ".png"),
                mime="image/png",
            )

        st.download_button(
           "Save csv",
           csv,
           str(name2 + ".csv"),
           "text/csv",
           key='download-csv'
        )
    run_calc = True
                



                # Streamlit application
        #st.write("DataFrame:")
        #st.write(df)
    
        # Download button
