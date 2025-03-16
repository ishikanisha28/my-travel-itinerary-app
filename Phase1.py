import os
import streamlit as st
import openai
from fpdf import FPDF
import unicodedata
import requests

# ✅ Setup OpenAI Client
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ✅ Set page configuration
st.set_page_config(page_title="Travel Itinerary Generator", layout="wide")

# ✅ Sidebar content
st.sidebar.title("ℹ️ About This App")
st.sidebar.info(
    "**Travel Itinerary Generator**\n\n"
    "🔹 Uses AI to create personalized travel plans.\n"
    "🔹 Generates detailed itineraries with food/activity recommendations.\n"
    "🔹 Download itineraries directly as PDF files.\n\n"
    "_Plan your perfect trip, in your preferred language!_"
)

# ✅ Function to download font if not present
def ensure_font(font_name, font_url):
    if not os.path.isfile(font_name):
        response = requests.get(font_url)
        with open(font_name, "wb") as f:
            f.write(response.content)

# ✅ Download DejaVuSans.ttf for multilingual support
dejavu_font = "DejaVuSans.ttf"
dejavu_url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
ensure_font(dejavu_font, dejavu_url)

# ✅ Generate itinerary with OpenAI
def generate_itinerary(location, days, month, budget, activities, travel_companion, language):
    activity_str = ", ".join(activities) if activities else "any"
    prompt = (
        f"Generate a {days}-day travel itinerary for {location} in {month} for a {budget} budget. "
        f"Focus on {activity_str} activities for someone traveling {travel_companion}. "
        f"Include morning, afternoon, and evening suggestions with food options. "
        f"Ensure popular and offbeat spots are covered with specific timings. Avoid prices. "
        f"Respond in {language}."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful travel planner."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"⚠️ OpenAI API Error: {e}")
        return None

# ✅ Function to remove non-ASCII characters (for font compatibility)
def remove_non_ascii(text):
    return unicodedata.normalize('NFKD', text).encode('latin-1', 'ignore').decode('latin-1')

# ✅ Create PDF using downloaded font
def create_pdf(itinerary, location, days, month, language):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", dejavu_font, uni=True)
    pdf.set_font("DejaVu", size=12)

    # ✅ Add title
    pdf.set_font("DejaVu", 'B', 16)
    title = f"{days}-Day Travel Itinerary for {location} in {month} ({language})"
    pdf.multi_cell(0, 10, title, align='C')
    pdf.ln(10)

    # ✅ Add itinerary
    pdf.set_font("DejaVu", size=12)
    itinerary_clean = remove_non_ascii(itinerary)
    pdf.multi_cell(0, 10, itinerary_clean)

    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return pdf_bytes

# ✅ Main App Logic
def main():
    st.title("🌍 Travel Itinerary Generator ✈️")
    st.subheader("Plan your dream trip with AI – in your language!")

    if "itinerary" not in st.session_state:
        st.session_state["itinerary"] = None

    location = st.text_input("📍 Enter the location:")
    days = st.number_input("📅 Number of days (1-7):", min_value=1, max_value=7, value=3)
    month = st.selectbox("🗓️ Travel month:", [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ])
    budget = st.selectbox("💸 Budget level:", ["Budget", "Mid-range", "Luxury"])
    activities = st.multiselect("🎯 Activities:", ["Adventure", "Relaxation", "Cultural", "Sightseeing", "Food Tour"])
    travel_companion = st.selectbox("👥 Traveling with:", ["Solo", "Couple", "Family", "Friends"])
    language = st.selectbox("🌐 Choose language:", ["English", "Spanish", "French", "German", "Bengali", "Hindi"])

    if st.button("🚀 Generate Itinerary"):
        if location.strip():
            st.session_state["itinerary"] = None
            itinerary = generate_itinerary(location, days, month, budget, activities, travel_companion, language)
            if itinerary:
                st.session_state["itinerary"] = itinerary
                st.success("✅ Your itinerary:")
                st.markdown(itinerary)
        else:
            st.warning("⚠️ Enter a valid location.")

    if st.session_state["itinerary"]:
        pdf_bytes = create_pdf(st.session_state["itinerary"], location, days, month, language)
        st.download_button(
            label="📥 Download Itinerary as PDF",
            data=pdf_bytes,
            file_name=f"{location}_Itinerary.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    main()
