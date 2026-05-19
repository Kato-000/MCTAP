"""
utils.py — Utility functions

Responsibilities of this module:
  - File I/O (JSONL append, trace save, summary update)
  - Text extraction (normalization of DSPy LM responses)
  - GPU status logging
"""

from __future__ import annotations

import json
from pathlib import Path

import torch as t
from loguru import logger


# =============================================================================
# File I/O
# =============================================================================

def log_jsonl(filepath: str | Path, data: dict) -> None:
    """Append a dict as a single JSON line to a JSONL file."""
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def save_trace(filepath: str | Path, data: dict) -> None:
    """Save the full attack tree to a JSON file (overwrite)."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_json_safe(path: Path, default):
    """Safely load a JSON file. Returns default if missing, empty, or corrupted."""
    if not path.exists():
        return default
    try:
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            logger.warning(f"[!] {path} is empty. Initializing with default value.")
            return default
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.warning(f"[!] Failed to parse JSON in {path} ({e}). Initializing with default value.")
        return default


def update_summary(summary_file: Path, entry: dict, success: bool) -> None:
    """Update the aggregated summary for all goals and write to success/failure split files.

    Recovers safely even if files are empty or corrupted.
    """
    # 1. Unified summary (all goals)
    summary = _load_json_safe(
        summary_file,
        default={"total_success": 0, "total_fail": 0, "total": 0, "results": []},
    )
    summary["total"] += 1
    if success:
        summary["total_success"] += 1
    else:
        summary["total_fail"] += 1
    summary["results"].append(entry)
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # 2. Split summary by success/failure
    stem = summary_file.stem
    split_file = (
        summary_file.parent / f"{stem}_success_only.json"
        if success
        else summary_file.parent / f"{stem}_fails_only.json"
    )
    split = _load_json_safe(split_file, default={"count": 0, "results": []})
    split["count"] += 1
    split["results"].append(entry)
    with open(split_file, "w", encoding="utf-8") as f:
        json.dump(split, f, ensure_ascii=False, indent=2)


# =============================================================================
# Text extraction
# =============================================================================

def extract_response_text(response) -> str:
    """Extract a string from a DSPy LM response.

    Handles all return formats (list, dict, str) that DSPy may produce.
    """
    if isinstance(response, list) and len(response) > 0:
        item = response[0]
        if isinstance(item, dict) and "text" in item:
            return item["text"]
        elif isinstance(item, str):
            return item
        else:
            return str(item)
    elif isinstance(response, dict) and "text" in response:
        return response["text"]
    elif isinstance(response, str):
        return response
    else:
        return str(response)


# =============================================================================
# GPU status logging
# =============================================================================

def check_gpu_status() -> None:
    """Log CUDA availability and GPU memory usage."""
    if t.cuda.is_available():
        device_name = t.cuda.get_device_name(0)
        allocated   = t.cuda.memory_allocated(0) / 1024**3
        reserved    = t.cuda.memory_reserved(0) / 1024**3
        total       = t.cuda.get_device_properties(0).total_memory / 1024**3
        logger.info(f"[GPU] Device: {device_name}")
        logger.info(
            f"[GPU] Memory: {allocated:.2f}GB allocated / "
            f"{reserved:.2f}GB reserved / {total:.2f}GB total"
        )
    else:
        logger.warning("[GPU] CUDA is NOT available - running on CPU!")
