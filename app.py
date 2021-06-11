# Core Pkgs
import streamlit as st 
import streamlit.components.v1 as stc 
from aitextgen import aitextgen #for ai text gen

# EDA Pkgs
import pandas as pd 
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Utils
import sqlite3
import base64
import time 
timestr = time.strftime("%Y%m%d-%H%M%S")
import requests
from datetime import datetime

st.set_option('deprecation.showPyplotGlobalUse', False)
hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

@st.cache(hash_funcs={aitextgen: id})
def load_model():
    model = aitextgen(model="EleutherAI/gpt-neo-125M",to_gpu=True)
    return model
    
# Storage in A Database
conn = sqlite3.connect('data.db')
c = conn.cursor()
    
    # Create Fxn From SQL
def create_table():
	c.execute('CREATE TABLE IF NOT EXISTS TextTable(message TEXT,postdate DATE)')


def add_data(message,postdate):
    c.execute('INSERT INTO TextTable(message,postdate) VALUES (?,?)',(message,postdate))
    conn.commit()

def view_all_data():
	c.execute("SELECT * FROM TextTable")
	data = c.fetchall()
	return data

#loading the from the model from the funtion 
ai = load_model()

def main():
    menu = ["Home","Storage","About"]
    create_table()
    
    choice = st.sidebar.selectbox("Menu",menu)
    
    if choice == "Home":
        st.title("AI TEXT GENERATOR WEB APP")
        
        st.sidebar.subheader("Text Generator Tuning/Settings")
        max_length= st.sidebar.slider("Maximum length of the generated text ",100,2048)
        # no_repeat_ngram_size= st.sidebar.slider("Token length to avoid repeating given phrases. ",2,5)
        top_k= st.sidebar.slider(" limits the sampled tokens to the top k values ",1,100)
        temperature= st.sidebar.slider("Controls the craziness of the text ",0.7,100.0)
        
        with st.form(key='mlform'):
            col1,col2 = st.beta_columns([2,1])
            with col1:
                message = st.text_area("Type your Message...")
                submit_message = st.form_submit_button(label='Genrate Text')
                
            with col2:
                st.write("AI Text Sample (Copy)")
                st.write("This is just a POC and not for Commercial use yet but you are free to play around")
    
        if submit_message:
            with st.spinner("AI is at Work........"):
                # text generation
                gpt_text = ai.generate_one(prompt=message, do_sample=True, top_k=top_k, temperature=temperature,
                                            max_length=max_length,no_repeat_ngram_size=2
                                            )
                st.success("AI Successfully generated the below text and Data Submitted")
                postdate = datetime.now()
                # Add Data To Database
                add_data(message,postdate)
                
                res_col1 ,res_col2 = st.beta_columns(2)
                with res_col1:
                    st.subheader("Generated Text Visualization")
                    # Create and generate a word cloud image:
                    wordcloud = WordCloud().generate(gpt_text)
                    # Display the generated image:
                    plt.imshow(wordcloud, interpolation='bilinear')
                    plt.axis("off")
                    plt.show()
                    st.pyplot()
                    
                
                with res_col2:
                    st.subheader("Generated Text Output")
                    st.success("Generated Text")
                    st.write(gpt_text)

    
    
    elif choice == "Storage":
        st.title("Manage & Monitor Results")
        stored_data =  view_all_data() 
        new_df = pd.DataFrame(stored_data,columns=['message','postdate'])
        st.dataframe(new_df)
        new_df['postdate'] = pd.to_datetime(new_df['postdate'])
   
    
    else:
        st.subheader("About")
        # html_temp ="""<div>
        #          <p></p>
        #          <p></p>
        #          </div>"""
        # st.markdown(html_temp, unsafe_allow_html=True)
        


if __name__ == '__main__':
	main()
