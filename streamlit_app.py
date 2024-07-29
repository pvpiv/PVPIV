import streamlit as st
import streamlit_analytics
import pandas as pd
import math
import kaleido
from math import sqrt
from plotly import figure_factory 
import json
from google.cloud import firestore
from google.oauth2 import service_account
from datetime import date
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
if 'last_sel' not in st.session_state:
    st.session_state['last_sel'] = None
def load_new(counts, collection_name):
    """Load count data from firestore into `counts`."""

    # Retrieve data from firestore.
    key_dict = json.loads(st.secrets["textkey"])
    #creds = firestore.Client.from_service_account_json(key_dict)
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="pvpogo")
   
    col = db.collection(collection_name)
    firestore_counts = col.document(st.secrets["fb_col"]).get().to_dict()
    # Update all fields in counts that appear in both counts and firestore_counts.
    if firestore_counts is not None:
        for key in firestore_counts:
            if key in counts:
                counts[key] = firestore_counts[key]


def save_new(counts, collection_name):
    """Save count data from `counts` to firestore."""
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    #creds = firestore.Client.from_service_account_json(key_dict)
    db = firestore.Client(credentials=creds, project="pvpogo")
    col = db.collection(collection_name)
    doc = col.document(st.secrets["fb_col"])
    doc.set(counts)  # creates if doesn't exist
    

col1,  col2,col3, col4 = st.columns([2,1,2,2])

def poke_search():
    if not st.session_state['last_sel']:
        st.session_state['last_sel'] = st.session_state.poke_choice
    else:
        st.session_state['last_sel'] = st.session_state.poke_choice
        
with col1:
    # UI for selecting name, attack2, defense2, hp2, level2
    load_new(streamlit_analytics.counts,st.secrets["fb_col"])
    streamlit_analytics.start_tracking()
    today = date.today()
    name2 = st.selectbox(label = today.strftime("%m/%d/%y"),options = df_stats['Name'],label_visibility = 'hidden',on_change = poke_search,key="poke_choice")

    streamlit_analytics.stop_tracking(unsafe_password=st.secrets['pass'])
    attack2 =st.slider('Attack IV', 0, 15, 15)
    defense2 = st.slider('Defense IV', 0, 15, 15)
    hp2 = st.slider('HP IV', 0, 15, 15)
    #level2 = st.slider('Select Level', 0, 51, 25)
    if st.button('Generate CP Table'):
        run_calc = True
        try:
            save_new(streamlit_analytics.counts,st.secrets["fb_col"])
            streamlit_analytics.stop_tracking(unsafe_password=st.secrets['pass'])
        except:
            pass
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

