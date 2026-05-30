import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- 1. CONFIGURATION & AI ---
load_dotenv()

# Try local .env first. If it fails (because we are on the cloud), use Streamlit Secrets.
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_KEY:
    try:
        GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

# This must be the very first Streamlit command!
st.set_page_config(page_title="Dremel AI Hub", page_icon="🔧", layout="wide")

# --- 2. DREMEL THEME INJECTION ---
st.markdown("""
    <style>
        /* 1. Dremel Cyan Accent for main buttons */
        div.stButton > button:first-child {
            background-color: #00AEEF !important;
            color: white !important;
            border: none !important;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 5px;
        }
        div.stButton > button:first-child:hover {
            background-color: #0089bd !important;
        }

        /* 2. Main page Cyan separators */
        hr {
            border-top: 2px solid #00AEEF;
        }

        /* 3. DREMEL BLUE SIDEBAR */
        [data-testid="stSidebar"] {
            background-color: #00529B !important;
        }

        /* 4. Force all text in the sidebar to be crisp white */
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] label {
            color: #FFFFFF !important;
        }

        /* 5. Make the sidebar dividers Cyan */
        [data-testid="stSidebar"] hr {
            border-top: 2px solid #00AEEF !important;
        }

        /* Tighten up the top margin */
        .block-container {
            padding-top: 2rem !important;
        }
    </style>
""", unsafe_allow_html=True)


# --- 3. CLOUD DATA CONNECTION ---
@st.cache_data(ttl=3600)
def load_cloud_data():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # If running locally on your laptop, use the file.
    if os.path.exists("dremel-bot-key.json"):
        creds = ServiceAccountCredentials.from_json_keyfile_name("dremel-bot-key.json", scope)
    # If running on the cloud, use the Streamlit Secrets vault.
    else:
        creds_dict = json.loads(st.secrets["google_sheets"]["json_key"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

    client = gspread.authorize(creds)
    sheet = client.open("Dremel_Trending_Data").sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)


# --- 4. BRANDING & MAIN NAVIGATION ---
try:
    st.sidebar.image("dremel_logo.png", use_container_width=True)
except Exception:
    st.sidebar.markdown("## DREMEL")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ App Navigation")

# THE NEW NAVIGATION DROPDOWN (Added "ℹ️ About the Project")
page_selection = st.sidebar.selectbox(
    "Select a Page:",
    [
        "🚀 Live Tools",
        "ℹ️ About the Project",
        "🏗️ Architecture: Dashboard",
        "🏗️ Architecture: AI Engine"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("Developed by Mihir Bose, Powered by AI")

# ==========================================
# PAGE 1: THE MAIN LIVE TOOLS
# ==========================================
if page_selection == "🚀 Live Tools":

    st.sidebar.markdown("**Tool Display Toggles:**")
    show_dashboard = st.sidebar.toggle("📊 Live Dashboard", value=True)
    show_ai = st.sidebar.toggle("🤖 AI Content Generator", value=True)

    if show_dashboard:
        st.markdown("""
            <div style="background-color: #00529B; padding: 20px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="color: #FFFFFF; margin: 0;">📊 Live Trend Engine Dashboard</h2>
                <p style="color: #FFFFFF; margin: 0; font-size: 16px;">Interact with the live data below to spot the fastest-growing DIY categories.</p>
            </div>
        """, unsafe_allow_html=True)

        TABLEAU_URL = "https://public.tableau.com/views/Dremel_TrendsDashboard/LiveDashboard?:language=en-US&publish=yes&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link" + "?:embed=yes&:showVizHome=no"
        st.components.v1.iframe(TABLEAU_URL, width=1200, height=700, scrolling=True)

    if show_dashboard and show_ai:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("<br><br>", unsafe_allow_html=True)

    if show_ai:
        st.markdown("""
            <div style="background-color: #00529B; padding: 20px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="color: #FFFFFF; margin: 0;">🤖 Dremel AI Ideation Center 🚀</h2>
                <p style="color: #FFFFFF; margin: 0; font-size: 16px;">Instantly translate rising trends into cross-channel marketing strategies.</p>
            </div>
        """, unsafe_allow_html=True)

        try:
            df = load_cloud_data()
            unique_keywords = sorted(df['Keyword'].dropna().unique())

            st.subheader("🎯 Step 1: Target a Trend")
            selected_trend = st.selectbox("Click inside the box to search or select a hot topic:", unique_keywords)
            st.write("")

            if st.button("⚡ Activate AI Virtual Managers", type="primary"):
                with st.spinner(f"Coordinating with virtual managers to analyze '{selected_trend}'..."):

                    prompt = f"""
                    You are a team of expert digital marketing managers at Dremel UK. 
                    The automated data engine has identified '{selected_trend}' as a major rising trend on YouTube UK.
                    Provide actionable, specific tasks for each of the following 6 managers. Keep each role's response to 2-3 clear, high-impact bullet points and use professional language tailored to Dremel's rotary tools and solutions.
                    Format your entire response EXACTLY like this so the app can read it:
                    [CONTENT]
                    - Bullet 1
                    [SOCIAL]
                    - Bullet 1
                    [EMAIL]
                    - Bullet 1
                    [WEBSITE]
                    - Bullet 1
                    [ECOMMERCE]
                    - Bullet 1
                    [PRODUCT]
                    - Bullet 1
                    """

                    model = genai.GenerativeModel('gemini-3.5-flash')
                    response = model.generate_content(prompt)
                    raw_text = response.text


                    def get_section(text, tag):
                        try:
                            parts = text.split(f"[{tag}]")
                            if len(parts) > 1:
                                return parts[1].split("[")[0].strip()
                            return "Strategy formulation in progress..."
                        except:
                            return "Strategy formulation in progress..."


                    content_strat = get_section(raw_text, "CONTENT")
                    social_strat = get_section(raw_text, "SOCIAL")
                    email_strat = get_section(raw_text, "EMAIL")
                    web_strat = get_section(raw_text, "WEBSITE")
                    ecom_strat = get_section(raw_text, "ECOMMERCE")
                    prod_strat = get_section(raw_text, "PRODUCT")

                    st.markdown("---")
                    st.subheader(f"📋 Operational Action Plan: {selected_trend.upper()}")

                    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                        "Content Manager", "Social Media", "Email Marketing",
                        "Website Manager", "3rd Party E-Com", "Product Manager"
                    ])

                    with tab1:
                        st.info("🎬 Video & Content Strategy")
                        st.write(content_strat)
                    with tab2:
                        st.info("📱 Social Media & Influencer Partnerships")
                        st.write(social_strat)
                    with tab3:
                        st.info("✉️ Email Campaign & Retention")
                        st.write(email_strat)
                    with tab4:
                        st.info("🌐 Homepage & Landing Page Optimization")
                        st.write(web_strat)
                    with tab5:
                        st.info("🛍️ Amazon & 3rd Party Retail Channels")
                        st.write(ecom_strat)
                    with tab6:
                        st.info("🛠️ Product Bundling & Accessory Focus")
                        st.write(prod_strat)

        except Exception as e:
            st.error(f"Error connecting to Cloud Data: {e}")

# ==========================================
# PAGE 2: ABOUT THE PROJECT (NEW PAGE)
# ==========================================
elif page_selection == "ℹ️ About the Project":
    st.markdown("""
        <div style="background-color: #00529B; padding: 20px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: #FFFFFF; margin: 0;">ℹ️ About This Project</h2>
            <p style="color: #FFFFFF; margin: 0; font-size: 16px;">The context, architecture, and optimal usage of the Dremel AI Hub.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 1. Why this platform was created?")
    st.write("""
    This platform was developed to modernize Dremel's marketing strategy by leveraging data-driven insights and artificial intelligence. 
    Instead of relying on historical assumptions or manual research, this tool actively monitors live consumer interests and DIY trends in the UK. 
    The goal is to bridge the gap between what target audiences are actively searching for and the multi-channel campaigns Dremel creates, ensuring maximum relevance, engagement, and ROI.
    """)

    st.divider()

    st.markdown("### 2. How it was created & how it works")
    st.write("""
    This application operates on a fully autonomous, production-grade cloud architecture built completely from scratch:
    * **Data Collection:** A serverless Python script runs nightly via GitHub Actions, scraping the YouTube API for the latest DIY and woodworking trends.
    * **NLP Processing:** The system uses Spacy (Natural Language Processing) to extract core topics and filter out conversational noise.
    * **Cloud Database:** The refined keyword data is autonomously pushed to a secure Google Sheets database.
    * **Data Visualization:** Tableau Public connects directly to this live database, rendering an interactive dashboard that updates automatically.
    * **AI Generation:** The frontend interfaces with Google's Gemini AI to dynamically generate tailored, cross-channel marketing strategies based on the live data.
    """)
    st.info("💡 *Tip: Check out the 'Architecture' pages in the sidebar menu for a deep dive into how the Dashboard and AI Engine code works!*")

    st.divider()

    st.markdown("### 3. How to use this website efficiently")
    st.markdown("""
    1. **Analyze the Data:** Go to the 'Live Tools' page and start by exploring the Tableau dashboard. Look for sudden spikes in specific categories to identify what is currently capturing audience attention.
    2. **Select a Trend:** Scroll down to the AI Ideation engine and use the dropdown menu to select one of the high-value keywords identified in the dashboard.
    3. **Generate Strategy:** Click the **'⚡ Activate AI Virtual Managers'** button. The AI will output a customized, multi-channel campaign tailored specifically around that trending topic across Content, Social, Email, Website, E-commerce, and Product Management.
    """)

# ==========================================
# PAGE 3: DASHBOARD DOCUMENTATION
# ==========================================
elif page_selection == "🏗️ Architecture: Dashboard":
    st.markdown("""
        <div style="background-color: #00529B; padding: 20px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: #FFFFFF; margin: 0;">🏗️ Data Architecture: The Trend Engine</h2>
            <p style="color: #FFFFFF; margin: 0; font-size: 16px;">Behind the scenes of the automated Tableau Dashboard.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 1. The Python Scraper (Data Collection)")
    st.write(
        "The system begins with a scheduled Python script running in the background. It utilizes the **Google API Client** to connect to YouTube's v3 API. The script is programmed with 25 highly specific DIY target keywords (e.g., 'Woodworking', 'Furniture Flips', 'Kids Crafts'). It queries the UK server region specifically, scraping the top 50 videos for each category to ensure a highly localized dataset.")

    st.markdown("### 2. Natural Language Processing (Data Processing)")
    st.write(
        "Raw video titles and descriptions are messy. To find true trends, the script uses **Spacy**, an advanced Natural Language Processing (NLP) library. The NLP engine strips away filler words ('stop words'), analyzes the grammar, and extracts only the core Nouns and Proper Nouns (e.g., pulling 'Epoxy' out of a long video title).")

    st.markdown("### 3. Google Cloud Integration (Data Storage)")
    st.write(
        "Once the data is cleaned into a Pandas DataFrame, the script authenticates securely with Google Cloud using a Service Account JSON Key and the `gspread` library. It acts as an automated 'robot worker,' wiping yesterday's data and writing today's fresh metrics directly to a hosted Google Sheet.")

    st.markdown("### 4. Tableau Public (Data Visualization)")
    st.write(
        "The final UI layer is built in Tableau. Because the dashboard is linked directly to the Google Sheet via an active data connection, it auto-syncs on a 24-hour cycle. The interactive iframe embedded in this app simply requests the most recent, published version of the dashboard from Tableau's servers.")

# ==========================================
# PAGE 4: AI ENGINE DOCUMENTATION
# ==========================================
elif page_selection == "🏗️ Architecture: AI Engine":
    st.markdown("""
        <div style="background-color: #00529B; padding: 20px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: #FFFFFF; margin: 0;">🏗️ System Architecture: The AI Ideation Tool</h2>
            <p style="color: #FFFFFF; margin: 0; font-size: 16px;">How Large Language Models (LLMs) are used to automate marketing strategy.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 1. Dynamic Cloud Retrieval")
    st.write(
        "To ensure the AI is only generating strategies based on *actual* current trends, the app must read the database first. Using Streamlit's `@st.cache_data` command, the app connects to the same Google Sheet updated by the Tableau dashboard. It caches this data so the website loads instantly, then parses the columns to populate the user's dropdown search box with live keywords.")

    st.markdown("### 2. Prompt Engineering & API Connection")
    st.write(
        "When a user clicks 'Activate Virtual Managers', the system takes the selected keyword and injects it into a highly engineered system prompt. It connects to the **Google Gemini 3.5 Flash** model via the `google.generativeai` library. The prompt specifically instructs the AI to adopt the persona of a 'Dremel UK Digital Marketing Manager' and forces it to output its response in a very strict, machine-readable format (using tags like `[CONTENT]` and `[SOCIAL]`).")

    st.markdown("### 3. Data Parsing & Routing")
    st.write(
        "Large Language Models naturally output raw blocks of text. To create the 'Manager Tabs' UI, the Python backend intercepts the raw text from Google Gemini. It runs a custom `get_section()` parsing function to split the text block apart based on the hidden tags we forced the AI to use. Finally, it routes each specific section of text into Streamlit's isolated UI tabs, creating the illusion of 6 different virtual employees working simultaneously.")