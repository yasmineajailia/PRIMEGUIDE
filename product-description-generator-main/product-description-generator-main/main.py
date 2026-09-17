# ========== Imports ==========

import os
import tempfile
import webbrowser

import faiss
import google.generativeai as genai
import ipywidgets as widgets
import numpy as np
import pandas as pd
import textstat
from dotenv import load_dotenv
from elevenlabs import ElevenLabs, VoiceSettings
from IPython.display import Audio, display
from sentence_transformers import SentenceTransformer
from transformers import pipeline

from feedback_gui import feedback_window
from nlp_utils import analyze_text

# ========== Loading Environment Variables ==========

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# ========== Loading Data ==========


def load_and_process_data():
    df_social = pd.read_csv("data/Social_Media_Advertising.csv")
    df_amazon = pd.read_csv(
        "data/train.csv", sep=",", quoting=3, on_bad_lines="skip", low_memory=False
    )
    df = pd.read_csv("data/digital_marketing_campaigns_smes.csv")

    entries = []

    for _, row in df_social.iterrows():
        entries.append(
            {
                "product": str(row.get("Campaign_Goal", "")).lower(),
                "target": str(row.get("Target_Audience", "")).lower(),
                "format": str(row.get("Channel_Used", "")).lower(),
                "completion": f"Campaign '{row.get('Campaign_Goal', '')}' on {row.get('Channel_Used', '')} for {row.get('Target_Audience', '')} | ROI: {row.get('ROI', '')}, engagement: {row.get('Engagement_Score', '')}",
            }
        )

    for _, row in df_amazon.iterrows():
        bullet_points = str(row.get("BULLET_POINTS", "")).replace("\n", " ")
        description = str(row.get("DESCRIPTION", "")).replace("\n", " ")
        entries.append(
            {
                "product": str(row.get("TITLE", "")).lower(),
                "target": "general",
                "format": "amazon",
                "completion": f"{bullet_points} {description}",
            }
        )

    for _, row in df.iterrows():
        entries.append(
            {
                "product": str(row.get("industry", "")).lower(),
                "target": str(row.get("target_audience", "")).lower(),
                "format": str(row.get("marketing_channel", "")).lower(),
                "completion": f"Conversion: {row.get('conversion_rate', '')}, engagement: {row.get('engagement_rate', '')}",
            }
        )

    return entries


# ========== Building and Loading FAISS Index ==========


def build_faiss_index(entries):
    texts = [f"{e['product']} {e['target']} {e['format']}" for e in entries]
    embeddings = embed_model.encode(texts, convert_to_numpy=True)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, "faiss_index.idx")
    np.save("embeddings.npy", embeddings)
    pd.DataFrame(entries).to_csv("entries.csv", index=False)

    return index, embeddings, texts


def load_faiss_index_and_data():
    index = faiss.read_index("faiss_index.idx")
    embeddings = np.load("embeddings.npy")
    entries = pd.read_csv("entries.csv").to_dict(orient="records")
    texts = [f"{e['product']} {e['target']} {e['format']}" for e in entries]
    return index, embeddings, entries, texts


def semantic_search(query, entries, embeddings, texts, index, top_k=3):
    query_vector = embed_model.encode([query])[0]
    distances, indices = index.search(np.array([query_vector]), top_k)
    return [entries[i] for i in indices[0]]


def generate_with_rag(product, target, ad_format, examples):
    example_texts = "\n".join([f"- {ex['completion']}" for ex in examples])
    prompt = (
        f"Here are examples of similar advertising campaigns:\n"
        f"{example_texts}\n\n"
        f"Now, generate a creative campaign adapted to the following context:\n"
        f"- Product: {product}\n"
        f"- Target audience: {target}\n"
        f"- Advertising format: {ad_format}\n"
        f"→ The message should be engaging, original, relevant for a small business, and professionally written."
    )
    response = model.generate_content(prompt)
    return response.text


# ========== User Feedback ==========


def feedback_with_stars():
    star_widget = widgets.IntSlider(
        value=0,
        min=0,
        max=5,
        step=1,
        description="Stars:",
        style={"description_width": "initial"},
        orientation="horizontal",
    )
    display(star_widget)

    def on_value_change(change):
        feedback = change["new"]
        print(f"Your rating: {feedback} stars")
        with open("feedback.txt", "a") as f:
            f.write(f"Feedback: {feedback} stars\n")
        print("Thank you for your feedback!")


# ========== Voice Descriptions ==========

voice_descriptions = {
    "Aria": "🌞 Bright and expressive female voice, perfect for captivating narratives or enthusiastic messages.",
    "Roger": "🎤 Deep and composed male voice, ideal for serious narrations or institutional messages.",
    "Sarah": "💬 Soft and reassuring female voice, perfect for welcome messages and calm instructions.",
    "Laura": "🎵 Warm and enthusiastic female voice that conveys energy and good vibes.",
    "Charlie": "🎧 Young and natural male voice, ideal for modern and dynamic content.",
    "George": "🤔 Mature and confident male voice, perfect for documentaries and inspiring speeches.",
    "Callum": "🎤 Clear and versatile male voice, suitable for dialogues and explanatory messages.",
    "River": "🎤 Fluid and soothing androgynous voice, ideal for neutral and inclusive messages.",
    "Liam": "🎤 Young and composed male voice, perfect for podcasts and casual narratives.",
    "Charlotte": "🎶 Soft and classic female voice, suitable for literary narrations and tales.",
    "Alice": "🎧 Modern and bubbly female voice, perfect for lifestyle content and tutorials.",
    "Matilda": "🌸 Soft and comforting female voice, ideal for audiobooks or guided meditations.",
    "Will": "🎤 Dynamic and engaging male voice, ideal for promotional videos and ads.",
    "Jessica": "🎤 Warm and smiling female voice, perfect for welcome messages and social videos.",
    "Eric": "🎙️ Serious and charismatic male voice, ideal for solemn speeches and historical narrations.",
    "Chris": "🎤 Casual and natural male voice, suitable for relaxed podcasts and interviews.",
    "Brian": "🎧 Clear and confident male voice, ideal for announcements and professional presentations.",
    "Daniel": "🎙️ Composed and expressive male voice, perfect for reports and explanatory videos.",
    "Lily": "🎶 Soft and melodious female voice, suitable for tales and poetic messages.",
    "Bill": "🎤 Energetic and exciting male voice, ideal for advertisements and event announcements.",
}

# ========== Audio Generation and Playback ==========


def generate_audio_from_text(text, voice_id, style):
    try:
        audio_gen = client.generate(
            text=text,
            voice=voice_id,
            model="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.4, similarity_boost=0.75, style=style
            ),
        )
        if not audio_gen:
            raise ValueError("No audio data generated.")
        audio_bytes = b"".join(audio_gen)
        if len(audio_bytes) == 0:
            raise ValueError("Audio data is empty.")
        return audio_bytes
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None


def play_audio(audio_bytes):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            f.write(audio_bytes)
            temp_audio_path = f.name
        print(f"Audio temporarily saved at: {temp_audio_path}")
        webbrowser.open(f"file://{temp_audio_path}")
    except Exception as e:
        print(f"Error playing audio: {e}")


def select_voice():
    print("\n🎤 Select a voice for audio playback:")
    for idx, (voice_name, description) in enumerate(voice_descriptions.items(), 1):
        print(f"{idx}. {voice_name}: {description}")

    choice = int(input("\nEnter the number of the desired voice: "))
    voice_name = list(voice_descriptions.keys())[choice - 1]
    return voice_name


# ========== Main Function ==========


def main():
    print("🧠 Intelligent Advertising Generator\n")
    product = input("Product: ")
    target = input("Target audience: ")
    ad_format = input("Format: ")

    if (
        os.path.exists("faiss_index.idx")
        and os.path.exists("embeddings.npy")
        and os.path.exists("entries.csv")
    ):
        print("📂 Loading index and data...")
        index, embeddings, entries, texts = load_faiss_index_and_data()
    else:
        print("🛠️ Building index and data...")
        entries = load_and_process_data()
        index, embeddings, texts = build_faiss_index(entries)

    examples = semantic_search(
        f"{product} {target} {ad_format}", entries, embeddings, texts, index
    )
    result = generate_with_rag(product, target, ad_format, examples)
    print("\n✅ Result:\n", result)

    print("\n📣 Please provide your feedback on this campaign via the graphical interface.")
    feedback_window()

    print("\n📚 Readability level:", textstat.flesch_reading_ease(result))
    print("🧒 Comprehension age:", textstat.text_standard(result))

    voice_name = select_voice()
    style = 0.5

    audio_bytes = generate_audio_from_text(result, voice_name, style)
    if audio_bytes:
        play_audio(audio_bytes)
    else:
        print("No audio generated.")


# ========== Program Launch ==========

if __name__ == "__main__":
    main()
