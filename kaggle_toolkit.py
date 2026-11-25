"""
kaggle_toolkit.py — Unified Headless Entrypoint for Gemini Editor on Kaggle
===========================================================================
Clean single-import wrapper exposing the useful media downloading, watermark
removal, audio/ASR, karaoke subtitles, forensic video analysis, and editing
pipelines from Gemini Editor without Telegram daemons, web UIs, or desktop deps.

Usage inside a Kaggle notebook cell:
    import sys
    sys.path.insert(0, "/kaggle/working/Gemini_editor")
    import kaggle_toolkit as kt

    video_path, cached = kt.download_media("https://www.instagram.com/reel/...")
    clean_path, log = kt.remove_watermark(video_path)
    wav_path = kt.extract_audio(clean_path)
    transcript = kt.transcribe_audio(wav_path)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

TOOLKIT_ROOT = Path(__file__).resolve().parent
if str(TOOLKIT_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLKIT_ROOT))


def download_media(
    url: str,
    output_dir: str = "/kaggle/working/downloads",
    filename: Optional[str] = None,
    title: Optional[str] = None,
) -> Tuple[Optional[str], bool]:
    """Download video from Instagram, YouTube, TikTok, etc. Returns (local_path, is_cached)."""
    os.makedirs(output_dir, exist_ok=True)
    from Downloader_Modules.downloader import download_video
    return download_video(
        url=url,
        custom_title=title,
        force_filename=filename,
        destination_dir=output_dir,
    )


def remove_watermark(
    input_path: str,
    output_path: Optional[str] = None,
    keywords: str = "",
    retry_level: int = 0,
    predetected_watermarks: Optional[list] = None,
    **kwargs,
) -> Tuple[Optional[str], str]:
    """Detect and remove watermarks from video/image. Returns (output_path, status_log)."""
    from Watermark_and_Inpainting.watermark_main import run_watermark_removal
    return run_watermark_removal(
        input_path=input_path,
        output_path=output_path,
        keywords=keywords,
        retry_level=retry_level,
        predetected_watermarks=predetected_watermarks,
        **kwargs,
    )


def extract_audio(video_path: str, output_wav: Optional[str] = None) -> Optional[str]:
    """Extract 16kHz mono PCM WAV from video_path. Returns output_wav or None."""
    from Audio_Modules.audio_extractor import extract_audio as _extract_audio
    if not output_wav:
        p = Path(video_path)
        output_wav = str(p.with_name(f"{p.stem}_extracted.wav"))
    ok = _extract_audio(video_path, output_wav)
    return output_wav if ok and os.path.exists(output_wav) else None


def transcribe_audio(
    audio_path: str,
    model_size: str = "small",
    language: Optional[str] = None,
    output_json_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Transcribe audio with faster-whisper including segment & word timestamps."""
    from Audio_Modules.whisper_transcriber import transcribe_audio as _transcribe
    return _transcribe(
        audio_path,
        output_json_path=output_json_path,
        model_size=model_size,
        language=language,
    )


def add_karaoke_subtitles(
    input_video: str,
    output_video: str,
    script_text: str = "",
    word_timestamps: Optional[List[Dict[str, Any]]] = None,
    existing_audio_path: Optional[str] = None,
    skip_audio_mix: bool = False,
) -> bool:
    """Burn .ASS karaoke subtitles onto input_video -> output_video."""
    from Text_Modules.karaoke_subtitle_engine import apply_karaoke_subtitles
    return apply_karaoke_subtitles(
        input_video=input_video,
        output_video=output_video,
        script_text=script_text,
        existing_audio_path=existing_audio_path,
        skip_audio_mix=skip_audio_mix,
        word_timestamps=word_timestamps,
    )


def encode_proxy(input_path: str, output_path: Optional[str] = None, for_gemini: bool = False) -> Any:
    """Create a lightweight 480p proxy (or Gemini-optimized compressed clip)."""
    from Main_Modules.proxy_encoder import encode_for_gemini, encode_proxy as _encode_proxy
    if for_gemini:
        return encode_for_gemini(input_path, output_dir=os.path.dirname(output_path) if output_path else None)
    return _encode_proxy(input_path, output_path=output_path)


def analyze_video_forensics(video_path: str, frame_paths: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
    """Run Gemini forensic video analysis (scenes, transcript alignment, watermark boxes)."""
    from Gemini_Modules.forensic_analyzer import analyze_video
    return analyze_video(video_path=video_path, frame_paths=frame_paths, **kwargs)


def run_phase1_ingest(
    source: str,
    platform: str = "instagram",
    limit: int = 1,
) -> Dict[str, Any]:
    """Run headless Phase 1 pipeline (download + proxy + audio + beat analysis)."""
    from Phase_1.phase1_orchestrator import run_phase1_pipeline
    is_url = source.strip().lower().startswith(("http://", "https://"))
    if is_url:
        return run_phase1_pipeline(mode="manual", url=source.strip(), platform=platform)
    return run_phase1_pipeline(
        mode="auto",
        target_accounts=[source.lstrip("@")],
        limit_per_account=limit,
        platform=platform,
    )


def run_phase2_edit(clip_dir: str, edit_directive: str = "", **kwargs) -> Dict[str, Any]:
    """Run Phase 2 AI editing pipeline on a clip directory."""
    from Phase_2.phase2_orchestrator import run_phase2_pipeline
    extra = dict(kwargs)
    if edit_directive:
        extra["edit_directive"] = edit_directive
    return run_phase2_pipeline(input_path=clip_dir, **extra)


def dispatch_job_config(job_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optional dispatcher for Kaggle notebook JOB_CONFIG payloads.
    Supports action: 'download' | 'watermark' | 'transcribe' | 'subtitles' | 'forensics' | 'phase1' | 'phase2'
    """
    action = str(job_config.get("action") or "").strip().lower()
    if action == "download":
        path, cached = download_media(
            url=job_config["url"],
            output_dir=job_config.get("output_dir", "/kaggle/working/downloads"),
            filename=job_config.get("filename"),
            title=job_config.get("title"),
        )
        return {"output_path": path, "cached": cached}
    if action == "watermark":
        out, log = remove_watermark(
            input_path=job_config["input_path"],
            output_path=job_config.get("output_path"),
            keywords=job_config.get("keywords", ""),
        )
        return {"output_path": out, "log": log}
    if action == "transcribe":
        wav = extract_audio(job_config["input_path"]) if job_config["input_path"].lower().endswith((".mp4", ".mov", ".mkv", ".webm")) else job_config["input_path"]
        if not wav:
            raise RuntimeError("No audio stream found to transcribe.")
        return transcribe_audio(wav, model_size=job_config.get("model_size", "small"), language=job_config.get("language"))
    if action == "subtitles":
        ok = add_karaoke_subtitles(
            input_video=job_config["input_path"],
            output_video=job_config["output_path"],
            script_text=job_config.get("script_text", ""),
            word_timestamps=job_config.get("word_timestamps"),
        )
        return {"ok": ok, "output_path": job_config["output_path"]}
    if action == "forensics":
        return analyze_video_forensics(job_config["input_path"])
    if action == "phase1":
        return run_phase1_ingest(job_config["source"], platform=job_config.get("platform", "instagram"), limit=int(job_config.get("limit", 1)))
    if action == "phase2":
        return run_phase2_edit(job_config["clip_dir"], edit_directive=job_config.get("edit_directive", ""))
    raise ValueError(f"Unsupported toolkit action: '{action}'")
