import streamlit as st
import openai
from fpdf import FPDF
import unicodedata

# ✅ Correct OpenAI Client Initialization (v1.66.3+)
client = openai.Client(api_key=st.secrets["OPENAI_API_KEY"])

# ✅ Set page configuration
st.set_page_config(page_title="Travel Itinerary Generator", layout="wide")

# ✅ Sidebar content
st.sidebar.title("ℹ️ About This Program")
st.sidebar.info(
    "**Travel Itinerary Generator**\n\n"
    "🔹 Uses AI (GPT-4 Turbo) to create personalized travel plans.\n"
    "🔹 Detailed activities, food recommendations, offbeat spots.\n"
    "🔹 Download as PDF – no font errors!\n\n"
    "_Plan your dream trip effortlessly!_"
)

# ✅ Function to generate itinerary using OpenAI API (GPT-4 Turbo)
def generate_itinerary(location, days, month, budget, activities, travel_companion):
    activity_str = ", ".join(activities) if activities else "any"
    prompt = (
        f"Create a detailed {days}-day travel itinerary for {location} in {month}. "
        f"Budget level: {budget}. Preferred activities: {activity_str}. "
        f"Traveler type: {travel_companion}. "
        "Include morning, afternoon, and evening plans with specific times and local food suggestions. "
        "Mix popular and offbeat places. Format it with day-wise headings, bullet points, and no prices."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an expert travel planner who creates structured and engaging itineraries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"⚠️ Error generating itinerary: {str(e)}")
        return None

# ✅ Function to clean text for PDF
def remove_non_ascii(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

# ✅ Function to create PDF (uses built-in Arial font)
def create_pdf(itinerary, location, days, month):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"{days}-Day Travel Itinerary for {location} ({month})", ln=True, align='C')
    pdf.ln(10)
    itinerary_clean = remove_non_ascii(itinerary)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, itinerary_clean)
    return pdf.output(dest='S').encode('latin-1')

# ✅ Main Streamlit App
def main():
    st.title("🌍 AI Travel Itinerary Planner ✈️")
    st.subheader("Craft your perfect trip — powered by GPT-4 Turbo")

    if "itinerary" not in st.session_state:
        st.session_state["itinerary"] = None

    # Inputs
    location = st.text_input("📍 Where are you going?")
    days = st.number_input("📅 Trip Length (1-7 days):", min_value=1, max_value=7, value=3)
    month = st.selectbox("🗓️ Travel Month:", 
                         ["January", "February", "March", "April", "May", "June",
                          "July", "August", "September", "October", "November", "December"])
    budget = st.selectbox("💸 Budget:", ["Budget", "Mid-range", "Luxury"])
    activities = st.multiselect("🎯 Preferred Activities:", 
                                ["Adventure", "Relaxation", "Cultural", "Sightseeing", "Food Tour"])
    travel_companion = st.selectbox("👥 Traveling With:", ["Solo", "Couple", "Family", "Friends"])

    # Generate Itinerary
    if st.button("🚀 Generate Itinerary"):
        if location.strip():
            st.session_state["itinerary"] = None
            itinerary = generate_itinerary(location, days, month, budget, activities, travel_companion)
            if itinerary:
                st.session_state["itinerary"] = itinerary
                st.success("✅ Your itinerary is ready!")
                st.markdown(itinerary)
        else:
            st.warning("⚠️ Please enter a destination.")

    # PDF Download Option
    if st.session_state["itinerary"]:
        pdf_bytes = create_pdf(st.session_state["itinerary"], location, days, month)
        st.download_button("📥 Download PDF", data=pdf_bytes,
                           file_name=f"{location}_Itinerary.pdf", mime="application/pdf")

# ✅ Run App
if __name__ == "__main__":
    main()
