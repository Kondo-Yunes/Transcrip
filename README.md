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

## Instalação como aplicativo

Para gerar um executável (ex.: Windows/macOS/Linux), use o PyInstaller:

```bash
pyinstaller --onefile --windowed desktop_app.py
```

O executável ficará na pasta `dist/`. Use-o como um programa comum, sem precisar abrir o Python.
