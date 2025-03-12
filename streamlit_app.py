#Streamlit hotel reommendation web interface

import streamlit as st
import numpy as np
import pandas as pd
import spacy
from string import punctuation, whitespace
from spacy.lang.en import STOP_WORDS
from spacy.tokens import Token
import time

#Load hotel data
@st.cache_data
def load_data():
    df = pd.read_csv('hoteldata/hotel_summary.csv')
    return df

df = load_data()

#load spacy data containing word vectors
nlp = spacy.load('en_core_web_md')

#Preprocess text by tokenizing, removing stopwords, lematizing and extracting keywords
def pre_process(document):
    from afinn import Afinn
    afinn = Afinn()
  
    hotel_names = set(df.Hotel_name)
    states = set(df.State).union({'nigeria', 'etc','km'})
    stopwords = STOP_WORDS.union(set(punctuation), set(whitespace), hotel_names, states)
    
    # Getter function to determine the value of token._.is_excluded
    def get_is_excluded(token):
        return token.text in stopwords

    Token.set_extension('is_excluded', getter=get_is_excluded, force=True)
    
    document = document.lower()
    doc = nlp(document)
    
    text = [token.lemma_ for token in doc if not token._.is_excluded and not token.is_oov]

    return nlp(" ".join(set(text)))

#Recommeder engine
def recommend(location, description):
    desc_doc = pre_process(description)
    review_doc = df[df['State'] == location]['Hotel_summary']
    similarity = [(review_doc.index[i], desc_doc.similarity(nlp(review_doc[review_doc.index[i]])))
                  for i in range(len(review_doc.index))]

    r_df = {'Hotel Name':[], 'Address':[], 'Score':[]}

    #Executes if number of hotels in the location exceeds 5  
    if len(similarity) > 5:
        top_5 = sorted(similarity, key=lambda x: x[1], reverse=True)[:5]
        for i in range(5):
            r_df['Hotel Name'].append(df.iloc[top_5[i][0]][['Hotel_name']][0].title())
            r_df['Address'].append(df.iloc[top_5[i][0]][['Address']][0].title())
            r_df['Score'].append(round(top_5[i][1],3))

    #Executes if number of hotels in the location is 1                
    elif len(similarity) == 1:
        r_df['Hotel Name'].append(df.iloc[similarity[0][0]][['Hotel_name']][0].title())
        r_df['Address'].append(df.iloc[similarity[0][0]][['Address']][0].title())
        r_df['Score'].append(round(similarity[0][1],3))
        
    else:
        for i in range(len(similarity)):
            r_df['Hotel Name'].append(df.iloc[similarity[i][0]][['Hotel_name']][0].title())
            r_df['Address'].append(df.iloc[similarity[i][0]][['Address']][0].title())
            r_df['Score'].append(round(similarity[i][1],3))

    index = list(range(1,len(r_df['Hotel Name'])+1))
    return pd.DataFrame(r_df, index=index)

def main():
    """
    Steamlit app
    """
    
    """
    # HOTEL RECOMMENDER SYSTEM
    
    One of the first things to do while planning a trip is to book comfortable accommodation. Booking a hotel
    online can be an overwhelming task with thousands of hotels to choose from for every destination.
    This system recommends hotels to a user based on their hotel description.
    """
    st.subheader('Which Nigerian state are you visiting?')
    option = st.selectbox(
        '',
        list((map(str.title, sorted(df['State'].unique())))))
        
    'You selected: ', option
    
    st.subheader(" Hotel Description")
    user_input = st.text_area("")

    left_column, right_column = st.columns(2)
    pressed = left_column.button('Press me?')
    if pressed:
        if user_input == "":
            right_column.subheader("You've not described your preferred hotel.")
        else:
            # Add a progress bar
            latest_iteration = st.empty()
            bar = st.progress(0)
            recommendations = recommend(option.lower(), user_input)
            for i in range(100):
                # Update the progress bar with each iteration.
                latest_iteration.text(f'{i+1}%')
                bar.progress(i + 1)
                time.sleep(0.0001)
            """
            # Top Recommendations
            """
            st.write(recommendations)

if __name__ == '__main__':
    main()