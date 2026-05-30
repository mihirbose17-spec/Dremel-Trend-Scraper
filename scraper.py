import os
import json
from dotenv import load_dotenv
import pandas as pd
import spacy
from googleapiclient.discovery import build
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load environment variables
load_dotenv()
API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

KEYWORDS = [
    '"DIY room decor & other DIY trends"', '"home improvement"', 'Woodworking',
    '"Paint art"', '"Fiber art"', '"Kids Crafts"', 'Engraving',
    '"Jewelry Making"', '"Personalized Gifting"', '"Event Decor"',
    '"Seasonal Decor"', '"Furniture Flips"', 'Dupes', '"Wall Decor"',
    '"Home accessories"', 'Painting', 'Hanging', 'Tiling',
    '"Feature walls"', 'Renovations', '"Full Remodels"', 'Plumbing',
    '"Bathtub Installation"', '"HVAC Work"', 'Lighting'
]

SEARCH_QUERY = f"({' OR '.join(KEYWORDS)}) UK"
nlp = spacy.load("en_core_web_sm")


def get_youtube_data(query, max_results=50):
    """Fetches video data from YouTube API."""
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    search_response = youtube.search().list(
        q=query, part='id,snippet', maxResults=max_results, type='video', regionCode='GB'
    ).execute()

    videos = []
    for search_result in search_response.get('items', []):
        videos.append({
            'Video_ID': search_result['id']['videoId'],
            'Title': search_result['snippet']['title'],
            'Description': search_result['snippet']['description'],
            'Date': search_result['snippet']['publishedAt']
        })
    return pd.DataFrame(videos)


def extract_keywords_nlp(text):
    doc = nlp(text.lower())
    return [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop and token.is_alpha]


def update_google_sheet(dataframe, sheet_name="Dremel_Trending_Data"):
    """Pushes the Pandas DataFrame to Google Sheets."""
    print("Connecting to Google Cloud...")

    # 1. Define the scope of what the bot is allowed to do
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # 2. Cloud-Proof Authentication
    if os.path.exists("dremel-bot-key.json"):
        # If running locally on your laptop
        creds = ServiceAccountCredentials.from_json_keyfile_name("dremel-bot-key.json", scope)
    else:
        # If running on the cloud (GitHub Actions)
        google_secret = os.environ.get("GOOGLE_CREDENTIALS")
        creds_dict = json.loads(google_secret)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

    client = gspread.authorize(creds)

    # 3. Open the sheet and select the first tab
    sheet = client.open(sheet_name).sheet1

    # 4. Clear old data and insert the new data
    sheet.clear()
    sheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
    print("Success! Cloud database updated.")


def main():
    print(f"Fetching data for {len(KEYWORDS)} target categories from YouTube UK...")
    df = get_youtube_data(SEARCH_QUERY)

    print("Running NLP Keyword Extraction...")
    df['Full_Text'] = df['Title'] + " " + df['Description']
    df['Extracted_Topics'] = df['Full_Text'].apply(extract_keywords_nlp)

    print("Formatting data...")
    df_clean = df.explode('Extracted_Topics')
    df_clean.rename(columns={'Extracted_Topics': 'Keyword'}, inplace=True)
    df_clean = df_clean[['Video_ID', 'Date', 'Title', 'Keyword']].dropna()

    # --- THE CLOUD UPGRADE ---
    update_google_sheet(df_clean)


if __name__ == '__main__':
    main()