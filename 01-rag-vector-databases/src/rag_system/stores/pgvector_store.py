from __future__ import annotations

import json
from uuid import uuid4

import psycopg
from pgvector.psycopg import register_vector
from psycopg import sql

from rag_system.chunking import DocumentChunk
from rag_system.config import PgVectorConfig
from rag_system.embeddings import create_embeddings
from rag_system.stores.base import RetrievedDocument, VectorStore


class PgVectorStore(VectorStore):
    name = "pgvector"

    def __init__(self, config: PgVectorConfig, embedding_config):
        self.config = config
        self._embeddings = create_embeddings(embedding_config)
        self._conn = psycopg.connect(
            host=config.host,
            port=config.port,
            dbname=config.database,
            user=config.user,
            password=config.password,
            autocommit=True,
        )
        register_vector(self._conn)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        dim = len(self._embeddings.embed_query("dimension probe"))
        table = self.config.table_name
        with self._conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata JSONB NOT NULL DEFAULT '{{}}',
                    embedding vector({dim}) NOT NULL
                )
                """
            )

    def add_chunks(self, chunks: list[DocumentChunk]) -> int:
        if not chunks:
            return 0

        texts = [chunk.text for chunk in chunks]
        vectors = self._embeddings.embed_documents(texts)

        with self._conn.cursor() as cur:
            for chunk, vector in zip(chunks, vectors):
                cur.execute(
                    sql.SQL(
                        "INSERT INTO {} (id, content, metadata, embedding) VALUES (%s, %s, %s, %s)"
                    ).format(sql.Identifier(self.config.table_name)),
                    (
                        str(uuid4()),
                        chunk.text,
                        json.dumps(chunk.metadata),
                        vector,
                    ),
                )
        return len(chunks)

    def search(self, query: str, top_k: int = 5) -> list[RetrievedDocument]:
        query_vector = self._embeddings.embed_query(query)
        with self._conn.cursor() as cur:
            cur.execute(
                sql.SQL(
                    """
                    SELECT content, metadata, 1 - (embedding <=> %s::vector) AS score
                    FROM {}
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """
                ).format(sql.Identifier(self.config.table_name)),
                (query_vector, query_vector, top_k),
            )
            rows = cur.fetchall()

        return [
            RetrievedDocument(
                text=row[0],
                metadata=row[1] if isinstance(row[1], dict) else json.loads(row[1]),
                score=float(row[2]),
                store=self.name,
            )
            for row in rows
        ]

    def count(self) -> int:
        with self._conn.cursor() as cur:
            cur.execute(
                sql.SQL("SELECT COUNT(*) FROM {}").format(
                    sql.Identifier(self.config.table_name)
                )
            )
            return int(cur.fetchone()[0])

    def close(self) -> None:
        self._conn.close()