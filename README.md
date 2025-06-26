# FlowerRecognizer

FlowerRecognizer is a web application built with Streamlit that allows users to recognize flower species from uploaded images. It uses the PlantNet API to perform the recognition.

## Features

- Upload a flower photo and get the species name
- Works in English and Polish
- Light and dark mode themes
- Displays confidence level of predictions
- Shows short descriptions from Wikipedia
- Saves history of recognitions with search and download options
- Gallery of all uploaded photos

## How to run the app locally

1. Clone the repository:

   git clone https://github.com/Wuwi3/FlowerRecognizer.git
   cd FlowerRecognizer

2. Create a virtual environment and install required packages:

   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   pip install -r requirements.txt

3. Add your PlantNet API key:

   Create a file called `.streamlit/secrets.toml` and put this inside:

   PLANTNET_API_KEY = "your_api_key_here"

4. Run the app:

   streamlit run flower_recognizer.py




Created by Marek Wołowik
