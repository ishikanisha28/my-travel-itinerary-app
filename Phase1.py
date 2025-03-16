import streamlit as st
import openai
from fpdf import FPDF
import unicodedata
import os

# ✅ OpenAI v1.66.3 API Key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ✅ Streamlit Page Config
st.set_page_config(page_title="Travel Itinerary Generator", layout="wide")

# ✅ Sidebar Info
st.sidebar.title("ℹ️ About This App")
st.sidebar.info(
    "**Travel Itinerary Generator**\n\n"
    "🔹 Powered by GPT-4 Turbo\n"
    "🔹 Custom itineraries in your preferred language\n"
    "🔹 Download itineraries as PDF (no font errors!)\n\n"
    "_Plan your perfect trip with ease!_"
)

# ✅ Generate Itinerary with Language
def generate_itinerary(location, days, month, budget, activities, travel_companion, language):
    activity_str = ", ".join(activities) if activities else "any"
    prompt = (
        f"Create a detailed {days}-day travel itinerary for {location} in {month}. "
        f"Budget: {budget}. Preferred activities: {activity_str}. "
        f"Traveling with: {travel_companion}. "
        f"Language: {language}. "
        "Include morning, afternoon, and evening plans with times and local food suggestions. "
        "Cover both popular and offbeat places. Format it day-wise, use bullet points. No prices."
    )
    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful and expert travel planner."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"⚠️ OpenAI API Error: {str(e)}")
        return None

# ✅ PDF Creation with Unicode Font
def create_pdf(itinerary, location, days, month):
    pdf = FPDF()
    pdf.add_page()

    # ✅ Add Unicode Font (DejaVuSans.ttf)
    font_path = "DejaVuSans.ttf"
    if os.path.exists(font_path):
        pdf.add_font("DejaVu", '', font_path, uni=True)
        pdf.set_font("DejaVu", '', 14)
    else:
        st.warning("⚠️ Font file DejaVuSans.ttf not found. Using Arial as fallback.")
        pdf.set_font("Arial", size=12)

    # ✅ Add Title
    pdf.set_font_size(16)
    pdf.cell(200, 10, txt=f"{days}-Day Itinerary for {location} ({month})", ln=True, align='C')
    pdf.ln(10)

    # ✅ Add Itinerary Content
    pdf.set_font_size(12)
    pdf.multi_cell(0, 10, itinerary)

    return pdf.output(dest='S').encode('latin-1', 'ignore')

# ✅ Main App Logic
def main():
    st.title("🌍 Travel Itinerary Generator ✈️")
    st.subheader("Plan your dream trip in any language!")

    if "itinerary" not in st.session_state:
        st.session_state["itinerary"] = None

    location = st.text_input("📍 Destination:")
    days = st.number_input("📅 Trip Length (1-7 days):", min_value=1, max_value=7, value=3)
    month = st.selectbox("🗓️ Travel Month:",
                         ["January", "February", "March", "April", "May", "June",
                          "July", "August", "September", "October", "November", "December"])
    budget = st.selectbox("💸 Budget Level:", ["Budget", "Mid-range", "Luxury"])
    activities = st.multiselect("🎯 Preferred Activities:",
                                ["Adventure", "Relaxation", "Cultural", "Sightseeing", "Food Tour"])
    travel_companion = st.selectbox("👥 Traveling With:", ["Solo", "Couple", "Family", "Friends"])
    language = st.selectbox("🌐 Language:",
                            ["English", "Spanish", "French", "German", "Hindi", "Bengali", "Chinese", "Japanese"])

    if st.button("🚀 Generate Itinerary"):
        if location.strip():
            st.session_state["itinerary"] = None
            itinerary = generate_itinerary(location, days, month, budget, activities, travel_companion, language)
            if itinerary:
                st.session_state["itinerary"] = itinerary
                st.success("✅ Your itinerary is ready!")
                st.markdown(itinerary)
        else:
            st.warning("⚠️ Please enter a valid destination.")

    if st.session_state["itinerary"]:
        pdf_bytes = create_pdf(st.session_state["itinerary"], location, days, month)
        st.download_button("📥 Download PDF", data=pdf_bytes,
                           file_name=f"{location}_Itinerary.pdf", mime="application/pdf")

# ✅ Run the App
if __name__ == "__main__":
    main()
