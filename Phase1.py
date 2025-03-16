import streamlit as st
import openai
from fpdf import FPDF
import unicodedata

# ✅ Set OpenAI API Key for v1.66.3
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ✅ Set Streamlit page config
st.set_page_config(page_title="Travel Itinerary Generator", layout="wide")

# ✅ Sidebar info
st.sidebar.title("ℹ️ About This App")
st.sidebar.info(
    "**Travel Itinerary Generator**\n\n"
    "🔹 Powered by GPT-4 Turbo\n"
    "🔹 Customized travel plans: Activities + Food + Timings\n"
    "🔹 Download as PDF — no font errors\n\n"
    "_Plan your perfect trip with ease!_"
)

# ✅ Generate Itinerary Function
def generate_itinerary(location, days, month, budget, activities, travel_companion):
    activity_str = ", ".join(activities) if activities else "any"
    prompt = (
        f"Create a detailed {days}-day travel itinerary for {location} in {month}. "
        f"Budget: {budget}. Preferred activities: {activity_str}. "
        f"Traveling with: {travel_companion}. "
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

# ✅ Remove non-ASCII characters for PDF
def remove_non_ascii(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

# ✅ Create PDF (Arial font avoids font errors)
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

# ✅ Main App Logic
def main():
    st.title("🌍 AI Travel Itinerary Generator ✈️")
    st.subheader("Plan your dream trip with GPT-4 Turbo!")

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

    if st.button("🚀 Generate Itinerary"):
        if location.strip():
            st.session_state["itinerary"] = None
            itinerary = generate_itinerary(location, days, month, budget, activities, travel_companion)
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

# ✅ Run App
if __name__ == "__main__":
    main()
