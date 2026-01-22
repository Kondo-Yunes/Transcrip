from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import torch
import whisperx

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".mp3", ".wav"}


@dataclass
class SegmentLine:
    start: float
    end: float
    speaker: str
    text: str

    def format(self) -> str:
        return f"[{format_timestamp(self.start)} - {format_timestamp(self.end)}] {self.speaker}: {self.text.strip()}"


def format_timestamp(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{minutes:02d}:{secs:02d}.{millis:03d}"


def collect_inputs(input_path: Path) -> List[Path]:
    if input_path.is_file():
        return [input_path]
    if not input_path.exists():
        raise FileNotFoundError(f"Caminho não encontrado: {input_path}")
    return sorted([p for p in input_path.iterdir() if p.suffix.lower() in VIDEO_EXTENSIONS])


def ensure_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)


def transcribe_file(
    input_path: Path,
    output_dir: Path,
    model_name: str = "large-v3",
    language: str = "pt",
    compute_type: str = "float16",
    hf_token: str | None = None,
) -> Path:
    if not input_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")

    hf_token = hf_token or os.getenv("HF_TOKEN")
    if not hf_token:
        raise EnvironmentError(
            "Defina a variável de ambiente HF_TOKEN para habilitar diarização via pyannote."
        )

    device = "cuda" if torch.cuda.is_available() else "cpu"
    audio = whisperx.load_audio(str(input_path))

    model = whisperx.load_model(model_name, device=device, compute_type=compute_type, language=language)
    result = model.transcribe(audio)

    align_model, metadata = whisperx.load_align_model(language_code=language, device=device)
    result = whisperx.align(result["segments"], align_model, metadata, audio, device=device)

    diarize = whisperx.DiarizationPipeline(use_auth_token=hf_token, device=device)
    diarize_segments = diarize(audio)

    result = whisperx.assign_word_speakers(diarize_segments, result)

    lines = extract_lines(result["segments"])

    output_file = output_dir / f"{input_path.stem}.txt"
    output_file.write_text("\n".join(line.format() for line in lines), encoding="utf-8")
    return output_file


def extract_lines(segments: Iterable[dict]) -> List[SegmentLine]:
    lines: List[SegmentLine] = []
    for segment in segments:
        speaker = segment.get("speaker") or "INTERLOCUTOR"
        lines.append(
            SegmentLine(
                start=float(segment["start"]),
                end=float(segment["end"]),
                speaker=speaker,
                text=segment.get("text", ""),
            )
        )
    return lines


def transcribe_path(
    input_path: Path,
    output_dir: Path,
    model_name: str = "large-v3",
    language: str = "pt",
    compute_type: str = "float16",
    hf_token: str | None = None,
) -> List[Path]:
    ensure_output_dir(output_dir)
    inputs = collect_inputs(input_path)
    outputs: List[Path] = []
    for file_path in inputs:
        outputs.append(
            transcribe_file(
                file_path,
                output_dir,
                model_name=model_name,
                language=language,
                compute_type=compute_type,
                hf_token=hf_token,
            )
        )
    return outputs
