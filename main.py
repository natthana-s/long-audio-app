import os
from flask import Flask, request
from google.cloud import texttospeech_v1 as texttospeech

app = Flask(__name__)

GCS_INPUT_URI = os.environ.get("GCS_INPUT_URI")
GCS_OUTPUT_URI_PREFIX = os.environ.get("GCS_OUTPUT_URI_PREFIX")
VOICE_LANGUAGE_CODE = os.environ.get("VOICE_LANGUAGE_CODE", "th-TH")
VOICE_NAME = os.environ.get("VOICE_NAME", "th-TH-Standard-A")
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")

@app.route("/", methods=["POST"])
def synthesize_long_audio():
    if not GCS_INPUT_URI or not GCS_OUTPUT_URI_PREFIX or not PROJECT_ID:
        return "กรุณาตั้งค่า Environment Variables: GCS_INPUT_URI, GCS_OUTPUT_URI_PREFIX และ GOOGLE_CLOUD_PROJECT", 500

    client = texttospeech.TextToSpeechLongAudioSynthesizeClient()

    # ✅ input config สำหรับ long audio
    input_config = texttospeech.InputConfig(
        gcs_source=texttospeech.GcsSource(uri=f"gs://{GCS_INPUT_URI}"),
        mime_type="text/plain"  # หรือ "application/ssml+xml" ถ้าไฟล์เป็น SSML
    )
    voice_config = texttospeech.VoiceSelectionParams(
        language_code=VOICE_LANGUAGE_CODE,
        name=VOICE_NAME
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    output_gcs_uri = f"gs://{GCS_OUTPUT_URI_PREFIX}/output.mp3"

    request_proto = texttospeech.SynthesizeLongAudioRequest(
        parent=f"projects/{PROJECT_ID}/locations/global",
        input=input_config,
        audio_config=audio_config,
        voice=voice_config,
        output_gcs_uri=output_gcs_uri
    )

    operation = client.synthesize_long_audio(request=request_proto)

    print(f"กำลังเริ่มการแปลงไฟล์เสียง... Operation Name: {operation.name}")
    return f"เริ่มต้นการแปลงไฟล์เสียงแล้ว ตรวจสอบผลได้ที่ {output_gcs_uri}", 202

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

