#!/usr/bin/env python3
import json
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
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


def run_transcription(
    audio_path: str,
    hf_token: str,
    language: str | None,
    batch_size: int,
) -> dict:
    if not torch.cuda.is_available():
        raise RuntimeError("GPU CUDA não encontrada. Esta interface exige GPU.")

    audio = whisperx.load_audio(audio_path)
    model = whisperx.load_model(
        "medium", "cuda", language=language, compute_type="float16"
    )
    result = model.transcribe(audio, batch_size=batch_size)

    align_model, metadata = whisperx.load_align_model(
        language_code=result["language"], device="cuda"
    )
    result = whisperx.align(result["segments"], align_model, metadata, audio, "cuda")

    diarize_model = whisperx.DiarizationPipeline(
        use_auth_token=hf_token, device="cuda"
    )
    diarize_segments = diarize_model(audio)
    result = whisperx.assign_word_speakers(diarize_segments, result)

    return {
        "language": result.get("language"),
        "segments": result["segments"],
    }


def save_outputs(result: dict, output_dir: str) -> tuple[str, str]:
    os.makedirs(output_dir, exist_ok=True)
    txt_path = os.path.join(output_dir, "transcricao.txt")
    json_path = os.path.join(output_dir, "transcricao.json")

    lines = render_lines(result["segments"])
    with open(txt_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)

    return txt_path, json_path


def main() -> None:
    root = tk.Tk()
    root.title("Transcrição com diarização")
    root.geometry("720x520")

    style = ttk.Style()
    style.theme_use("clam")

    audio_path_var = tk.StringVar()
    output_dir_var = tk.StringVar(value=os.getcwd())
    hf_token_var = tk.StringVar(value=os.environ.get("HF_TOKEN", ""))
    language_var = tk.StringVar()
    batch_size_var = tk.StringVar(value="16")
    status_var = tk.StringVar(value="Pronto para transcrever.")

    def select_audio() -> None:
        filename = filedialog.askopenfilename(
            title="Selecione o áudio/vídeo",
            filetypes=[
                ("Áudio/Vídeo", "*.wav *.mp3 *.m4a *.mp4 *.mov *.flac"),
                ("Todos", "*.*"),
            ],
        )
        if filename:
            audio_path_var.set(filename)

    def select_output_dir() -> None:
        directory = filedialog.askdirectory(title="Selecione a pasta de saída")
        if directory:
            output_dir_var.set(directory)

    def set_status(message: str) -> None:
        status_var.set(message)
        root.update_idletasks()

    def run_job() -> None:
        audio_path = audio_path_var.get().strip()
        output_dir = output_dir_var.get().strip()
        hf_token = hf_token_var.get().strip()
        language = language_var.get().strip() or None

        if not audio_path:
            messagebox.showerror("Erro", "Selecione um arquivo de áudio/vídeo.")
            return
        if not hf_token:
            messagebox.showerror("Erro", "Informe o token do Hugging Face.")
            return

        try:
            batch_size = int(batch_size_var.get())
        except ValueError:
            messagebox.showerror("Erro", "Batch size deve ser um número inteiro.")
            return

        def task() -> None:
            try:
                set_status("Processando... Isso pode levar alguns minutos.")
                result = run_transcription(audio_path, hf_token, language, batch_size)
                txt_path, json_path = save_outputs(result, output_dir)
                set_status("Transcrição concluída.")
                messagebox.showinfo(
                    "Concluído",
                    f"Arquivos salvos em:\n{txt_path}\n{json_path}",
                )
            except Exception as exc:  # noqa: BLE001
                set_status("Erro durante a transcrição.")
                messagebox.showerror("Erro", str(exc))

        threading.Thread(target=task, daemon=True).start()

    container = ttk.Frame(root, padding=16)
    container.pack(fill=tk.BOTH, expand=True)

    ttk.Label(
        container,
        text="Transcreva áudio/vídeo com timestamps e identificação de interlocutores.",
    ).pack(anchor=tk.W, pady=(0, 12))

    audio_frame = ttk.Frame(container)
    audio_frame.pack(fill=tk.X, pady=4)
    ttk.Label(audio_frame, text="Arquivo de áudio/vídeo").pack(anchor=tk.W)
    audio_entry = ttk.Entry(audio_frame, textvariable=audio_path_var)
    audio_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
    ttk.Button(audio_frame, text="Selecionar...", command=select_audio).pack(
        side=tk.RIGHT
    )

    output_frame = ttk.Frame(container)
    output_frame.pack(fill=tk.X, pady=4)
    ttk.Label(output_frame, text="Pasta de saída").pack(anchor=tk.W)
    output_entry = ttk.Entry(output_frame, textvariable=output_dir_var)
    output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
    ttk.Button(output_frame, text="Selecionar...", command=select_output_dir).pack(
        side=tk.RIGHT
    )

    token_frame = ttk.Frame(container)
    token_frame.pack(fill=tk.X, pady=4)
    ttk.Label(token_frame, text="Token do Hugging Face").pack(anchor=tk.W)
    ttk.Entry(token_frame, textvariable=hf_token_var, show="*").pack(
        fill=tk.X, expand=True
    )

    options_frame = ttk.Frame(container)
    options_frame.pack(fill=tk.X, pady=8)
    ttk.Label(options_frame, text="Idioma (ex: pt, en)").grid(
        row=0, column=0, sticky=tk.W
    )
    ttk.Entry(options_frame, textvariable=language_var, width=10).grid(
        row=0, column=1, sticky=tk.W, padx=(8, 16)
    )
    ttk.Label(options_frame, text="Batch size").grid(row=0, column=2, sticky=tk.W)
    ttk.Entry(options_frame, textvariable=batch_size_var, width=6).grid(
        row=0, column=3, sticky=tk.W, padx=(8, 0)
    )

    action_frame = ttk.Frame(container)
    action_frame.pack(fill=tk.X, pady=12)
    ttk.Button(action_frame, text="Transcrever", command=run_job).pack(anchor=tk.W)

    ttk.Label(container, textvariable=status_var).pack(anchor=tk.W, pady=(8, 0))

    root.mainloop()


if __name__ == "__main__":
    main()
