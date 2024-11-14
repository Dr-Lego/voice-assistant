# Live Voice Assistant

A simple voice assistant that listens, processes speech, and responds using a custom language model powered by **Ollama**.

> [!WARNING]
> This project was not made for Windows or macOS. It is designed to work on Linux.

## Features

- Real-time speech recognition and conversion to text.
- Customizable conversational model using **Ollama**.
- Audible responses with **Text-to-Speech (TTS)**.
- Simple Tkinter-based UI to display spoken text and assistant's replies.

## Setup

1. **System utilities**:

   - `sudo apt-get install pulseaudio-utils alsa-utils pactl aplay` (for microphone volume control and TTS).

2. **Ollama**:

   - Install the **Ollama** client from [Ollama's website](https://ollama.com)
   - Pull `gemma2:2b` or your preferred model (you will need to modify [model.cfg](model.cfg)): `ollama pull gemma2:2b`.

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Customization

You can customize the assistant's name by modifying the NAME variable in [main.py](main.py) (default is "alex"). This name is used to trigger the assistant's listening and responses.

For example, change the name in the script to something like:

```python
NAME = "your_custom_name"
```


## Running

1. Clone the repository and install dependencies.
2. Run the assistant with:
   ```bash
   python main.py
````

3. The assistant listens for commands, processes them, and provides responses in both text and speech.
4. To stop the application, press **Ctrl+C**.
