import os
import streamlit as st
import openai
from openai import OpenAIError  # ✅ Error handling
from fpdf import FPDF

# ✅ Load OpenAI API Key from Streamlit secrets
api_key = st.secrets.get("OPENAI_API_KEY")
if not api_key:
    st.error("⚠️ OpenAI API Key missing in Streamlit Secrets!")
    st.stop()

openai.api_key = api_key

# ✅ Streamlit page settings
st.set_page_config(page_title="Wanderplan Travel Planner", layout="wide")

# Sidebar info
st.sidebar.title("ℹ️ About Wanderplan")
st.sidebar.info(
    "**Wanderplan**\n\n"
    "🔹 AI-powered travel plans using OpenAI.\n"
    "🔹 Detailed itineraries with activity and food options.\n"
    "🔹 Multilingual support (English, Hindi, Bengali...)\n"
    "🔹 Downloadable as PDF with Unicode fonts.\n"
    "_Plan your perfect trip effortlessly!_"
)

# ✅ Generate itinerary via OpenAI
def generate_itinerary(location, days, month, budget, activities, travel_companion, language):
    activity_str = ", ".join(activities) if activities else "any"
    prompt = (
        f"Generate a {days}-day travel itinerary for {location} in {month} for a {budget} budget. "
        f"Focus on {activity_str} activities for someone traveling {travel_companion}. "
        f"Include morning, afternoon, and evening suggestions with food options. "
        f"Cover popular and offbeat spots with specific timings. Avoid showing prices. "
        f"Respond in {language}."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except OpenAIError as e:
        st.error(f"⚠️ OpenAI API Error: {str(e)}")
        return None

# ✅ Create PDF with Unicode font support
def create_pdf(itinerary, location, days, month, language):
    pdf = FPDF()
    pdf.add_page()

    # Font selection for Bengali vs others
    if language == "Bengali":
        font_path = "NotoSansBengali-Regular.ttf"
        font_name = "NotoBengali"
    else:
        font_path = "DejaVuSans.ttf"
        font_name = "DejaVu"

    if not os.path.exists(font_path):
        st.error(f"⚠️ Font file {font_path} not found.")
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

    # Input fields
    location = st.text_input("📍 Enter the location:")
    days = st.number_input("📅 Number of days (1-7):", min_value=1, max_value=7, value=2)
    month = st.selectbox("🗓️ Select the month:", 
                         ["January", "February", "March", "April", "May", "June", 
                          "July", "August", "September", "October", "November", "December"])
    budget = st.selectbox("💸 Budget level:", ["Budget", "Mid-range", "Luxury"])
    activities = st.multiselect("🎯 Activities you like:", 
                                ["Adventure", "Relaxation", "Cultural", "Sightseeing", "Food Tour"])
    travel_companion = st.selectbox("👥 Traveling with:", ["Solo", "Couple", "Family", "Friends"])
    language = st.selectbox("🌐 Itinerary language:", 
                            ["English", "Spanish", "French", "German", "Hindi", "Bengali"])

    # Generate itinerary
    if st.button("🚀 Generate Itinerary"):
        if location.strip():
            st.session_state["itinerary"] = None
            with st.spinner("Generating your itinerary..."):
                itinerary = generate_itinerary(location, days, month, budget, activities, travel_companion, language)
                if itinerary:
                    st.session_state["itinerary"] = itinerary
                    st.success("✅ Your itinerary:")
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
        st.info("Generate an itinerary to enable PDF download.")

# Run the app
if __name__ == "__main__":
    main()
