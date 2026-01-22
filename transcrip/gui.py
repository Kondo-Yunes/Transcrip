from __future__ import annotations

import os
import threading
import tkinter as tk
from dataclasses import dataclass, field
from pathlib import Path
from tkinter import filedialog, messagebox

from transcrip.config import AppConfig, load_config, save_config
from transcrip.transcribe import transcribe_path


@dataclass
class AppState:
    selected_files: list[Path] = field(default_factory=list)
    selected_folder: Path | None = None


def pick_files(state: AppState, input_label: tk.Label) -> None:
    paths = filedialog.askopenfilenames(title="Selecione um ou mais vídeos")
    if paths:
        state.selected_files = [Path(path) for path in paths]
        state.selected_folder = None
        input_label.config(text=f"{len(state.selected_files)} arquivo(s) selecionado(s).")


def pick_folder(state: AppState, input_label: tk.Label) -> None:
    path = filedialog.askdirectory(title="Selecione uma pasta de vídeos")
    if path:
        state.selected_folder = Path(path)
        state.selected_files = []
        input_label.config(text=f"Pasta selecionada: {state.selected_folder}")


def pick_output_folder(entry: tk.Entry) -> None:
    path = filedialog.askdirectory(title="Selecione a pasta de saída")
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)


def open_output_folder(output_entry: tk.Entry) -> None:
    output_path = output_entry.get().strip()
    if not output_path:
        messagebox.showwarning("Atenção", "Selecione a pasta de saída primeiro.")
        return
    path = Path(output_path)
    if not path.exists():
        messagebox.showwarning("Atenção", "A pasta de saída não existe.")
        return
    if os.name == "nt":
        os.startfile(path)  # type: ignore[attr-defined]
    else:
        os.system(f'xdg-open "{path}"')


def save_token(token_entry: tk.Entry, status: tk.Label) -> None:
    token = token_entry.get().strip()
    config = AppConfig(hf_token=token)
    save_config(config)
    status.config(text="Token salvo localmente com sucesso.", fg="#1f4")


def run_transcription(
    state: AppState, output_entry: tk.Entry, token_entry: tk.Entry, status: tk.Label
) -> None:
    output_path = output_entry.get().strip()
    if not output_path:
        messagebox.showerror("Erro", "Selecione a pasta de saída.")
        return

    if state.selected_files:
        input_path: Path | list[Path] = [Path(p) for p in state.selected_files]
    elif state.selected_folder:
        input_path = state.selected_folder
    else:
        messagebox.showerror("Erro", "Selecione um ou mais vídeos ou uma pasta de vídeos.")
        return

    hf_token = token_entry.get().strip() or load_config().hf_token
    if not hf_token:
        messagebox.showerror(
            "Erro",
            "Informe o token do Hugging Face para habilitar diarização.",
        )
        return

    def task() -> None:
        status.config(text="Processando...", fg="#1f4")
        try:
            outputs: list[Path] = []
            if isinstance(input_path, list):
                for file_path in input_path:
                    outputs.extend(
                        transcribe_path(
                            file_path, Path(output_path), hf_token=hf_token
                        )
                    )
            else:
                outputs = transcribe_path(input_path, Path(output_path), hf_token=hf_token)
            status.config(text=f"Concluído: {len(outputs)} arquivo(s).", fg="#1f4")
        except Exception as exc:
            status.config(text=f"Erro: {exc}", fg="#d33")

    threading.Thread(target=task, daemon=True).start()


def main() -> None:
    root = tk.Tk()
    root.title("Transcrip")
    root.geometry("680x420")
    root.resizable(False, False)

    state = AppState()
    config = load_config()

    tk.Label(root, text="Seleção de vídeos:").pack(anchor="w", padx=16, pady=(16, 4))
    input_frame = tk.Frame(root)
    input_frame.pack(fill="x", padx=16)
    input_label = tk.Label(input_frame, text="Nenhum vídeo selecionado.", anchor="w")
    input_label.pack(side="left", fill="x", expand=True)
    tk.Button(input_frame, text="Selecionar vídeos", command=lambda: pick_files(state, input_label)).pack(
        side="left", padx=4
    )
    tk.Button(
        input_frame,
        text="Selecionar pasta",
        command=lambda: pick_folder(state, input_label),
    ).pack(side="left")

    tk.Label(root, text="Pasta de saída:").pack(anchor="w", padx=16, pady=(16, 4))
    output_frame = tk.Frame(root)
    output_frame.pack(fill="x", padx=16)
    output_entry = tk.Entry(output_frame)
    output_entry.pack(side="left", fill="x", expand=True)
    tk.Button(
        output_frame,
        text="Selecionar",
        command=lambda: pick_output_folder(output_entry),
    ).pack(side="left", padx=4)
    tk.Button(
        output_frame,
        text="Abrir pasta",
        command=lambda: open_output_folder(output_entry),
    ).pack(side="left")

    status = tk.Label(root, text="Aguardando...", fg="#555")
    status.pack(anchor="w", padx=16, pady=(16, 4))

    tk.Label(root, text="Token do Hugging Face (para diarização):").pack(
        anchor="w", padx=16, pady=(16, 4)
    )
    token_frame = tk.Frame(root)
    token_frame.pack(fill="x", padx=16)
    token_entry = tk.Entry(token_frame)
    token_entry.pack(side="left", fill="x", expand=True)
    token_entry.insert(0, config.hf_token)
    tk.Button(
        token_frame,
        text="Salvar token",
        command=lambda: save_token(token_entry, status),
    ).pack(side="left", padx=4)

    tk.Button(
        root,
        text="Iniciar transcrição",
        command=lambda: run_transcription(state, output_entry, token_entry, status),
        bg="#2b7",
        fg="white",
        padx=8,
        pady=4,
    ).pack(pady=12)

    root.mainloop()


if __name__ == "__main__":
    main()
