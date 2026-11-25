# Gemini Editor — Kaggle Headless Toolkit API

Clean headless toolbox stripped of Telegram bot daemons, web UIs, Windows desktop packages, and social auto-publishers.

## Kaggle Quick Setup
```python
import os, sys, subprocess
REPO_URL = "https://github.com/iammidhun6771/agent-helper-kaggle.git"
REPO_DIR = "/kaggle/working/Gemini_editor"
if not os.path.exists(REPO_DIR):
    subprocess.run(["git", "clone", "--depth", "1", REPO_URL, REPO_DIR], check=True)
else:
    subprocess.run(["git", "-C", REPO_DIR, "pull", "--ff-only"], check=True)
sys.path.insert(0, REPO_DIR)
import kaggle_toolkit as kt
```

## Available Functions (`import kaggle_toolkit as kt`)

- `kt.download_media(url, output_dir="/kaggle/working/downloads", filename=None, title=None)`  
  Downloads video via multi-strategy `yt-dlp` / Apify fallback (`Downloader_Modules/downloader.py`). Returns `(local_path, is_cached)`.

- `kt.remove_watermark(input_path, output_path=None, keywords="", retry_level=0)`  
  Detects and inpaints/removes watermarks (`Watermark_and_Inpainting/watermark_main.py`). Returns `(output_path, status_log)`.

- `kt.extract_audio(video_path, output_wav=None)`  
  Extracts 16 kHz mono WAV via FFmpeg (`Audio_Modules/audio_extractor.py`).

- `kt.transcribe_audio(audio_path, model_size="small", language=None)`  
  Runs `faster-whisper` ASR returning segments & word timestamps (`Audio_Modules/whisper_transcriber.py`).

- `kt.add_karaoke_subtitles(input_video, output_video, script_text="", word_timestamps=None)`  
  Renders `.ASS` karaoke subtitles (`Text_Modules/karaoke_subtitle_engine.py`).

- `kt.encode_proxy(input_path, output_path=None, for_gemini=False)`  
  Creates 480p proxy or Gemini-optimized compressed clip (`Main_Modules/proxy_encoder.py`).

- `kt.analyze_video_forensics(video_path)`  
  Gemini video timeline + transcript alignment + watermark box analysis (`Gemini_Modules/forensic_analyzer.py`). Requires `GEMINI_API_KEY`.

- `kt.run_phase1_ingest(source, platform="instagram", limit=1)`  
  Full Phase 1 download + proxy + audio + beat pipeline (`Phase_1/phase1_orchestrator.py`).

- `kt.run_phase2_edit(clip_dir, edit_directive="")`  
  Phase 2 master edit orchestrator (`Phase_2/phase2_orchestrator.py`).
