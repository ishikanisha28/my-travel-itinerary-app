import os
import streamlit as st
import openai
from fpdf import FPDF
import unicodedata

# ✅ Fetch OpenAI API Key from environment variable
api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error("⚠️ ERROR: OpenAI API Key is missing or not set properly in Secrets!")
    st.stop()

# ✅ Set OpenAI API Key properly
openai.api_key = api_key

# ✅ Set page configuration
st.set_page_config(page_title="Travel Itinerary Generator", layout="wide")

# ✅ Function to generate itinerary using OpenAI API with custom options
def generate_itinerary(location, days, month, budget, activities, travel_companion):
    activity_str = ", ".join(activities) if activities else "any"
    prompt = (
        f"Generate a {days}-day travel itinerary for {location} in {month} for a {budget} budget. "
        f"Focus on {activity_str} activities for someone traveling {travel_companion}. "
        "Include morning, afternoon, and evening suggestions with food options. "
        "Ensure popular and offbeat spots are covered with specific timings. "
        "Avoid displaying prices."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Change to "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        # ✅ Correct way to access response content
        return response.choices[0].message.content
    except openai.error.OpenAIError as e:
        st.error(f"⚠️ OpenAI API Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"⚠️ Unexpected Error: {str(e)}")
        return None

# ✅ Function to create PDF
def create_pdf(itinerary, location, days, month):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"{days}-Day Travel Itinerary for {location} in {month}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, itinerary)
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return pdf_bytes

# ✅ Main application logic
def main():
    st.title("🌍 Travel Itinerary Generator ✈️")
    st.subheader("Plan your perfect trip with AI!")

    location = st.text_input("📍 Enter the location:")
    days = st.number_input("📅 Enter the number of days (1-7):", min_value=1, max_value=7, value=2)
    month = st.selectbox("🗓️ Select the month of your trip:", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
    budget = st.selectbox("💸 Choose your budget level:", ["Budget", "Mid-range", "Luxury"])
    activities = st.multiselect("🎯 Choose activities you like:", ["Adventure", "Relaxation", "Cultural", "Sightseeing", "Food Tour"])
    travel_companion = st.selectbox("👥 Who are you traveling with?", ["Solo", "Couple", "Family", "Friends"])

    if st.button("🚀 Generate Itinerary"):
        if location.strip():
            itinerary = generate_itinerary(location, days, month, budget, activities, travel_companion)
            if itinerary:
                st.success("✅ Here is your itinerary:")
                st.markdown(itinerary)
                pdf_bytes = create_pdf(itinerary, location, days, month)
                st.download_button(
                    label="📥 Download Itinerary as PDF",
                    data=pdf_bytes,
                    file_name=f"{location}_Travel_Itinerary.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("⚠️ Please enter a valid location.")

if __name__ == "__main__":
    main()
