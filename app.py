import streamlit as st
import streamlit.components.v1 as components
import pathlib
import base64
import os
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="కథావనం", page_icon="📚", layout="wide")

# --- Upload directory ---
UPLOAD_DIR = "uploads"
for subfolder in ["videos", "audio", "images", "text"]:
    os.makedirs(os.path.join(UPLOAD_DIR, subfolder), exist_ok=True)

# --- Helper to save file ---
def save_file(uploaded_file, subfolder):
    folder = os.path.join(UPLOAD_DIR, subfolder)
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# --- Helper to embed image in HTML ---
def img_to_base64(img_path):
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- Load and fix HTML ---
html_content = pathlib.Path("index.html").read_text(encoding="utf-8")

# Images to embed (testimonial + Gemini image)
images_to_embed = [
    "Gemini_Generated_Image_e3tuzfe3tuzfe3tu.jpg",
    "geeta.jpg",
    "raju patel.jpg",
    "arjun.jpg"
]

for img_name in images_to_embed:
    if os.path.exists(img_name):
        img_base64 = img_to_base64(img_name)
        html_content = html_content.replace(
            img_name,
            f"data:image/jpeg;base64,{img_base64}"
        )

# --- Navigation ---
menu = st.sidebar.radio("నావిగేషన్", ["🏠 హోమ్", "📤 అప్‌లోడ్", "📂 నా కథల సేకరణ"])

# --- Homepage ---
if menu == "🏠 హోమ్":
    components.html(html_content, height=3000, scrolling=True)
    if st.button("📂 నా కథల సేకరణకు వెళ్ళండి"):
        st.session_state.page = "collection"

# --- Upload Page ---
elif menu == "📤 అప్‌లోడ్":
    st.header("📤 మీ కథను అప్‌లోడ్ చేయండి")

    tab_video, tab_audio, tab_text, tab_image = st.tabs(
        ["🎥 వీడియో", "🎙 ఆడియో", "📝 టెక్స్ట్", "🖼 చిత్రం"]
    )

    with tab_video:
        video_file = st.file_uploader("వీడియో ఫైల్ ఎంచుకోండి", type=["mp4", "mov", "avi"])
        if video_file and st.button("అప్‌లోడ్ చేయండి", key="video"):
            path = save_file(video_file, "videos")
            st.success(f"✅ వీడియో విజయవంతంగా అప్‌లోడ్ అయింది: {path}")

    with tab_audio:
        audio_file = st.file_uploader("ఆడియో ఫైల్ ఎంచుకోండి", type=["mp3", "wav", "ogg"])
        if audio_file and st.button("అప్‌లోడ్ చేయండి", key="audio"):
            path = save_file(audio_file, "audio")
            st.success(f"✅ ఆడియో విజయవంతంగా అప్‌లోడ్ అయింది: {path}")

    with tab_text:
        story_text = st.text_area("మీ కథను ఇక్కడ రాయండి (తెలుగులో)")
        if st.button("అప్‌లోడ్ చేయండి", key="text"):
            if story_text.strip():
                filename = f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(os.path.join(UPLOAD_DIR, "text", filename), "w", encoding="utf-8") as f:
                    f.write(story_text)
                st.success("✅ కథ విజయవంతంగా అప్‌లోడ్ అయింది!")
            else:
                st.error("❌ దయచేసి కథను నమోదు చేయండి")

    with tab_image:
        img_file = st.file_uploader("చిత్రం ఎంచుకోండి", type=["jpg", "jpeg", "png"])
        if img_file and st.button("అప్‌లోడ్ చేయండి", key="image"):
            path = save_file(img_file, "images")
            st.success(f"✅ చిత్రం విజయవంతంగా అప్‌లోడ్ అయింది: {path}")

# --- Collection Page ---
elif menu == "📂 నా కథల సేకరణ":
    st.header("📂 నా కథల సేకరణ")

    # Images
    st.subheader("🖼 చిత్రాలు")
    img_dir = os.path.join(UPLOAD_DIR, "images")
    img_files = [f for f in os.listdir(img_dir) if f.lower().endswith(("jpg", "jpeg", "png"))]
    if img_files:
        cols = st.columns(3)
        for i, img in enumerate(img_files):
            cols[i % 3].image(os.path.join(img_dir, img), caption=img, use_container_width=True)
    else:
        st.info("చిత్రాలు లేవు")

    # Videos
    st.subheader("🎥 వీడియోలు")
    video_dir = os.path.join(UPLOAD_DIR, "videos")
    video_files = [f for f in os.listdir(video_dir) if f.lower().endswith(("mp4", "mov", "avi"))]
    if video_files:
        for vid in video_files:
            st.video(os.path.join(video_dir, vid))
    else:
        st.info("వీడియోలు లేవు")

    # Audios
    st.subheader("🎙 ఆడియోలు")
    audio_dir = os.path.join(UPLOAD_DIR, "audio")
    audio_files = [f for f in os.listdir(audio_dir) if f.lower().endswith(("mp3", "wav", "ogg"))]
    if audio_files:
        for aud in audio_files:
            st.audio(os.path.join(audio_dir, aud))
    else:
        st.info("ఆడియోలు లేవు")

    # Text Stories
    st.subheader("📝 వ్రాత కథలు")
    text_dir = os.path.join(UPLOAD_DIR, "text")
    text_files = [f for f in os.listdir(text_dir) if f.endswith(".txt")]
    if text_files:
        for txt in text_files:
            with open(os.path.join(text_dir, txt), "r", encoding="utf-8") as f:
                st.text_area(txt, f.read(), height=150)
    else:
        st.info("వ్రాత కథలు లేవు")
