import streamlit as st
from send_digest import (
    get_news,
    get_weather,
    get_calendar_events,
    get_quote,
    generate_summary,
)

# Streamlit page setup
st.set_page_config(
    page_title="Daily Digest AI",
    page_icon="🌅",
    layout="centered"
)

st.title("🌅 Daily Digest AI")
st.write("Generate your personalized daily summary instantly!")

# Inputs
name = st.text_input("Your Name", "Friend")
city = st.text_input("City", "Pune")

# Button to trigger digest
if st.button("Generate Digest"):
    with st.spinner("Fetching your daily updates..."):
        # Gather all the components
        news = get_news()
        weather = get_weather(city)
        calendar = get_calendar_events()
        quote = get_quote()

        # Create the digest
        digest = generate_summary(news, weather, calendar, quote, name=name)

    # Display the digest
    st.markdown("### 📜 Your Digest")
    st.markdown(digest)

    # Optional: Display each section in collapsible panels
    with st.expander("📰 News Headlines"):
        st.write(news if isinstance(news, list) else [news])

    with st.expander("🌤 Weather"):
        st.write(weather)

    with st.expander("📅 Calendar Events"):
        st.write(calendar if isinstance(calendar, list) else [calendar])

    with st.expander("💡 Quote of the Day"):
        st.write(quote)
