from __future__ import annotations

import argparse
from pathlib import Path

from transcrip.transcribe import transcribe_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Transcrição jurídica com diarização")
    parser.add_argument("--input", required=True, help="Arquivo ou pasta com vídeos")
    parser.add_argument("--output", required=True, help="Pasta para salvar as transcrições")
    parser.add_argument("--model", default="large-v3", help="Modelo WhisperX")
    parser.add_argument("--language", default="pt", help="Idioma (ex.: pt)")
    parser.add_argument("--compute-type", default="float16", help="Compute type (ex.: float16)")
    parser.add_argument("--hf-token", help="Token do Hugging Face (opcional)")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input).expanduser()
    output_dir = Path(args.output).expanduser()

    outputs = transcribe_path(
        input_path,
        output_dir,
        model_name=args.model,
        language=args.language,
        compute_type=args.compute_type,
        hf_token=args.hf_token,
    )

    for output_file in outputs:
        print(f"Gerado: {output_file}")


if __name__ == "__main__":
    main()
