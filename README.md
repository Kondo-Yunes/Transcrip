# Transcrip

Aplicativo simples para transcrição de audiências judiciais em português com diarização (identificação de interlocutor) e timestamps. O foco é rodar localmente em Windows 11 com GPU NVIDIA (ex.: RTX 4060 8GB), oferecendo:

- Transcrição jurídica em português com ordenação por contexto jurídico (via modelo WhisperX).
- Timestamps por segmento e identificação de interlocutor (diarização).
- Interface para uso leigo (GUI) com upload de vídeos e geração de `.txt` diarizado.
- Processamento em lote: pasta com vários vídeos, gerando `.txt` com o mesmo nome do vídeo.

> **Observação:** A diarização usa `pyannote.audio` via `whisperx` e requer um token do Hugging Face. Defina a variável de ambiente `HF_TOKEN` antes de executar.

## Requisitos

- Windows 11
- NVIDIA GPU com CUDA (ex.: RTX 4060 8GB)
- Python 3.10+ (recomendado 3.11)
- Drivers NVIDIA + CUDA Toolkit compatível

## Instalação (para quem vai usar o app)

Se você recebeu um instalador **Transcrip-Setup.exe**, basta:

1. Dar dois cliques no arquivo.
2. Seguir o assistente de instalação.
3. Abrir o programa pelo atalho **Transcrip** no Menu Iniciar.

> Não é necessário usar terminal ou comandos.

## Instalação (para quem vai montar o instalador)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -U pip
pip install -e .
```

## Uso (GUI)

1. Abra o aplicativo (atalho ou executável).
2. Clique em **Selecionar vídeos** para escolher vários arquivos, ou **Selecionar pasta** para processar um lote.
3. Clique em **Selecionar** para escolher a pasta de saída.
4. Cole o **token do Hugging Face** e clique em **Salvar token** (fica guardado localmente).
5. Clique em **Iniciar transcrição**.
6. Use **Abrir pasta** para abrir os resultados.

## Uso (CLI)

Transcrever um único vídeo:

```bash
transcrip --input "C:\audiencias\audio1.mp4" --output "C:\audiencias\transcricoes"
```

Transcrever todos os vídeos de uma pasta:

```bash
transcrip --input "C:\audiencias\lote" --output "C:\audiencias\transcricoes"
```

## Token do Hugging Face (o que é e como conseguir)

O **token do Hugging Face** é uma chave que permite baixar modelos necessários para diarização (identificação de interlocutores) via `pyannote`. Sem ele, a diarização não funciona.

### Como gerar o token

1. Crie uma conta em https://huggingface.co/
2. Acesse https://huggingface.co/settings/tokens
3. Clique em **New token** e gere um token do tipo **Read**.
4. Copie o token gerado.

### Como colocar o token no programa

- Abra a GUI, cole o token no campo **Token do Hugging Face** e clique em **Salvar token**.
- O token fica salvo localmente em `C:\\Users\\<seu_usuario>\\.transcrip\\config.json`.
- Você pode substituir o token a qualquer momento, colando um novo e salvando novamente.

## Gerar executável (opcional)

Para criar um instalador simples local, você pode empacotar com `pyinstaller`:

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole -n Transcrip transcrip/gui.py
```

O executável ficará em `dist/Transcrip.exe`.

## Gerar instalador (opcional)

Se você quiser fornecer um instalador clicável para o usuário final, use o Inno Setup:

1. Instale o Inno Setup: https://jrsoftware.org/isinfo.php
2. (Opcional) Monte a pasta `installer/deps` com instaladores e utilitários para instalação automática:
   - `installer/deps/ffmpeg/` com `ffmpeg.exe` e dependências.
   - `installer/deps/cuda/cuda_installer.exe` (CUDA Toolkit).
   - `installer/deps/vc_redist.x64.exe` (Microsoft Visual C++ Redistributable).
3. Abra o arquivo `installer/Transcrip.iss`.
4. Clique em **Build > Compile**.
5. O instalador ficará em `installer/dist/Transcrip-Setup.exe`.

### Observações importantes sobre dependências automáticas

- **Python** é empacotado dentro do `Transcrip.exe` gerado pelo PyInstaller, então o usuário não precisa instalar Python separadamente.
- **FFmpeg** pode ser empacotado dentro da pasta do app (veja `installer/deps/ffmpeg`).
- **CUDA Toolkit e drivers NVIDIA** exigem permissões de administrador e podem solicitar reinicialização. O script do instalador roda esses instaladores se eles estiverem em `installer/deps/`.
- Em ambientes corporativos, os drivers NVIDIA podem precisar de aprovação da TI.
