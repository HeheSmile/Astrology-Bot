import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
from datetime import datetime

st.set_page_config(
    page_title="Personal Astrologer Chatbot",
    page_icon=":crystal_ball:",
    layout="wide",
    initial_sidebar_state="expanded"
)

compatibility = st.secrets['compatibility_data']
compatibility_data = {sign: list(map(int, compatibility[sign])) for sign in compatibility}
zodiac_list = list(compatibility_data.keys())

def get_matching_zodiac(birthdate: str):
    date = datetime.strptime(birthdate, '%Y-%m-%d')
    day, month = date.day, date.month
    signs =[
        (1, 20, 'capricorn'), (2, 19, 'aquarius'), (3, 20, 'pisces'),
        (4, 20, 'aries'), (5, 21, 'taurus'), (6, 21, 'gemini'),
        (7, 23, 'cancer'), (8, 23, 'leo'), (9, 23, 'virgo'),
        (10, 23, 'libra'), (11, 22, 'scorpio'), (12, 22, 'sagittarius'),
        (12, 31, 'capricorn')
    ]
    for m, d, sign in signs:
        if month == m and day <= d:
            return sign
    return zodiac_list[0]  # Default to Capricorn if no match found

def find_match(sign):
    df = pd.DataFrame(compatibility_data).T
    kmeans = KMeans(n_clusters=4, n_init=10, random_state=42)
    df["cluster"] = kmeans.fit_predict(df.iloc[:, :12])
    user_cluster = df.loc[sign]["cluster"]
    possible = df[df["cluster"] == user_cluster].drop(index=sign)
    match = possible.mean(axis=1).idxmax()
    return match


#----UI----
st.title("💘 Zodiac Matchmaker")
st.markdown("Find your cosmic compatibility based on your sign, birthday, and the stars!")

with st.sidebar:
    st.subheader("Navigation")
    # Add links to other pages
    st.page_link("Home.py", label="Chat Bot", icon="🤖")
    st.page_link("pages/Match.py", label="Matching", icon="💞")

with st.form("zodiac_form"):
    gender = st.selectbox("Your Gender", ["Male", "Female", "Other"])
    birthdate = st.date_input("Your Birthdate")
    sign_input = st.selectbox("Your Zodiac Sign", ["Auto Detect from Birthday"] + [z.capitalize() for z in zodiac_list])
    submitted = st.form_submit_button("Find My Match 💞")

if submitted:
    bdate_str = birthdate.strftime("%Y-%m-%d")

    if sign_input == "Auto Detect from Birthday":
        user_sign = find_match(bdate_str)
        print(user_sign)
        st.write(f"🪐 Detected Zodiac Sign: **{user_sign.capitalize()}**")
        
    else:
        user_sign = sign_input.lower()

    best_match = find_match(user_sign)
    st.success(f"💘 Best Match for **{user_sign.capitalize()}** ({gender}) is **{best_match.capitalize()}**!")
    st.balloons()
