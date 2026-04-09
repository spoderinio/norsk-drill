from fastapi import APIRouter
from fastapi.responses import FileResponse
import subprocess, tempfile, os

router = APIRouter()
PIPER = os.path.expanduser("~/piper/piper")
MODEL = os.path.expanduser("~/piper-voices/no_NO-talesyntese-medium.onnx")

@router.get("/tts")
async def tts(text: str):
    wav = tempfile.mktemp(suffix=".wav")
    mp3 = tempfile.mktemp(suffix=".mp3")
    subprocess.run([PIPER, "--model", MODEL, "--length_scale", "1.3",
                    "--output_file", wav], input=text.encode(), check=True)
    subprocess.run(["/usr/bin/ffmpeg", "-y", "-i", wav, mp3], 
                   capture_output=True, check=True)
    os.unlink(wav)
    return FileResponse(mp3, media_type="audio/mpeg")
