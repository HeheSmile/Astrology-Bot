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
    page_icon=":crystal_ball:"
)

# Cleaning dataframe
# @st.cache_data
df = pd.read_csv('./data/horoscope_saved.csv')
# Convert 'date' column to datetime and extract day of week, month, and year
df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

df.isna().sum()  # Check for missing values
df.nunique()  # Check for unique values in each column

# Extracting day of week, month, and year from the date
df['day_of_week'] = df['date'].dt.dayofweek
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year
df.to_json(orient='records')

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

#load dataframe zodiac
zodiac_df = df

import requests
def get_zodiac_daily(sign):
    api_url = f'https://api.api-ninjas.com/v1/horoscope?zodiac={sign}'
    response = requests.get(api_url, headers={'X-Api-Key': st.secrets['api']['horoscope-api-key']})
    if response.status_code == requests.codes.ok:
        return response.json().get('horoscope')
    else:
        return {"error": response.status_code, "message": response.text}
    
    
def get_zodiac_related_ideas(user_query, df, top_n=10):
    zodiac_signs = [
        "aries", "taurus", "gemini", "cancer", "leo", "virgo",
        "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
    ]
    
    # Match signs from the query
    found_signs = [sign for sign in zodiac_signs if sign in user_query.lower()]
    
    # Filter by sign if any found
    filtered_df = df[df["sign"].isin(found_signs)] if found_signs else df

    # Rank by how many words from the query appear in the horoscope
    user_words = set(user_query.lower().split())
    filtered_df["score"] = filtered_df["horoscope"].apply(
        lambda h: sum(word in h.lower() for word in user_words)
    )

    # Get top N results
    top_results = filtered_df.sort_values(by="score", ascending=False).head(top_n)
    return top_results[["sign", "date", "horoscope"]].reset_index(drop=True)
# Test the fallback function



model = genai.GenerativeModel("gemini-1.5-flash",
                            system_instruction=f"""
                                You are {bot_name}, a personal astrologer. You are an expert in astrology and horoscopes and you will help customers to 
                                answer their questions about zodiac signs, horoscopes, and astrology-related topics.
                                Act like a human astrologer, you will answer the questions in a friendly and helpful manner.
                                Despite the questions being in English, you will always response in Vietnamese.
                                Provide the answer in a concise and clear manner, using simple language that is easy to understand.
                                Answer in one paragraph only, do not write too long.
                                Only one answer per question, do not write multiple answers.
                                Diversify your answers, do not repeat the same answer.
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
            "avt": bot_avt,
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S")}
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

