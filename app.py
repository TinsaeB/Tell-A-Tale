import streamlit as st
import requests
import pyttsx3
import tempfile
import os
import asyncio
from edge_tts import Communicate
from utils import save_tale_text, save_audio_file, zip_tale_and_audio
import base64

# Ollama API settings
OLLAMA_URL = "http://localhost:11434/api/generate"  # Default Ollama local endpoint
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"

def get_ollama_models():
    try:
        response = requests.get(OLLAMA_TAGS_URL)
        response.raise_for_status()
        data = response.json()
        # Return list of model names
        return [m['name'] for m in data.get('models', [])]
    except Exception:
        return ["phi4"]  # Fallback

def generate_tale(user_prompt, model, tale_type):
    # Explicitly require ONLY the tale text, no titles, commentary, or formatting
    prompt = (
        f"You are a creative storyteller. Write a {tale_type.lower()} tale that is imaginative, engaging, and original. "
        f"Base your story on the following prompt, genre, or theme: '{user_prompt}'. "
        f"Output ONLY the story text, with no introduction, explanation, closing remarks, titles, or formatting. Do not include any commentary or extra text—just the tale itself."
    )
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response from model.")
    except Exception as e:
        return f"Error: {e}"

def narrate_text_pyttsx3(text, voice_id=None):
    engine = pyttsx3.init()
    if voice_id:
        engine.setProperty('voice', voice_id)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        temp_filename = fp.name
    engine.save_to_file(text, temp_filename)
    engine.runAndWait()
    return temp_filename

def narrate_text_edge_tts(text, voice="en-US-JennyNeural"):
    async def _speak_async(text, voice, temp_filename):
        communicate = Communicate(text, voice)
        await communicate.save(temp_filename)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        temp_filename = fp.name
    asyncio.run(_speak_async(text, voice, temp_filename))
    return temp_filename

st.set_page_config(page_title="Tell-A-Tale: AI Story Generator & Narrator", layout="centered")
st.title("📚 Tell-A-Tale: AI Story Generator & Narrator")
st.caption("Generate, listen, save, and share AI-powered tales with narration!")

if 'tale' not in st.session_state:
    st.session_state['tale'] = ''
if 'audio_bytes' not in st.session_state:
    st.session_state['audio_bytes'] = None
if 'audio_file' not in st.session_state:
    st.session_state['audio_file'] = ''

# --- Main UI Layout (No Tabs, Modern Minimal Flow) ---

with st.container():
    st.markdown("## ✨ Generate Your Tale")
    cols = st.columns([1, 1, 1])
    with cols[0]:
        models = get_ollama_models()
        selected_model = st.selectbox(
            "Model", models, index=models.index("phi4") if "phi4" in models else 0,
            help="Choose which local LLM to use for story generation.", key="select_model_gen"
        )
    with cols[1]:
        tale_types = [
            "Biblical", "Historical", "Fun Facts", "Fairy Tale", "Science Fiction", "Fantasy", "Adventure", "Mystery", "Horror", "Comedy", "Romance", "Legend/Myth", "Children's Story"
        ]
        selected_tale_type = st.selectbox(
            "Tale Type", tale_types, index=3, key="select_tale_type_gen"
        )
    with cols[2]:
        narration_type = st.radio(
            "Narration",
            ("Standard (Offline)", "Human-like (Edge TTS)"),
            help="Choose the voice style for narration.", key="narration_type_gen"
        )

    st.markdown("---")
    prompt = st.text_area(
        "Prompt or Theme",
        placeholder="e.g. A magical forest adventure for children",
        height=80,
        help="What should the story be about?",
        key="prompt_gen"
    )

    # Voice selection
    pyttsx3_voice_id = None
    edge_voice = "en-US-JennyNeural"
    if narration_type == "Standard (Offline)":
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        pyttsx3_voice_options = [(v.id, v.name) for v in voices]
        pyttsx3_voice_id, pyttsx3_voice_label = st.selectbox(
            "Offline Voice", pyttsx3_voice_options, format_func=lambda x: x[1], key="pyttsx3_voice_select"
        )
    else:
        from edge_voices import EDGE_TTS_VOICES
        edge_voice, edge_voice_label = st.selectbox(
            "Edge TTS Voice", EDGE_TTS_VOICES, format_func=lambda x: x[1], key="edge_voice_select"
        )

    st.markdown("---")
    gen_col, narr_col = st.columns([2, 1])
    with gen_col:
        generate = st.button("✨ Generate Tale", use_container_width=True, key="generate_btn_gen")
    with narr_col:
        narrate = st.button("🎤 Narrate Tale", use_container_width=True, key="narrate_btn")

    # Tale Generation
    if generate and prompt.strip():
        with st.spinner(f"Generating a {selected_tale_type} tale using {selected_model} model..."):
            tale = generate_tale(prompt, selected_model, selected_tale_type)
            st.session_state['tale'] = tale
            st.session_state['audio_bytes'] = None
            st.session_state['audio_file'] = ''

    # Tale Display
    if st.session_state['tale']:
        st.markdown("### 📖 Your Tale")
        st.write(st.session_state['tale'])
        st.markdown("---")
        # Narration
        if narrate:
            with st.spinner("Narrating tale..."):
                if narration_type == "Human-like (Edge TTS)":
                    audio_file = narrate_text_edge_tts(st.session_state['tale'], voice=edge_voice)
                else:
                    audio_file = narrate_text_pyttsx3(st.session_state['tale'], voice_id=pyttsx3_voice_id)
                audio_bytes = open(audio_file, 'rb').read()
                st.session_state['audio_bytes'] = audio_bytes
                st.session_state['audio_file'] = audio_file
                os.remove(audio_file)
        # Audio Player & Download/Share
        if st.session_state['audio_bytes']:
            st.audio(st.session_state['audio_bytes'], format='audio/mp3')
            tale_filename = 'tale.txt'
            audio_filename = 'tale_narration.mp3'
            zip_filename = 'tale_and_audio.zip'
            st.download_button("💾 Save Tale (.txt)", st.session_state['tale'], file_name=tale_filename, mime='text/plain', help="Download the story as a text file.")
            st.download_button("💾 Save Audio (.mp3)", st.session_state['audio_bytes'], file_name=audio_filename, mime='audio/mp3', help="Download the narration as an MP3 file.")
            # --- Sharing Section ---
            import urllib.parse
            import pyperclip
            # WhatsApp share for text
            whatsapp_url = f"https://wa.me/?text={urllib.parse.quote(st.session_state['tale'])}"
            st.markdown(f"[📤 Share Tale on WhatsApp]({whatsapp_url})", unsafe_allow_html=True)
            # Telegram share for text
            telegram_url = f"https://t.me/share/url?url=&text={urllib.parse.quote(st.session_state['tale'])}"
            st.markdown(f"[📤 Share Tale on Telegram]({telegram_url})", unsafe_allow_html=True)
            # Email share for text
            email_url = f"mailto:?subject=Tell-A-Tale%20Story&body={urllib.parse.quote(st.session_state['tale'])}"
            st.markdown(f"[📤 Share Tale by Email]({email_url})", unsafe_allow_html=True)
            # Clipboard copy
            if st.button("📋 Copy Tale to Clipboard"):
                pyperclip.copy(st.session_state['tale'])
                st.success("Tale copied to clipboard!")
            # Zip for sharing
            with tempfile.TemporaryDirectory() as tmpdir:
                tale_path = os.path.join(tmpdir, tale_filename)
                audio_path = os.path.join(tmpdir, audio_filename)
                zip_path = os.path.join(tmpdir, zip_filename)
                save_tale_text(st.session_state['tale'], tale_path)
                save_audio_file(st.session_state['audio_bytes'], audio_path)
                zip_tale_and_audio(tale_path, audio_path, zip_path)
                with open(zip_path, 'rb') as f:
                    zip_bytes = f.read()
                    st.download_button("📤 Share Tale & Audio (.zip)", zip_bytes, file_name=zip_filename, mime='application/zip', help="Download a ZIP containing both the tale and narration for easy sharing.")
            # --- MongoDB Save Button ---
            from db_utils import save_tale_to_db
            if st.button("💾 Save Tale to Database"):
                doc_id = save_tale_to_db(
                    prompt,
                    selected_tale_type,
                    selected_model,
                    st.session_state['tale'],
                    st.session_state['audio_bytes']
                )
                st.success(f"Tale saved to database! Document ID: {doc_id}")
            st.info("To share audio on WhatsApp, Telegram, or Email: Download the MP3, then upload/send it in your chat or email.")
        else:
            st.info("Click 'Narrate Tale' to generate audio for your story.")
    else:
        st.info("Enter a prompt and generate a tale to get started.")

# --- Saved Tales Sidebar ---
from db_utils import get_all_tales, get_tale_by_id, search_tales, update_tale_text, delete_tale
with st.sidebar:
    st.markdown("## 📚 Saved Tales")
    # --- Search and Filtering ---
    search_query = st.text_input("🔎 Search tales (prompt or text):", "", key="sidebar_search")
    type_filter = st.selectbox("Filter by Tale Type:", ["All"] + [
        "Biblical", "Historical", "Fun Facts", "Fairy Tale", "Science Fiction", "Fantasy", "Adventure", "Mystery", "Horror", "Comedy", "Romance", "Legend/Myth", "Children's Story"
    ], key="sidebar_type_filter")
    model_filter = st.selectbox("Filter by Model:", ["All"] + list({t['model'] for t in get_all_tales()}), key="sidebar_model_filter")

    filtered_tales = search_tales(
        query=search_query if search_query else None,
        type_filter=None if type_filter == "All" else type_filter,
        model_filter=None if model_filter == "All" else model_filter
    )

    if filtered_tales:
        tale_options = [
            f"[{t['created_at'].strftime('%Y-%m-%d %H:%M')}] {t['tale_type']} | {t['model']} | {t['prompt'][:30]}..."
            for t in filtered_tales
        ]
        selected_idx = st.selectbox("Select a saved tale to view:", range(len(filtered_tales)), format_func=lambda i: tale_options[i], key="sidebar_select")
        selected_tale = filtered_tales[selected_idx]
        st.markdown(f"**Prompt:** {selected_tale['prompt']}")
        st.markdown(f"**Tale Type:** {selected_tale['tale_type']}")
        st.markdown(f"**Model:** {selected_tale['model']}")
        st.markdown(f"**Date:** {selected_tale['created_at'].strftime('%Y-%m-%d %H:%M')}")
        st.markdown("---")
        st.markdown("#### Tale Text:")
        # --- Edit Tale Text ---
        edited_text = st.text_area("Edit Tale Text:", selected_tale['tale_text'], key=f"sidebar_edit_{selected_tale['id']}")
        if st.button("💾 Save Changes", key=f"sidebar_save_{selected_tale['id']}"):
            updated = update_tale_text(selected_tale['id'], edited_text)
            if updated:
                st.success("Tale updated!")
            else:
                st.warning("No changes made or update failed.")
        if st.button("❌ Delete Tale", key=f"sidebar_delete_{selected_tale['id']}"):
            deleted = delete_tale(selected_tale['id'])
            if deleted:
                st.success("Tale deleted! Please refresh to update the list.")
            else:
                st.warning("Delete failed.")
        if st.button("▶️ Play Narration", key=f"sidebar_play_{selected_tale['id']}"):
            tale_doc = get_tale_by_id(selected_tale['id'])
            if tale_doc and tale_doc.get('audio_bytes'):
                st.audio(tale_doc['audio_bytes'], format='audio/mp3')
                st.download_button("💾 Download Narration (.mp3)", tale_doc['audio_bytes'], file_name='saved_tale_narration.mp3', mime='audio/mp3', key=f"sidebar_download_{selected_tale['id']}")
            else:
                st.warning("No narration audio found for this tale.")
    else:
        st.info("No tales found matching your criteria.")
