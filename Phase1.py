import os
import streamlit as st
import openai
from fpdf import FPDF
import unicodedata

# ✅ Set up OpenAI client for version 1.66.3
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ✅ Set page config
st.set_page_config(page_title="Travel Itinerary Planner", layout="wide")

# ✅ Sidebar info
st.sidebar.title("ℹ️ About This App")
st.sidebar.info(
    "**Travel Planner**\n\n"
    "🔹 Generate personalized travel itineraries.\n"
    "🔹 Supports different languages.\n"
    "🔹 Download itinerary as PDF.\n\n"
    "_Plan smart. Travel better!_"
)

# ✅ Itinerary generation using OpenAI Chat API (v1.66.3 compatible)
def generate_itinerary(location, days, month, budget, activities, travel_companion, language):
    activity_str = ", ".join(activities) if activities else "any"
    prompt = (
        f"Generate a {days}-day travel itinerary for {location} in {month} for a {budget} budget. "
        f"Focus on {activity_str} activities for someone traveling {travel_companion}. "
        "Include morning, afternoon, and evening suggestions with food options. "
        f"Ensure both popular and hidden spots are included. Avoid prices. Respond in {language}."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful and detail-oriented travel planner."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"⚠️ OpenAI API Error: {str(e)}")
        return None

# ✅ Remove non-ASCII (for PDF generation)
def remove_non_ascii(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

# ✅ Create PDF with font handling
def create_pdf(itinerary, location, days, month, language):
    pdf = FPDF()
    pdf.add_page()

    font_name = "DejaVu"
    font_path = "DejaVuSans.ttf"  # Make sure this file exists in the same directory

    if os.path.exists(font_path):
        try:
            pdf.add_font(font_name, '', font_path, uni=True)
            pdf.set_font(font_name, size=12)
        except Exception as e:
            st.warning(f"⚠️ Font load error: {str(e)}. Using default font.")
            pdf.set_font("Arial", size=12)
    else:
        st.warning("⚠️ Font file DejaVuSans.ttf not found. Using default font.")
        pdf.set_font("Arial", size=12)

    # Title
    pdf.set_font(font_name if font_name in pdf.fonts else "Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"{days}-Day Travel Itinerary for {location} ({month})", ln=True, align='C')
    pdf.ln(10)

    # Itinerary text
    itinerary_clean = remove_non_ascii(itinerary) if font_name not in pdf.fonts else itinerary
    pdf.set_font(font_name if font_name in pdf.fonts else "Arial", size=12)
    pdf.multi_cell(0, 10, itinerary_clean)

    return pdf.output(dest='S').encode('latin-1')

# ✅ Streamlit main app
def main():
    st.title("🌍 Travel Itinerary Planner ✈️")
    st.subheader("Plan smarter with AI!")

    if "itinerary" not in st.session_state:
        st.session_state["itinerary"] = None

    location = st.text_input("📍 Destination:")
    days = st.number_input("📅 Number of days (1-7):", min_value=1, max_value=7, value=3)
    month = st.selectbox("🗓️ Travel Month:", 
        ["January", "February", "March", "April", "May", "June",
         "July", "August", "September", "October", "November", "December"]
    )
    budget = st.selectbox("💰 Budget:", ["Budget", "Mid-range", "Luxury"])
    activities = st.multiselect("🎯 Interests:", 
        ["Adventure", "Relaxation", "Cultural", "Sightseeing", "Food Tour"])
    travel_companion = st.selectbox("👥 Who are you traveling with?", ["Solo", "Couple", "Family", "Friends"])
    language = st.selectbox("🌐 Language:", ["English", "Spanish", "French", "German", "Hindi"])

    if st.button("🚀 Generate Itinerary"):
        if location.strip():
            st.session_state["itinerary"] = None
            itinerary = generate_itinerary(location, days, month, budget, activities, travel_companion, language)
            if itinerary:
                st.session_state["itinerary"] = itinerary
                st.success("✅ Your itinerary is ready!")
                st.markdown(itinerary)
        else:
            st.warning("⚠️ Please enter a destination.")

    if st.session_state["itinerary"]:
        pdf_bytes = create_pdf(st.session_state["itinerary"], location, days, month, language)
        st.download_button(
            label="📥 Download as PDF",
            data=pdf_bytes,
            file_name=f"{location}_Itinerary.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    main()
