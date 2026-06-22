from __future__ import annotations

from langchain_huggingface import HuggingFaceEmbeddings

from rag_system.config import EmbeddingsConfig


def create_embeddings(config: EmbeddingsConfig) -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=config.model_name,
        model_kwargs={"device": config.device},
        encode_kwargs={"normalize_embeddings": True},
    )