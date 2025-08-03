import os
from flask import Flask, request
from google.cloud import texttospeech_v1
from google.cloud.texttospeech_v1.types.cloud_tts_longaudio import (
    SynthesizeLongAudioRequest,
    GcsSource,
    InputConfig
)

# สำหรับพารามิเตอร์ทั่วไป
from google.cloud.texttospeech_v1.types import (
    VoiceSelectionParams,
    AudioConfig
)
app = Flask(__name__)

GCS_INPUT_URI = os.environ.get("GCS_INPUT_URI")
GCS_OUTPUT_URI_PREFIX = os.environ.get("GCS_OUTPUT_URI_PREFIX")
VOICE_LANGUAGE_CODE = os.environ.get("VOICE_LANGUAGE_CODE", "th-TH")
VOICE_NAME = os.environ.get("VOICE_NAME", "th-TH-Standard-A")
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")

@app.route("/", methods=["POST"])
def synthesize_long_audio():
    if not GCS_INPUT_URI or not GCS_OUTPUT_URI_PREFIX or not PROJECT_ID:
        return "Missing environment variables", 500

    client = texttospeech_v1.TextToSpeechLongAudioSynthesizeClient()

    input_config = InputConfig(
        gcs_source=GcsSource(uri=f"gs://{GCS_INPUT_URI}"),
        mime_type="text/plain"
    )

    voice = VoiceSelectionParams(
        language_code=VOICE_LANGUAGE_CODE,
        name=VOICE_NAME
    )

    audio_config = AudioConfig(
        audio_encoding=texttospeech_v1.AudioEncoding.MP3
    )

    output_gcs_uri = f"gs://{GCS_OUTPUT_URI_PREFIX}/output.mp3"

    request_proto = SynthesizeLongAudioRequest(
        parent=f"projects/{PROJECT_ID}/locations/global",
        input=input_config,
        audio_config=audio_config,
        voice=voice,
        output_gcs_uri=output_gcs_uri
    )

    operation = client.synthesize_long_audio(request=request_proto)
    print(f"Operation started: {operation.name}")

    return f"กำลังประมวลผลเสียง: {operation.name}", 202

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

