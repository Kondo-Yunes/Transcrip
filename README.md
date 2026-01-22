# Transcrição com identificação de interlocutores

Este projeto fornece um aplicativo desktop e um script CLI para transcrever áudio em texto com timestamps e diarização (identificação de interlocutores) usando WhisperX.

## Requisitos

- Python 3.10+
- GPU CUDA recomendada (o aplicativo desktop exige GPU)
- Token do Hugging Face com acesso aos modelos de diarização

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Instalação do PyTorch (GPU)

O PyTorch precisa ser instalado pelo índice correto. Use um dos comandos abaixo:

**CUDA 12.1 (recomendado para GPUs recentes):**

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

**Somente CPU (se você não tiver GPU):**

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Dependência do FFmpeg

O WhisperX requer o FFmpeg instalado no sistema:

- **Windows (Chocolatey):** `choco install ffmpeg`
- **macOS (Homebrew):** `brew install ffmpeg`
- **Linux (Debian/Ubuntu):** `sudo apt-get install ffmpeg`

## Uso

Defina o token do Hugging Face:

```bash
export HF_TOKEN=seu_token
```

Aplicativo desktop (com seleção de arquivo):

```bash
python desktop_app.py
```

Execute a transcrição via CLI:

```bash
python transcribe.py caminho/para/audio.wav --model medium --output transcricao.txt
```

Saída em JSON:

```bash
python transcribe.py caminho/para/audio.wav --output transcricao.json
```

## Observações

- O script exige diarização. Se você não informar `HF_TOKEN` ou `--hf-token`, ele irá encerrar com erro.
- Ajuste `--device` para `cpu` se não houver GPU.
- O botão **Diagnóstico** no aplicativo informa se Torch, CUDA e FFmpeg estão disponíveis.

## Instalação como aplicativo

Para gerar um executável (ex.: Windows/macOS/Linux), use o PyInstaller:

```bash
pyinstaller --onefile --windowed desktop_app.py
```

O executável ficará na pasta `dist/`. Use-o como um programa comum, sem precisar abrir o Python.

## Se nada funcionar

1. Abra o aplicativo e clique em **Diagnóstico** para ver o que está faltando.
2. Garanta que o `torch` foi instalado pelo índice correto (CUDA ou CPU).
3. Instale o FFmpeg, pois sem ele o WhisperX não carrega áudio.
