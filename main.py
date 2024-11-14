import tkinter as tk
from threading import Thread
from RealtimeSTT import AudioToTextRecorder
from dimits import Dimits
from llm import LLM
import re
import signal
import sys
import demoji
import subprocess
import time
import warnings

warnings.filterwarnings("ignore", category=UserWarning, message=".*CUDAExecutionProvider.*")

NAME = "alex"

# Initialize Dimits and LLM
dt = Dimits("en_US-ryan-high")
llm = LLM(
    model_name=open("model.cfg", "r").read().strip(),
    system_prompt=f"""You are {NAME.title()}, a friendly voice assistant. Always speak naturally, as if having a casual conversation. Keep responses brief and avoid any formatting or special characters. Never use asterisks, bullet points, or markdown. Speak directly, using contractions and everyday language. If unsure, say so casually. Adjust your tone to the context and show empathy when needed. Imagine your words will be spoken aloud by a text-to-speech system."""
)

# Global flag to control the audio listening loop
running = True
messages = []


def set_microphone_volume(volume: int):
    """Sets the microphone volume."""
    if 0 <= volume <= 100:
        subprocess.run(
            ["pactl", "set-source-volume", "@DEFAULT_SOURCE@", f"{volume}%"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )


def process_text(text):
    """Process recognized text and handle LLM responses."""
    left_text.insert(tk.END, text + "\n")
    left_text.see(tk.END)

    if text.lower().startswith(NAME):
        messages.append(
            {"role": "user", "content": re.sub(NAME, "", text, flags=re.IGNORECASE)}
        )

        response = ""
        sentence = ""
        stream = llm.chat(
            messages=[{"role": "user", "content": f"SYSTEM INFORMATION: [TIME: {time.strftime('%Y-%m-%d %H:%M')}]"}]
            + messages,
            stream=True,
        )

        for chunk in stream:
            response += chunk
            right_text.insert(tk.END, chunk)
            right_text.see(tk.END)

            sentence += chunk
            if chunk.endswith((".", "!", "?")):
                set_microphone_volume(0)
                dt.text_2_speech(demoji.replace(sentence), engine="aplay")
                time.sleep(0.1)  # Delay for audio playback
                set_microphone_volume(100)
                sentence = ""

        if sentence:
            set_microphone_volume(0)
            dt.text_2_speech(demoji.replace(sentence), engine="aplay")
            time.sleep(0.1)
            set_microphone_volume(100)

        messages.append({"role": "assistant", "content": response})
        if len(messages) >= 6:
            messages.pop(0)

        right_text.insert(tk.END, "\n")
        right_text.see(tk.END)


def listen():
    """Continuously listen for audio input in a separate thread."""
    global running
    with AudioToTextRecorder(model="base", language="en") as recorder:
        while running:
            recorder.text(process_text)


def signal_handler(sig, frame):
    """Handle the Ctrl+C signal to gracefully exit."""
    global running
    print("\nCtrl+C pressed. Closing the application...")
    running = False
    root.quit()
    sys.exit(0)


# Setup the main application window
root = tk.Tk()
root.title("Live UI")

# Create two panels for displaying text
left_panel = tk.Frame(root)
right_panel = tk.Frame(root)

left_text = tk.Text(left_panel, wrap=tk.WORD)
right_text = tk.Text(right_panel, wrap=tk.WORD)

left_label = tk.Label(left_panel, text="Spoken Text")
right_label = tk.Label(right_panel, text="LLM Output")

left_label.pack(side=tk.TOP)
left_text.pack(expand=True, fill=tk.BOTH)
right_label.pack(side=tk.TOP)
right_text.pack(expand=True, fill=tk.BOTH)

left_panel.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
right_panel.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

# Register the signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# Start the audio listener in a separate thread
audio_thread = Thread(target=listen, daemon=True)
audio_thread.start()

# Run the Tkinter main loop
try:
    root.mainloop()
except KeyboardInterrupt:
    print("\nKeyboard interrupt received. Closing the application...")
finally:
    running = False
    root.quit()
    sys.exit(0)
