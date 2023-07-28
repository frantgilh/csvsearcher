import streamlit as st
import pandas as pd
import numpy as np
import pickle
from pandas.api.types import is_numeric_dtype,is_datetime64_any_dtype

st.set_page_config(
    page_title="CSV Search",
    layout="wide",
)


CHUNKSIZE = 10000

#@st.cache_data
def read_pickle(pkl = 'wizard.pkl'):
    file = open(pkl, 'rb')
    wzrd = pickle.load(file)
    file.close()
    return wzrd

def write_pickle(wzrd,pkl='wizard.pkl'):
    file = open(pkl, 'wb')
    pickle.dump(wzrd, file)
    file.close()
    


def search(filename,filetype,filtercol,filtertype,filterparams):
    
    filtered_rows = []
    
    if filetype == 'csv':
        reader = pd.read_csv(filename, parse_dates=True,chunksize=CHUNKSIZE,on_bad_lines='skip', encoding= 'unicode_escape')
    else:
        reader = pd.read_excel(filename, parse_dates=True,chunksize=CHUNKSIZE,on_bad_lines='skip', encoding= 'unicode_escape')
       
    for chunk in reader:
        if filtertype == "Contains":
            filtered_chunk = chunk[chunk[filtercol].str.contains(filterparams, case=False)]
        elif filtertype == "Not Contains":
            filtered_chunk = chunk[~chunk[filtercol].str.contains(filterparams, case=False)]            
        elif filtertype == "Equal":
            filtered_chunk = chunk[chunk[filtercol] == filterparams] 
        elif filtertype == "Not Equal":
            filtered_chunk = chunk[chunk[filtercol] != filterparams]             
        elif filtertype == "Higher Than":
            filtered_chunk = chunk[chunk[filtercol] > filterparams]  
        elif filtertype == "Lower Than":
            filtered_chunk = chunk[chunk[filtercol] < filterparams]              
        elif filtertype == "Between":
            filtered_chunk = chunk[chunk[filtercol].between(filterparams[0],filterparams[1])]                                       
        else:
            print('filtername not determined!')
        filtered_rows.append(filtered_chunk)
    

    filtered_df = pd.concat(filtered_rows)
    filtered_df.to_csv(f"output_{filename.split('.')[-2]}_{filtercol}_{filtertype}_{filterparams}.csv")
        

dtread = False    
sdbar = st.sidebar
sdbar.title('Filtering Area')

    
file_name = st.text_input(
        'Please Type File Location',
        placeholder = 'foldername/filename.csv'
    )

if file_name.split('.')[-1] in (['csv','txt']):
    data = pd.read_csv(file_name,parse_dates=True, on_bad_lines='skip',nrows = 50, encoding= 'unicode_escape')
    filetype = 'csv'
    dtread = True
elif file_name.split('.')[-1] in (['xls','xlsx']):
    data = pd.read_excel(file_name, parse_dates=True,nrows = 50,on_bad_lines='skip', encoding= 'unicode_escape')
    filetype = 'excel'
    dtread = True
else:
    st.warning('Please Type a valid data', icon='⚠️')
    

if dtread:
    st.title('Selected Data')    
    st.dataframe(data) 


if dtread:
    
    sdbar.subheader('Columns')
    col = sdbar.selectbox('Please Select The Colum to Filter ',data.columns,format_func=lambda x: f"""{x} ({str(data[x].dtype.type).split("'")[1]})""")
    filterchs = False
    if is_numeric_dtype(data[col]):
        filtertype = sdbar.selectbox('Please Select The Filter',('Higher Than','Lower Than','Between','Equal','Not Equal'))
        if filtertype == 'Between':
            c1,c2 = sdbar.columns(2)
            lowerbound = c1.number_input('Please Type lower Bound')
            upperbound = c2.number_input('Please Type Upper Bound')  
            if upperbound < lowerbound:
                sdbar.warning('Please Type a valid range', icon='⚠️')
            else:
                if sdbar.button('Search',key='numerfilterbetween'):
                    search(file_name,filetype,col,filtertype,[lowerbound,upperbound])
        else:
            filternumber = sdbar.number_input('Insert a number')
            if sdbar.button('Search',key='numerfilter'):
                search(file_name,filetype,col,filtertype,filternumber)           
    else: 
        filtertype = sdbar.selectbox('Please Select The Filter',('Contains','Not Contains','Equal','Not Equal'))
        filtertext = sdbar.text_input('Please Type Filter String')
        if sdbar.button('Search',key = 'filterstring'):
            search(file_name,filetype,col,filtertype,filtertext)
        
    
