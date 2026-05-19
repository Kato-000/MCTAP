"""
memory.py — RAG store for memorizing and retrieving successful attacks

Responsibilities of this module:
  - Store past successful attacks as embedding vectors (.pt files)
  - Retrieve top-k results for a new goal using cosine similarity

Storage format — one file per VulnCategory:
    data/memory/ENC_EVASION.pt
    data/memory/PERSONA_ROLEPLAY.pt
    ...

Each .pt file contains:
    {
        "embeddings": Tensor (N, 768)  <- embedding of goal text
        "data":       List[dict]       <- corresponding attack records
    }

Contents of data[i]:
    {
        "adversarial_prompt": str   <- successful adversarial prompt
        "goal":               str   <- attack goal
        "score":              int   <- evaluation score (3 or 4)
        "vuln_category":      str   <- vulnerability category used
    }
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional
from typing_extensions import Self

import torch as t
from jaxtyping import Float
from loguru import logger
from openai import OpenAI
from torch import Tensor

from src.models import Model
from src.vuln import VulnCategory


class Memory:
    """RAG store for a single VulnCategory.

    Stores past successful attacks as embedding vectors and retrieves
    the top-k most semantically similar examples for a given goal.

    Usage:
        # Create new
        mem = Memory.new("data/memory/PERSONA_ROLEPLAY.pt", embedding_model)

        # Load from existing file
        mem = Memory.from_file("data/memory/PERSONA_ROLEPLAY.pt", embedding_model)

        # Add a successful attack (saved to .pt immediately)
        mem.add(key=goal, new_data={...})

        # Retrieve similar successful examples for a goal
        examples = mem.retrieve(key=goal, k=3)
    """

    def __init__(
        self,
        embeddings: Float[Tensor, "n_records d_model"],
        data: List[dict],
        memory_file: str,
        embedding_model: Model,
    ) -> None:
        self.embeddings    = embeddings
        self.data          = data
        self.memory_file   = memory_file
        self.embedding_model = embedding_model

    @classmethod
    def from_file(cls, memory_file: str, embedding_model: Model) -> Self:
        """Restore a Memory instance from a saved .pt file."""
        checkpoint = t.load(memory_file)
        return cls(
            embeddings=checkpoint["embeddings"],
            data=checkpoint["data"],
            memory_file=memory_file,
            embedding_model=embedding_model,
        )

    @classmethod
    def new(cls, memory_file: str, embedding_model: Model, d_model: int = 768) -> "Memory":
        """Create a new empty Memory instance."""
        return cls(
            embeddings=t.zeros(0, d_model),
            data=[],
            memory_file=memory_file,
            embedding_model=embedding_model,
        )

    def save(self) -> None:
        """Write the current state to a .pt file."""
        t.save({"embeddings": self.embeddings, "data": self.data}, self.memory_file)

    def embed(self, sentence: str) -> Optional[Float[Tensor, "d_model"]]:
        """Vectorize text using the embedding model. Returns None on failure."""
        try:
            client = OpenAI(
                base_url=self.embedding_model.api_base,
                api_key=self.embedding_model.api_key,
            )
            return t.tensor(
                client.embeddings.create(
                    input=[sentence], model=self.embedding_model.model_name
                ).data[0].embedding,
                device=self.embeddings.device,
                dtype=self.embeddings.dtype if self.embeddings.numel() > 0 else t.float32,
            )
        except Exception as e:
            logger.warning(f"[Memory] Embedding failed: {e}")
            return None

    def add(self, key: str, new_data: dict) -> None:
        """Add a successful attack and immediately save to file.

        Args:
            key:      Text used as the embedding key (typically the goal)
            new_data: Attack record dict to store
        """
        embed = self.embed(key)
        if embed is None:
            logger.warning("[Memory] Skipping add due to embedding failure")
            return
        if self.embeddings.numel() == 0:
            self.embeddings = embed.unsqueeze(0)
        else:
            self.embeddings = t.cat([self.embeddings, embed.unsqueeze(0)], dim=0)
        self.data.append(new_data)
        self.save()

    def retrieve(self, key: str, k: int = 3) -> List[dict]:
        """Return the top-k past attack records most semantically similar to key.

        Searches by cosine similarity. Returns [] if memory is empty or embedding fails.
        """
        if self.embeddings.numel() == 0 or len(self.data) == 0:
            return []
        k = min(k, len(self.data))
        key_embed = self.embed(key)
        if key_embed is None:
            logger.warning("[Memory] Skipping retrieve due to embedding failure")
            return []
        best_indices = (
            t.cosine_similarity(self.embeddings, key_embed.unsqueeze(0), dim=-1)
            .topk(k=k)
            .indices.tolist()
        )
        return [self.data[idx] for idx in best_indices]

    def __len__(self) -> int:
        return len(self.data)


class MemoryStore:
    """Per-category Memory manager.

    Maintains one Memory instance per VulnCategory, each backed by its own
    .pt file. This allows the system to retrieve examples that were generated
    using the same attack strategy as the current attempt.

    File layout:
        {memory_dir}/ENC_EVASION.pt
        {memory_dir}/DIRECT_OVERRIDE.pt
        {memory_dir}/PERSONA_ROLEPLAY.pt
        {memory_dir}/INTENT_CONCEAL.pt
        {memory_dir}/PROGRESSIVE_MANIP.pt
        {memory_dir}/CONTEXT_INJECTION.pt

    Usage:
        store = MemoryStore.load("data/memory", embedding_model)

        # Retrieve examples for a specific category
        examples = store.retrieve(goal, category=VulnCategory.PERSONA_ROLEPLAY, k=3)

        # Save a successful attack under its category
        store.add(goal, data={...}, category=VulnCategory.PERSONA_ROLEPLAY)
    """

    def __init__(self, memories: Dict[VulnCategory, Memory]) -> None:
        self._memories = memories

    @classmethod
    def load(cls, memory_dir: str, embedding_model: Model) -> "MemoryStore":
        """Load (or create) one Memory per VulnCategory from memory_dir.

        If a category's .pt file already exists it is loaded; otherwise a
        new empty Memory is created (and written on first add).
        """
        dirpath = Path(memory_dir)
        dirpath.mkdir(parents=True, exist_ok=True)

        memories: Dict[VulnCategory, Memory] = {}
        for cat in VulnCategory:
            fpath = dirpath / f"{cat.value}.pt"
            if fpath.exists():
                logger.info(f"[MemoryStore] Loading {fpath}")
                memories[cat] = Memory.from_file(str(fpath), embedding_model)
            else:
                logger.info(f"[MemoryStore] Creating new memory for {cat.value} at {fpath}")
                memories[cat] = Memory.new(str(fpath), embedding_model)

        return cls(memories)

    def retrieve(
        self,
        goal: str,
        category: VulnCategory,
        k: int = 3,
    ) -> List[str]:
        """Return up to k prompt hints for the given category.

        Records store a unified ``conversation`` list regardless of category:
            [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]

        The returned hint joins all user turns with " ||| " so the attacker LM
        sees the full multi-turn structure (or the single prompt for other categories).
        Falls back to ``adversarial_prompt`` for older records without ``conversation``.
        """
        mem = self._memories[category]
        records = mem.retrieve(key=goal, k=k)
        results = []
        for r in records:
            if r.get("conversation"):
                user_turns = [
                    msg["content"]
                    for msg in r["conversation"]
                    if msg.get("role") == "user"
                ]
                results.append(" ||| ".join(user_turns))
            else:
                results.append(r.get("adversarial_prompt", ""))
        return results

    def add(self, goal: str, data: dict, category: VulnCategory) -> None:
        """Save a successful attack record under the given category.

        Args:
            goal:     The attack goal used as the embedding key
            data:     Full attack record dict (adversarial_prompt, score, etc.)
            category: The VulnCategory this attack belongs to
        """
        self._memories[category].add(key=goal, new_data=data)
        logger.info(
            f"[MemoryStore] Saved to {category.value} "
            f"(total: {len(self._memories[category])})"
        )

    def stats(self) -> Dict[str, int]:
        """Return the number of stored records per category."""
        return {cat.value: len(mem) for cat, mem in self._memories.items()}
