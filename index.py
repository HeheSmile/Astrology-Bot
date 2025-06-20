import os 
import json 
import pandas as pd 

from dotenv import load_dotenv 
import google.generativeai as genai 
import streamlit as st 

# Cleaning dataframe
df = pd.read_csv('./data/horoscope_saved.csv', index_col=0)

# Convert 'date' column to datetime and extract day of week, month, and year
df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

# Extracting day of week, month, and year from the date
df['day_of_week'] = df['date'].dt.dayofweek
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year

# Delete the original 'date' column
df.drop(columns=['date'], inplace=True)
print(df.head())
print(df.nunique())
print(df.isna().sum())

#setup api 
load_dotenv() 
google_api_key = os.getenv("GOOGLE_API_KEY") # Gemini API Key
genai.configure(api_key=google_api_key)



#load config 

with open('config.json','r') as f :
    config = json.load(f)
    functions = config.get('functions')
    initial_bot_message = config.get('bot_initial_message')

    bot_name = config.get('bot_name')
    bot_avt = config.get('bot_avt')

    user_avt = config.get('user_avt')


#load dataframe zodiac
zodiac_df = df

#Call LLM 
model = genai.GenerativeModel("gemini-1.5-flash")
    
genai.GenerativeModel("gemini-1.5-flash",
                            system_instruction=f"""
                                You are {bot_name}, a personal astrologer. You are an expert in astrology and horoscopes and you will help customers to 
                                answer their questions about zodiac signs, horoscopes, and astrology-related topics.
                                you will use the following data to answer the questions:{zodiac_df.to_json(orient='records')}
                                you will also use the following functions to answer the questions: {functions}
                                you will always respond in Vietnamese.
                                if you don't know the answer, you will say "Tôi xin lỗi, tôi không biết câu trả lời cho câu hỏi này"
                                if the user asks for a horoscope, you will use the data provided to generate a horoscope for the user.
                                if the user asks for a zodiac sign, you will use the data provided to generate information
                                about the zodiac sign.
                                if the user asks for a birthday horoscope, you will use the data provided to generate a horoscope for the user's birthday.
                                if the user asks for a daily horoscope, you will use the data provided to generate a horoscope for the current day.
                                if the user asks for a weekly horoscope, you will use the data provided to generate a horoscope for the current week.
                                if the user asks about their zodiac sign, you will use the data provided to generate information about their zodiac sign.
                                if the user asks about their zodiac sign, and what will happen today base on their zodiac sign, you will get today's date 
                                and use the data provided to generate a horoscope for the current day.
                                Bạn cần trả lời tin nhắn mới nhất và sử dụng những tin nhắn trước làm trí nhớ của mình
                                Hãy trả lời người dùng bằng tiếng Việt sao cho dễ hiểu,kèm theo ví dụ thực tế có liên quan.
                                    """)

#chatbot chatting function
def astrology_chatbot():
    st.title("Personal Astrologer Chatbot")
    st.subheader("Hỏi về chiêm tinh, cung hoàng đạo, tử vi, v.v.")
    st.write("Chào mừng bạn đến với ZodiacBot! Tôi có thể giúp bạn với các câu hỏi về chiêm tinh và cung hoàng đạo. Hãy hỏi tôi bất cứ điều gì!")
    
    #History log
    if "history" not in st.session_state:
        st.session_state.history = [
            {"role": "assistant", 
            "content" : initial_bot_message,
            "avt" : bot_avt,}
        ]
    
    if 'bot_memory' not in st.session_state:
        st.session_state.bot_memory = []
    
    # Display chat history
    for message in st.session_state.history:
        with st.chat_message(message["role"], avatar =message["avt"]):
            st.write(message["content"])

    prompt = st.chat_input("Bạn cần hỏi gì về chiêm tinh? ")
    if prompt :
        st.session_state.history.append(
            {"role": "user", 
            "content" : prompt,
            "avt" : user_avt,}
        )
        with st.chat_message("user", avatar = user_avt):
            st.markdown("You")
            st.write(prompt)
    
    # Call the model to get a response
        bot_res = model.generate_content(f"Tin nhắn trước: {st.session_state.bot_memory}, bạn cần trả lời: {prompt} (người dùng nhắn)").text
        print(st.session_state.bot_memory)

        st.session_state.history.append(
                {"role": "assistant", 
                "content" : bot_res,
                "avt" : bot_avt,}
        )
    
        with st.chat_message("assistant", avatar = bot_avt):
            st.markdown(bot_name)
            st.write(bot_res)

        st.session_state.bot_memory.append(f"{prompt} (người dùng nhắn)")
        st.session_state.bot_memory.append(f"{bot_res} (bot nhắn)")

if __name__ == "__main__" :
    astrology_chatbot()