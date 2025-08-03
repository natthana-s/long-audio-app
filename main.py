import os
from flask import Flask, request
from google.cloud import texttospeech

app = Flask(__name__)

# ดึงค่าจาก Environment Variables ที่เราจะตั้งค่าบน Cloud Run
GCS_INPUT_URI = os.environ.get("GCS_INPUT_URI")
GCS_OUTPUT_URI_PREFIX = os.environ.get("GCS_OUTPUT_URI_PREFIX")
VOICE_LANGUAGE_CODE = os.environ.get("VOICE_LANGUAGE_CODE", "th-TH")
VOICE_NAME = os.environ.get("VOICE_NAME", "th-TH-Standard-A")

@app.route("/", methods=["POST"])
def synthesize_long_audio():
    """
    ฟังก์ชันหลักที่จะถูกเรียกเมื่อมี Request เข้ามา
    เพื่อสั่งให้ Text-to-Speech เริ่มทำงาน
    """
    if not GCS_INPUT_URI or not GCS_OUTPUT_URI_PREFIX:
        return "กรุณาตั้งค่า Environment Variables: GCS_INPUT_URI และ GCS_OUTPUT_URI_PREFIX", 500

    # 1. สร้าง Client เพื่อเชื่อมต่อกับ Text-to-Speech API
    client = texttospeech.TextToSpeechClient()

    # 2. กำหนด Input จากไฟล์ใน Cloud Storage
    input_config = texttospeech.SynthesisInput(
        text=f"gs://{GCS_INPUT_URI}"
    )

    # 3. กำหนดค่าเสียงที่ต้องการ
    voice_config = texttospeech.VoiceSelectionParams(
        language_code=VOICE_LANGUAGE_CODE,
        name=VOICE_NAME
    )

    # 4. กำหนดรูปแบบไฟล์เสียง (Output)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    # 5. กำหนดตำแหน่งที่จะเก็บไฟล์เสียงที่แปลงเสร็จแล้ว
    output_gcs_uri = f"gs://{GCS_OUTPUT_URI_PREFIX}/output.mp3"

    # 6. ประกอบร่าง Request ทั้งหมดเข้าด้วยกัน
    request = texttospeech.SynthesizeLongAudioRequest(
        input=input_config,
        audio_config=audio_config,
        voice=voice_config,
        output_gcs_uri=output_gcs_uri,
    )

    # 7. สั่งให้ API เริ่มทำงาน (แบบ Asynchronous)
    operation = client.synthesize_long_audio(request=request)

    print(f"กำลังเริ่มการแปลงไฟล์เสียง... Operation Name: {operation.name}")
    
    # ตอบกลับทันทีว่าเริ่มงานแล้ว ไม่ต้องรอจนงานเสร็จ
    return f"เริ่มต้นการแปลงไฟล์เสียงแล้ว สามารถตรวจสอบผลลัพธ์ได้ที่ {output_gcs_uri} ในภายหลัง", 202

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))