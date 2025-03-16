from openai import OpenAI
import streamlit as st
from fpdf import FPDF
import unicodedata

# ✅ Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ✅ Set page configuration
st.set_page_config(page_title="Travel Itinerary Generator", layout="wide")

# ✅ Sidebar content
st.sidebar.title("ℹ️ About This Program")
st.sidebar.info(
    "**Travel Itinerary Generator**\n\n"
    "🔹 AI-powered travel plans tailored to your preferences.\n\n"
    "🔹 Explore activities, food, and hidden gems.\n\n"
    "🔹 Download your itinerary as a PDF.\n\n"
    "_Plan your dream trip effortlessly!_"
)

# ✅ Function to generate itinerary using OpenAI GPT-4 Turbo
def generate_itinerary(location, days, month, budget, activities, travel_companion):
    activity_str = ", ".join(activities) if activities else "any"
    prompt = (
        f"Create a detailed {days}-day travel itinerary for {location} in {month}. "
        f"Budget level: {budget}. Preferred activities: {activity_str}. "
        f"Traveling with: {travel_companion}. "
        "Include morning, afternoon, and evening plans with food suggestions and timings. "
        "Mix popular and offbeat places. Avoid showing prices."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an expert travel planner. Create engaging, well-structured, day-wise itineraries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"⚠️ OpenAI API Error: {str(e)}")
        return None

# ✅ Clean text for PDF
def remove_non_ascii(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

# ✅ Create downloadable PDF (no custom font)
def create_pdf(itinerary, location, days, month):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"{days}-Day Itinerary for {location} ({month})", ln=True, align='C')
    pdf.ln(10)

    itinerary_clean = remove_non_ascii(itinerary)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, itinerary_clean)
    return pdf.output(dest='S').encode('latin-1')

# ✅ Main Streamlit App
def main():
    st.title("🌍 AI Travel Itinerary Generator ✈️")
    st.subheader("Plan your perfect trip with AI!")

    if "itinerary" not in st.session_state:
        st.session_state["itinerary"] = None

    # User Inputs
    location = st.text_input("📍 Destination:")
    days = st.number_input("📅 Trip Length (1-7 days):", min_value=1, max_value=7, value=3)
    month = st.selectbox("🗓️ Travel Month:",
                         ["January", "February", "March", "April", "May", "June",
                          "July", "August", "September", "October", "November", "December"])
    budget = st.selectbox("💸 Budget Level:", ["Budget", "Mid-range", "Luxury"])
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
