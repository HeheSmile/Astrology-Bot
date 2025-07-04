import os 
import json 
import pandas as pd 

from dotenv import load_dotenv 
import google.generativeai as genai 
import streamlit as st

import datetime
now = datetime.datetime.now()

# -- UI ---
st.set_page_config(
    page_title="Personal Astrologer Chatbot",
    page_icon=":crystal_ball:",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Cleaning dataframe
@st.cache_data
def clean_dataframe(df):
    # Convert 'date' column to datetime and extract day of week, month, and year
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

    # Extracting day of week, month, and year from the date
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year

    # Delete the original 'date' column
    df.drop(columns=['date'], inplace=True)
    
    return df
df = pd.read_csv('./data/horoscope_saved.csv', index_col=0)

#setup api 
load_dotenv() 
api = st.secrets['api']['api-key'] # Gemini API Key
genai.configure(api_key=api)

#load config 

with open('config.json','r', encoding = 'utf-8') as f :
    config = json.load(f)
    functions = config.get('functions')
    initial_bot_message = config.get('initial_bot_message')

    bot_name = config.get('bot_name')
    bot_avt = config.get('bot_avt')

    user_avt = config.get('user_avt')

#Call LLM 
model = genai.GenerativeModel("gemini-1.5-flash")

#load dataframe zodiac
zodiac_df = df

import requests
def get_zodiac_daily(sign):
    api_url = f'https://api.api-ninjas.com/v1/horoscope?zodiac={sign}'
    response = requests.get(api_url, headers={'X-Api-Key': st.secrets['api']['horoscope-api-key']})
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        return {"error": response.status_code, "message": response.text}

genai.GenerativeModel("gemini-1.5-flash",
                            system_instruction=f"""
                                You are {bot_name}, a personal astrologer. You are an expert in astrology and horoscopes and you will help customers to 
                                answer their questions about zodiac signs, horoscopes, and astrology-related topics.
                                Act like a human astrologer, you will answer the questions in a friendly and helpful manner.
                                you will use the following data to answer the questions:{zodiac_df.to_json(orient='records')}.
                                if you don't know the answer, you will say "Tôi xin lỗi, tôi không biết câu trả lời cho câu hỏi này." 
                                Despite the questions being in English, you will always response in Vietnamese.
                                Provide the answer in a concise and clear manner, using simple language that is easy to understand.
                                Answer in one paragraph only, do not write too long.
                                Only one answer per question, do not write multiple answers.
                                Only answer questions related to astrology, zodiac signs, and horoscopes.
                                If the question is about today zodiac sign horoscope, you will use the get_zodiac_daily("the sign that user mentioned") function to get the horoscope for the zodiac sign.
                                If questions are not related to astrology, zodiac signs, or horoscopes, you will say "Tôi xin lỗi, tôi không thể trả lời câu hỏi này vì nó không liên quan đến chiêm tinh học, cung hoàng đạo hoặc tử vi."
                                    """)

#chatbot chatting function
def astrology_chatbot():
    st.title("Personal Astrologer Chatbot")
    st.write("Welcome to the Personal Astrologer Chatbot! Ask me anything about astrology, zodiac signs, and horoscopes. I will do my best to provide you with accurate and helpful information.")
    
    #History log
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", 
            "content": initial_bot_message,
            "avt": bot_avt}
        ]

    if 'bot_memory' not in st.session_state:
        st.session_state.bot_memory = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"], avatar =message["avt"]):
            st.write(message["content"])

    prompt = st.chat_input("Bạn cần hỏi gì về chiêm tinh? ")
    if prompt :
        st.session_state.chat_history.append(
            {"role": "user", 
            "content" : prompt,
            "avt" : user_avt,
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S") }
        )
        with st.chat_message("user", avatar = user_avt):
            st.markdown("You")
            st.write(prompt)
    
    # Call the model to get a response
        bot_response = model.generate_content(f"Tin nhắn trước: {st.session_state.bot_memory}, bạn cần trả lời: {prompt} (người dùng nhắn)").text
        print(st.session_state.bot_memory)

        st.session_state.chat_history.append(
                {"role": "assistant", 
                "content" : bot_response,
                "avt" : bot_avt,
                "datetime": now.strftime("%Y-%m-%d %H:%M:%S")}
        )
    
        with st.chat_message("assistant", avatar = bot_avt):
            st.markdown(bot_name)
            st.write(bot_response)

        st.session_state.bot_memory.append(f"{prompt} (người dùng nhắn)")
        st.session_state.bot_memory.append(f"{bot_response} (bot nhắn)")

    if st.session_state.chat_history:
        print(st.session_state.chat_history)

        # Save chat history to a file
        with open('./chat_history/chat_history.json', 'w', encoding='utf-8') as f:
            json.dump(st.session_state.chat_history, f, ensure_ascii=False, indent=4)

if __name__ == "__main__" :
    astrology_chatbot()

