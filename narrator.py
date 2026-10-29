"""
Voice Alert Narrator
Converts a structured security alert (JSON) into a spoken audio briefing
using the ElevenLabs Text-to-Speech API.
"""

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# --- Configuration ---------------------------------------------------------
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"       # A default ElevenLabs voice
MODEL_ID = "eleven_multilingual_v2"      # Text-to-speech model
OUTPUT_FORMAT = "mp3_44100_128"          # mp3, 44.1kHz, 128kbps


def load_alert(path: str) -> dict:
    """Read the alert JSON file and return it as a Python dictionary."""
    return json.loads(Path(path).read_text())


def build_narration(alert: dict) -> str:
    """
    Turn the structured alert into a script meant to be HEARD, not read.
    Short sentences and the most important info first (severity),
    because an analyst listening can't skim.
    """
    severity = alert["severity"].upper()
    actions = alert["recommended_actions"]

    # Number the actions so the listener can follow the order
    action_lines = " ".join(
        f"Step {i}. {action}." for i, action in enumerate(actions, start=1)
    )

    return (
        f"{severity} severity alert. {alert['title']}. "
        f"Detected by {alert['source']} on host {alert['affected_host']}, "
        f"user {alert['user']}. "
        f"Technique: {alert['mitre_technique']['name']}, "
        f"MITRE {alert['mitre_technique']['id']}. "
        f"{alert['description']} "
        f"Recommended actions. {action_lines}"
    )


def synthesize(text: str, output_path: Path) -> None:
    """Send the text to ElevenLabs and save the returned audio as an mp3."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise SystemExit("Missing ELEVENLABS_API_KEY. Check your .env file.")

    client = ElevenLabs(api_key=api_key)

    # The API returns the audio as a stream of byte chunks
    audio_stream = client.text_to_speech.convert(
        text=text,
        voice_id=VOICE_ID,
        model_id=MODEL_ID,
        output_format=OUTPUT_FORMAT,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        for chunk in audio_stream:
            f.write(chunk)


def main() -> None:
    load_dotenv()  # loads the API key from .env

    parser = argparse.ArgumentParser(description="Narrate a security alert.")
    parser.add_argument("alert_file", help="Path to the alert JSON file")
    parser.add_argument("-o", "--output", default="output/alert_briefing.mp3")
    args = parser.parse_args()

    alert = load_alert(args.alert_file)
    script = build_narration(alert)

    print("Narration script:\n")
    print(script, "\n")

    synthesize(script, Path(args.output))
    print(f"Audio saved to {args.output}")


if __name__ == "__main__":
    main()
