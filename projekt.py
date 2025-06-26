import streamlit as st
import requests
from PIL import Image
import io
import pandas as pd
import plotly.express as px
import wikipedia

API_KEY = st.secrets.get("PLANTNET_API_KEY")

# Session state initialization
st.session_state.setdefault("history", [])
st.session_state.setdefault("gallery", [])
st.session_state.setdefault("theme", "dark")
st.session_state.setdefault("lang", "en")

# Translations
TEXTS = {
    "en": {
        "title": "Flower Recognition App",
        "language": "Language selected",
        "dark_mode": "Dark Mode",
        "lang_checkbox": "Polish",
        "intro": "Upload a photo of a flower to find out what species it is!",
        "upload_text": "Choose a flower photo",
        "about_text": "This app uses the PlantNet API to identify flowers and plants. Upload a photo to learn more!",
        "learn_more": "Learn more about PlantNet",
        "error_message": "Error recognizing the image. Please check your API key or try again.",
        "history_text": "Prediction History",
        "filter_history": "Filter history (file name or species):",
        "download_result": "Download result (text)",
        "download_annotated": "Download annotated image",
        "footer": "Created by Marek Wołowik"
    },
    "pl": {
        "title": "Aplikacja do rozpoznawania kwiatów",
        "language": "Wybrany język",
        "dark_mode": "Ciemny motyw",
        "lang_checkbox": "Polski",
        "intro": "Prześlij zdjęcie kwiatu, aby dowiedzieć się, jaki to gatunek!",
        "upload_text": "Wybierz zdjęcie kwiatu",
        "about_text": "Aplikacja używa PlantNet API do identyfikacji kwiatów i roślin. Prześlij zdjęcie, aby dowiedzieć się więcej!",
        "learn_more": "Dowiedz się więcej o PlantNet",
        "error_message": "Błąd rozpoznawania obrazu. Sprawdź klucz API lub spróbuj ponownie.",
        "history_text": "Historia rozpoznań",
        "filter_history": "Filtruj historię (nazwa pliku lub gatunek):",
        "download_result": "Pobierz wynik (tekst)",
        "download_annotated": "Pobierz zdjęcie z adnotacją",
        "footer": "Stworzone przez Marek Wołowik"
    }
}

# Theme setting function
def set_theme():
    if st.session_state.theme == "light":
        bg_color = "#e6f2ff"
        sidebar_color = "#f8f9fa"
        box_bg = "#d4edda"
        text_color = "#222"
    else:
        bg_color = "#18191A"
        sidebar_color = "#242526"
        box_bg = "#23272b"
        text_color = "#f0f2f6"
    
    theme = f"""
    <style>
    body, .main, .stApp {{ font-family: 'Arial', sans-serif; background-color: {bg_color}; color: {text_color}; }}
    .stButton>button {{ color: white; background: linear-gradient(90deg, #ffb347, #ffcc33); border-radius: 5px; padding: 10px; }}
    .stSidebar {{ background-color: {sidebar_color}; }}
    .result-box {{ background-color: {box_bg}; color: {text_color}; padding: 15px; border-radius: 8px; }}
    </style>
    """
    st.markdown(theme, unsafe_allow_html=True)

set_theme()

# Sidebar Configuration
with st.sidebar:
    st.title("🌼 Flower Recognition")
    theme_changed = st.checkbox(f"🌙 {TEXTS[st.session_state.lang]['dark_mode']}", value=(st.session_state.theme == "dark"))
    if theme_changed != (st.session_state.theme == "dark"):
        st.session_state.theme = "dark" if theme_changed else "light"
        st.rerun()  # Rerun when theme changes

    lang_changed = st.checkbox(f"🇵🇱 {TEXTS[st.session_state.lang]['lang_checkbox']}", value=(st.session_state.lang == "pl"))
    if lang_changed != (st.session_state.lang == "pl"):
        st.session_state.lang = "pl" if lang_changed else "en"
        st.rerun()  # Rerun when language changes

    st.markdown(f"**{TEXTS[st.session_state.lang]['language']}:** {('English' if st.session_state.lang == 'en' else 'Polski')}")
    st.info(TEXTS[st.session_state.lang]["about_text"])
    st.markdown(f"[{TEXTS[st.session_state.lang]['learn_more']}](https://plantnet.org/)")

# Main Content
st.title(TEXTS[st.session_state.lang]["title"])
st.write(TEXTS[st.session_state.lang]["intro"])

uploaded_file = st.file_uploader(TEXTS[st.session_state.lang]["upload_text"], type=["jpg", "png"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()

    url = "https://my-api.plantnet.org/v2/identify/all"
    files = {"images": img_byte_arr}
    params = {"api-key": API_KEY, "lang": st.session_state.lang}

    response = requests.post(url, files=files, params=params)
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            best_match = results[0]
            species = best_match["species"]["scientificName"]
            confidence = best_match["score"] * 100

            st.markdown(f"<div class='result-box'>🌼 This is probably a <b>{species}</b>!<br>Confidence: {confidence:.2f}%</div>", unsafe_allow_html=True)

            st.markdown("#### Top 3 Species")
            df = pd.DataFrame([{"Species": r["species"]["scientificName"], "Confidence": r["score"]*100} for r in results[:3]])
            st.dataframe(df, use_container_width=True)
            fig = px.bar(df, x="Species", y="Confidence", title="Confidence Level", color="Species")
            st.plotly_chart(fig, use_container_width=True)

            try:
                wikipedia.set_lang(st.session_state.lang)
                summary = wikipedia.summary(species, sentences=2)
                st.markdown(f"**About {species}:** {summary}")
            except Exception:
                st.info("No Wikipedia description available for this species.")

            st.session_state.history.append({"file": uploaded_file.name, "prediction": species, "confidence": confidence})
            st.session_state.gallery.append(image)

            result_text = f"Species: {species}\nConfidence: {confidence:.2f}"

        else:
            st.error(TEXTS[st.session_state.lang]["error_message"])
    else:
        st.error(TEXTS[st.session_state.lang]["error_message"])

# Display History
if st.session_state.history:
    st.markdown(f"### 📝 {TEXTS[st.session_state.lang]['history_text']}")
    hist_df = pd.DataFrame(st.session_state.history)
    filter_term = st.text_input(TEXTS[st.session_state.lang]["filter_history"])
    if filter_term:
        hist_df = hist_df[hist_df["file"].str.contains(filter_term, case=False) | hist_df["prediction"].str.contains(filter_term, case=False)]
    st.dataframe(hist_df, use_container_width=True)
    csv = hist_df.to_csv(index=False).encode()
    st.download_button("Download history (CSV)", csv, "flower_history.csv", "text/csv")

# Display Gallery
if st.session_state.gallery:
    st.markdown("### 🌸 Gallery")
    cols = st.columns(3)
    for idx, img in enumerate(st.session_state.gallery):
        with cols[idx % 3]:
            st.image(img, use_container_width=True, caption=f"#{idx+1}")

# Footer
st.markdown(f"""
    <footer style="text-align: center; padding: 10px; background-color: {('#e6f2ff' if st.session_state.theme == 'light' else '#242526')};">
        <small style="color: #fff;">© 2025 Flower Recognition — {TEXTS[st.session_state.lang]['footer']}<br>
        <a href="https://github.com/Wuwi3" target="_blank" style="color: #fff;">GitHub</a> | 
        <a href="mailto:marek.wolowik01@gmail.com" style="color: #fff;">Contact me</a></small>
    </footer>
    """, unsafe_allow_html=True)
