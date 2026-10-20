"""Loader for the synthetic Nimbus Dynamics corpus (Chapters 6, 35).

Reads a corpus directory containing ``manifest.json`` (the governance
record) plus markdown documents. Produces Document objects carrying full
provenance, and (via load_chunks) retrieval-ready Chunk objects using
structure-aware chunking.

The loader is deliberately strict: a manifest entry whose file is missing
raises, and a document missing from the manifest is never loaded. Silent
corpus drift is a context-quality failure (Chapter 5) — the loader makes
it loud instead.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

from .chunking import chunk_markdown
from .context import SourceRef
from .retrieval import Chunk


@dataclass
class Document:
    """A corpus document with provenance and its raw manifest entry."""

    doc_id: str
    text: str
    source: SourceRef
    path: str = ""
    metadata: dict = field(default_factory=dict)  # raw manifest entry

    @property
    def title(self) -> str:
        return self.source.title or self.doc_id


def default_corpus_dir() -> str:
    """Locate the synthetic corpus: env var override, else relative path.

    The default assumes commands run from the repository root (documented
    in docs/getting-started.md). Override with CE_CORPUS_DIR when needed.
    """
    env = os.environ.get("CE_CORPUS_DIR")
    return env if env else os.path.join("datasets", "synthetic", "corpus")


def load_corpus(corpus_dir: str | None = None) -> list:
    """Load all documents listed in the manifest, with provenance."""
    corpus_dir = corpus_dir or default_corpus_dir()
    manifest_path = os.path.join(corpus_dir, "manifest.json")
    with open(manifest_path, encoding="utf-8") as fh:
        manifest = json.load(fh)

    documents: list = []
    for entry in manifest["documents"]:
        doc_path = os.path.join(corpus_dir, entry["file"])
        if not os.path.exists(doc_path):
            raise FileNotFoundError(
                f"manifest lists {entry['file']!r} but the file is missing "
                f"in {corpus_dir!r} — corpus integrity check failed"
            )
        with open(doc_path, encoding="utf-8") as fh:
            text = fh.read()
        source = SourceRef(
            source_id=entry["id"],
            title=entry.get("title", ""),
            version=str(entry.get("version", "")),
            effective_date=entry.get("effective_date", ""),
            access=entry.get("access", "public"),
            owner=entry.get("owner", ""),
        )
        documents.append(
            Document(
                doc_id=entry["id"],
                text=text,
                source=source,
                path=doc_path,
                metadata=dict(entry),
            )
        )
    return documents


def load_chunks(corpus_dir: str | None = None, max_words: int = 160) -> list:
    """Load the corpus as retrieval-ready Chunks (structure-aware)."""
    chunks: list = []
    for doc in load_corpus(corpus_dir):
        pieces = chunk_markdown(doc.text, max_words=max_words)
        for ordinal, piece in enumerate(pieces):
            body = piece["text"]
            heading = piece["heading"]
            text = f"{heading}. {body}" if heading else body
            chunks.append(
                Chunk(
                    chunk_id=f"{doc.doc_id}-v{doc.source.version}-c{ordinal:02d}",
                    text=text,
                    source=doc.source,
                    metadata={
                        "ordinal": ordinal,
                        "heading": heading,
                        "title": doc.title,
                        "synthetic_injection": bool(
                            doc.metadata.get("synthetic_injection", False)
                        ),
                    },
                )
            )
    return chunks
