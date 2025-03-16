import os
import streamlit as st
import openai
from openai import OpenAIError
from fpdf import FPDF

# ✅ Load OpenAI API Key securely
api_key = st.secrets.get("OPENAI_API_KEY")
if not api_key:
    st.error("⚠️ OpenAI API Key missing in Streamlit Secrets!")
    st.stop()

openai.api_key = api_key

# ✅ Configure Streamlit page
st.set_page_config(page_title="Wanderplan Travel Planner", layout="wide")

# Sidebar info
st.sidebar.title("ℹ️ About Wanderplan")
st.sidebar.info(
    "**Wanderplan**\n\n"
    "🔹 AI-powered travel plans using OpenAI.\n"
    "🔹 Detailed itineraries with food, sights & local tips.\n"
    "🔹 Multilingual support: Bengali, Hindi, Spanish...\n"
    "🔹 Downloadable as PDF with Unicode fonts.\n\n"
    "_Plan your perfect trip with AI!_"
)

# ✅ Generate detailed itinerary via OpenAI GPT
def generate_itinerary(location, days, month, budget, activities, travel_companion, language):
    activity_str = ", ".join(activities) if activities else "any"
    prompt = (
        f"Create a detailed and high-quality {days}-day travel itinerary for {location} in {month} for a {budget} budget. "
        f"Include well-planned morning, afternoon, and evening activities for each day. "
        f"Include top attractions, hidden gems, local experiences, and food recommendations for each meal. "
        f"Provide specific timings and helpful tips. "
        f"Focus on {activity_str} activities for someone traveling {travel_companion}. "
        f"Avoid showing prices. "
        f"Make the itinerary feel like a guidebook with immersive descriptions. "
        f"Respond in {language}."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,  # Increased for longer itineraries
            temperature=0.8
        )
        return response['choices'][0]['message']['content'].strip()
    except OpenAIError as e:
        st.error(f"⚠️ OpenAI API Error: {str(e)}")
        return None

# ✅ Create PDF with Unicode font for Bengali and more
def create_pdf(itinerary, location, days, month, language):
    pdf = FPDF()
    pdf.add_page()

    # Font selection for Bengali and others
    if language == "Bengali":
        font_path = "NotoSansBengali-Regular.ttf"
        font_name = "NotoBengali"
    else:
        font_path = "DejaVuSans.ttf"
        font_name = "DejaVu"

    if not os.path.exists(font_path):
        st.error(f"⚠️ Font file {font_path} not found in app directory.")
        return None

    pdf.add_font(font_name, '', font_path, uni=True)
    pdf.set_font(font_name, size=12)

    # Title
    pdf.set_font(font_name, 'B', 16)
    pdf.cell(200, 10, txt=f"{days}-Day Travel Itinerary for {location} in {month}", ln=True, align='C')
    pdf.ln(10)

    # Content
    pdf.set_font(font_name, size=12)
    pdf.multi_cell(0, 10, itinerary)

    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return pdf_bytes

# ✅ Main Streamlit App
def main():
    st.title("🌍 Wanderplan ✈️")
    st.subheader("Plan your perfect trip with AI!")

    if "itinerary" not in st.session_state:
        st.session_state["itinerary"] = None

    # Inputs
    location = st.text_input("📍 Enter the location:")
    days = st.number_input("📅 Number of days (1-7):", min_value=1, max_value=7, value=3)
    month = st.selectbox("🗓️ Month of travel:", 
                         ["January", "February", "March", "April", "May", "June", 
                          "July", "August", "September", "October", "November", "December"])
    budget = st.selectbox("💸 Budget:", ["Budget", "Mid-range", "Luxury"])
    activities = st.multiselect("🎯 Preferred activities:", 
                                ["Adventure", "Relaxation", "Cultural", "Sightseeing", "Food Tour"])
    travel_companion = st.selectbox("👥 Traveling with:", ["Solo", "Couple", "Family", "Friends"])
    language = st.selectbox("🌐 Language:", 
                            ["English", "Spanish", "French", "German", "Hindi", "Bengali"])

    # Generate Itinerary
    if st.button("🚀 Generate Itinerary"):
        if location.strip():
            st.session_state["itinerary"] = None
            with st.spinner("Generating your perfect itinerary..."):
                itinerary = generate_itinerary(location, days, month, budget, activities, travel_companion, language)
                if itinerary:
                    st.session_state["itinerary"] = itinerary
                    st.success("✅ Your itinerary is ready!")
                    st.markdown(itinerary)
        else:
            st.warning("⚠️ Please enter a valid location.")

    # Download PDF
    if st.session_state["itinerary"]:
        pdf_bytes = create_pdf(st.session_state["itinerary"], location, days, month, language)
        if pdf_bytes:
            st.download_button(
                label="📥 Download Itinerary as PDF",
                data=pdf_bytes,
                file_name=f"{location}_Travel_Itinerary.pdf",
                mime="application/pdf"
            )
    else:
        st.info("Generate your itinerary to enable PDF download.")

# ✅ Run the app
if __name__ == "__main__":
    main()
