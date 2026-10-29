# Voice Alert Narrator
 
Turns structured security alerts (JSON) into spoken audio briefings for SOC analysts, using the [ElevenLabs Text-to-Speech API](https://elevenlabs.io/docs).
 
## The problem
 
Security analysts spend long shifts watching dashboards, and critical alerts compete for attention with dozens of other signals. Some situations make screens a poor channel:
 
- **On-call responders** who are away from their desk, driving, or woken at 3 AM.
- **Eyes-busy work**: an analyst already deep in an investigation who needs to hear that something critical just fired.
- **Accessibility**: analysts with visual impairments or screen fatigue.
An audio briefing delivers the essentials in about 30 seconds, in the order a human would want to hear them.
 
## The solution
 
`Voice Alert Narrator` takes the JSON alert your EDR/SIEM already produces and generates a short spoken summary as an `.mp3`.
 
```
Alert JSON  ->  Narration script  ->  ElevenLabs TTS API  ->  .mp3 briefing
 (EDR/SIEM)     (written for the ear)
```
 
### Design decision: write for the ear, not the eye
 
Reading raw fields aloud ("Host: FIN-WS-023. Technique: T1003.") sounds robotic and is hard to follow. The narration script is deliberately rewritten for listening:
 
- **Severity first**, because a listener can't skim ahead.
- **Conversational phrasing** instead of field-by-field reading.
- **Identifiers spelled out** (`FIN-WS-023` becomes "F I N, W S, 0 2 3") so they are pronounced clearly.
- **Pauses between sections** to give the listener time to absorb.
- **Ordered actions** ("First... Then... Finally...") so response steps are easy to follow.
Voice choice and voice settings (stability, style) were tuned by ear to get a calm, clear delivery rather than the robotic default.
 
## Quick start
 
**Requirements:** Python 3.9+ and an ElevenLabs account.
 
```bash
git clone https://github.com/FranVV-Ecu/voice-alert-narrator.git
cd voice-alert-narrator
 
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
 
Create your API key in ElevenLabs, then store it locally:
 
```bash
cp .env.example .env
# edit .env and set ELEVENLABS_API_KEY=your_key
```
 
Run it:
 
```bash
python narrator.py sample_alerts/critical_credential_theft.json
afplay output/alert_briefing.mp3     # macOS; use any audio player elsewhere
```
 
Use `-o` to choose the output path:
 
```bash
python narrator.py sample_alerts/critical_credential_theft.json -o output/custom.mp3
```
 
## Input format
 
Alerts follow a typical SOC structure (see `sample_alerts/`):
 
```json
{
  "alert_id": "ALR-2026-00417",
  "severity": "critical",
  "title": "Possible credential dumping on finance workstation",
  "source": "EDR",
  "affected_host": "FIN-WS-023",
  "user": "m.rivera",
  "mitre_technique": { "id": "T1003", "name": "OS Credential Dumping" },
  "description": "...",
  "recommended_actions": ["...", "..."]
}
```
 
All sample data is fictional.
 
## Project structure
 
```
voice-alert-narrator/
├── narrator.py            # Main script: load alert, build script, call API
├── sample_alerts/         # Fictional example alerts
├── requirements.txt       # Python dependencies
├── .env.example           # Template for local configuration
└── .gitignore             # Keeps secrets and generated audio out of Git
```
 
## Security notes
 
- The API key is loaded from a local `.env` file and is **never committed** (`.gitignore` excludes it).
- Use an API key with **least-privilege permissions**: only Text to Speech is needed.
- Alert data may contain sensitive details (hostnames, usernames). In a real deployment, review your organization's policy before sending alert content to any third-party API.
## Roadmap
 
- **Severity-based voices**: a firmer delivery for critical alerts, calmer for informational ones.
- **Multilingual briefings** for global SOC teams, using the multilingual model.
- **Batch mode**: a single digest of the top alerts from the last hour.
- **SIEM integration**: trigger narration automatically from a webhook (Splunk, Sentinel, etc.).
- **Conversational follow-up** with ElevenLabs Agents: let the analyst ask "which other hosts show this pattern?" and hear the answer.
- **Streaming output** for lower latency on time-critical alerts.
## Tech stack
 
Python, [ElevenLabs Python SDK](https://github.com/elevenlabs/elevenlabs-python), python-dotenv.
