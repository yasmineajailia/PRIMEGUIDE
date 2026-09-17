import os
import traceback
from elevenlabs import ElevenLabs, VoiceSettings
import tempfile
import uuid

def generate_audio(text, voice_id="Aria", style=0.5):
    """
    Generates audio from text using ElevenLabs API.
    
    Args:
        text (str): The text to convert to speech
        voice_id (str): The voice ID to use for generation
        style (float): The style parameter for voice generation (0.0-1.0)
        
    Returns:
        tuple: (status_message, audio_path)
    """
    print(f"Generating audio for text: '{text[:50]}...' with voice: '{voice_id}'")
    
    if not text:
        return "Error: Please provide text to generate audio.", None
    
    try:
        # Load ElevenLabs API key from environment variables
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            print("Warning: ELEVENLABS_API_KEY not found in environment variables.")
            return "Error: ElevenLabs API key not configured.", None
            
        client = ElevenLabs(api_key=api_key)
        
        print(f"Generating audio with voice: {voice_id}")
        
        # Generate audio
        audio_gen = client.generate(
            text=text,
            voice=voice_id,
            model="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.4, 
                similarity_boost=0.75, 
                style=style
            ),
        )
        
        if not audio_gen:
            raise ValueError("No audio data generated.")
            
        audio_bytes = b"".join(audio_gen)
        
        if len(audio_bytes) == 0:
            raise ValueError("Audio data is empty.")        # Create directory for generated audio
        output_dir = "generated_audio"
        os.makedirs(output_dir, exist_ok=True)
        
        # Also ensure the static directory exists
        static_audio_dir = os.path.join("static", "generated_audio")
        os.makedirs(static_audio_dir, exist_ok=True)
        
        # Save the generated audio
        audio_filename = f"generated_audio_{uuid.uuid4()}.mp3"
        audio_filepath = os.path.join(output_dir, audio_filename)
        
        with open(audio_filepath, "wb") as f:
            f.write(audio_bytes)
        
        print(f"Audio saved to: {audio_filepath}")
        
        # Also save a copy directly to the static directory as a fallback
        static_audio_filepath = os.path.join(static_audio_dir, audio_filename)
        try:
            # Copy the file to ensure it's available in both locations
            import shutil
            shutil.copy2(audio_filepath, static_audio_filepath)
            print(f"Audio also copied to static directory: {static_audio_filepath}")
            
            # Verify both files exist and have content
            if os.path.exists(audio_filepath) and os.path.getsize(audio_filepath) > 0:
                print(f"Verified file exists at {audio_filepath} with size {os.path.getsize(audio_filepath)} bytes")
            else:
                print(f"WARNING: File verification failed for {audio_filepath}")
                
            if os.path.exists(static_audio_filepath) and os.path.getsize(static_audio_filepath) > 0:
                print(f"Verified file exists at {static_audio_filepath} with size {os.path.getsize(static_audio_filepath)} bytes")
            else:
                print(f"WARNING: File verification failed for {static_audio_filepath}")
                
        except Exception as e:
            print(f"Warning: Could not copy audio to static directory: {e}")
            traceback.print_exc()
        return f"Generated audio for provided text", audio_filepath
    
    except Exception as e:
        traceback.print_exc()
        error_message = f"Error generating audio: {e}"
        return error_message, None

# Available voices with descriptions
voice_descriptions = {
    "Aria": "Bright and expressive female voice, perfect for captivating narratives",
    "Roger": "Deep and composed male voice, ideal for serious narrations",
    "Sarah": "Soft and reassuring female voice, perfect for welcome messages",
    "Laura": "Warm and enthusiastic female voice that conveys energy",
    "Charlie": "Young and natural male voice, ideal for modern content",
    "George": "Mature and confident male voice, perfect for documentaries",
    "Callum": "Clear and versatile male voice, suitable for explanatory messages",
    "River": "Fluid and soothing androgynous voice, ideal for neutral messages",
    "Liam": "Young and composed male voice, perfect for podcasts",
    "Charlotte": "Soft and classic female voice, suitable for literary narrations",
    "Alice": "Modern and bubbly female voice, perfect for lifestyle content",
    "Matilda": "Soft and comforting female voice, ideal for audiobooks",
    "Will": "Dynamic and engaging male voice, ideal for promotional videos",
    "Jessica": "Warm and smiling female voice, perfect for welcome messages",
    "Eric": "Serious and charismatic male voice, ideal for solemn speeches",
    "Chris": "Casual and natural male voice, suitable for relaxed podcasts",
    "Brian": "Clear and confident male voice, ideal for announcements",
    "Daniel": "Composed and expressive male voice, perfect for explanatory videos",
    "Lily": "Soft and melodious female voice, suitable for tales",
    "Bill": "Energetic and exciting male voice, ideal for advertisements"
}
