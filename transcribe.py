#!/usr/bin/env python3
import argparse
import json
import os
from typing import Iterable

import torch
import whisperx


def format_timestamp(seconds: float) -> str:
    total_ms = int(round(seconds * 1000))
    ms = total_ms % 1000
    total_seconds = total_ms // 1000
    s = total_seconds % 60
    total_minutes = total_seconds // 60
    m = total_minutes % 60
    h = total_minutes // 60
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def render_lines(segments: Iterable[dict]) -> list[str]:
    lines: list[str] = []
    for segment in segments:
        start = format_timestamp(segment["start"])
        end = format_timestamp(segment["end"])
        speaker = segment.get("speaker", "UNKNOWN")
        text = segment.get("text", "").strip()
        lines.append(f"[{start} -> {end}] {speaker}: {text}")
    return lines


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Transcreve áudio para texto com timestamps e identificação de interlocutor."
        )
    )
    parser.add_argument("audio", help="Caminho para o arquivo de áudio/video")
    parser.add_argument(
        "--model",
        default="medium",
        help="Modelo WhisperX (ex: tiny, base, small, medium, large-v2)",
    )
    parser.add_argument(
        "--device",
        default="cuda",
        help="Dispositivo para execução (cuda ou cpu)",
    )
    parser.add_argument(
        "--language",
        default=None,
        help="Idioma esperado (ex: pt, en). Se omitido, será detectado.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Arquivo de saída (.txt ou .json). Se omitido, imprime no stdout.",
    )
    parser.add_argument(
        "--hf-token",
        default=os.environ.get("HF_TOKEN"),
        help="Token do Hugging Face para diarização (ou defina HF_TOKEN).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
        help="Tamanho do batch para transcrição.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.device == "cuda" and not torch.cuda.is_available():
        raise SystemExit(
            "GPU CUDA não encontrada. Use --device cpu para rodar na CPU."
        )

    if not args.hf_token:
        raise SystemExit(
            "Token do Hugging Face é obrigatório para diarização. "
            "Use --hf-token ou defina HF_TOKEN."
        )

    compute_type = "float16" if args.device == "cuda" else "int8"

    audio = whisperx.load_audio(args.audio)
    model = whisperx.load_model(
        args.model, args.device, language=args.language, compute_type=compute_type
    )
    result = model.transcribe(audio, batch_size=args.batch_size)

    align_model, metadata = whisperx.load_align_model(
        language_code=result["language"], device=args.device
    )
    result = whisperx.align(result["segments"], align_model, metadata, audio, args.device)

    diarize_model = whisperx.DiarizationPipeline(
        use_auth_token=args.hf_token, device=args.device
    )
    diarize_segments = diarize_model(audio)
    result = whisperx.assign_word_speakers(diarize_segments, result)

    output_data = {
        "language": result.get("language"),
        "segments": result["segments"],
    }

    if args.output:
        _, ext = os.path.splitext(args.output)
        if ext.lower() == ".json":
            with open(args.output, "w", encoding="utf-8") as handle:
                json.dump(output_data, handle, ensure_ascii=False, indent=2)
        else:
            lines = render_lines(result["segments"])
            with open(args.output, "w", encoding="utf-8") as handle:
                handle.write("\n".join(lines))
    else:
        for line in render_lines(result["segments"]):
            print(line)


if __name__ == "__main__":
    main()
