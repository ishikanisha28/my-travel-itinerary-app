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

# ✅ Sidebar content
st.sidebar.title("ℹ️ About This Program")
st.sidebar.info(
    "**Travel Itinerary Generator**\n\n"
    "🔹 Uses AI to create customized travel plans.\n\n"
    "🔹 Generates detailed itineraries with activity and food suggestions.\n\n"
    "🔹 Download itineraries directly as PDF files.\n\n"
    "_Plan your perfect trip effortlessly!_"
)

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
        # ✅ Updated: Using openai.ChatCompletion.create for SDK 1.65.2
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Change to "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        # ✅ Correct way to access response content
        return response['choices'][0]['message']['content'].strip()
    except openai.error.OpenAIError as e:
        st.error(f"⚠️ OpenAI API Error: {str(e)}")
        print(f"OpenAI API Error: {str(e)}")  # ✅ Logs error to Streamlit console
        return None
    except Exception as e:
        st.error(f"⚠️ Unexpected Error: {str(e)}")
        print(f"Unexpected Error: {str(e)}")  # ✅ Logs error to Streamlit console
        return None

# ✅ Function to remove non-ASCII characters
def remove_non_ascii(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

# ✅ Function to create PDF
def create_pdf(itinerary, location, days, month):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # ✅ Add a title to the PDF
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"{days}-Day Travel Itinerary for {location} in {month}", ln=True, align='C')
    pdf.ln(10)

    # ✅ Ensure UTF-8 encoding and add itinerary content
    itinerary_clean = remove_non_ascii(itinerary)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, itinerary_clean)

    # ✅ Save PDF to bytes
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return pdf_bytes

# ✅ Main application logic
def main():
    st.title("🌍 Travel Itinerary Generator ✈️")
    st.subheader("Plan your perfect trip with AI!")

    # Initialize session state for itinerary if not present
    if "itinerary" not in st.session_state:
        st.session_state["itinerary"] = None

    # Input fields for location, days, and month
    location = st.text_input("📍 Enter the location:")
    days = st.number_input("📅 Enter the number of days (1-7):", min_value=1, max_value=7, value=2)
    month = st.selectbox(
        "🗓️ Select the month of your trip:",
        ["January", "February", "March", "April", "May", "June",
         "July", "August", "September", "October", "November", "December"]
    )

    # ✅ Customization options
    budget = st.selectbox("💸 Choose your budget level:", ["Budget", "Mid-range", "Luxury"])
    activities = st.multiselect("🎯 Choose activities you like:", ["Adventure", "Relaxation", "Cultural", "Sightseeing", "Food Tour"])
    travel_companion = st.selectbox("👥 Who are you traveling with?", ["Solo", "Couple", "Family", "Friends"])

    # ✅ Generate itinerary when button is clicked
    if st.button("🚀 Generate Itinerary"):
        if location.strip():
            st.session_state["itinerary"] = None  # ✅ Reset stored itinerary
            itinerary = generate_itinerary(location, days, month, budget, activities, travel_companion)
            if itinerary:
                st.session_state["itinerary"] = itinerary
                st.success("✅ Here is your itinerary:")
                st.markdown(itinerary)
        else:
            st.warning("⚠️ Please enter a valid location.")

    # ✅ Enable PDF download only if an itinerary has been generated
    if st.session_state["itinerary"]:
        pdf_bytes = create_pdf(st.session_state["itinerary"], location, days, month)
        st.download_button(
            label="📥 Download Itinerary as PDF",
            data=pdf_bytes,
            file_name=f"{location}_Travel_Itinerary.pdf",
            mime="application/pdf"
        )
    else:
        st.info("Generate your itinerary first to enable PDF download.")

# ✅ Run the main function
if __name__ == "__main__":
    main()
