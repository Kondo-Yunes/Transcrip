from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


CONFIG_DIR = Path.home() / ".transcrip"
CONFIG_PATH = CONFIG_DIR / "config.json"


@dataclass
class AppConfig:
    hf_token: str = ""


def load_config() -> AppConfig:
    if not CONFIG_PATH.exists():
        return AppConfig()
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return AppConfig()
    return AppConfig(hf_token=str(data.get("hf_token", "")))


def save_config(config: AppConfig) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps({"hf_token": config.hf_token}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
