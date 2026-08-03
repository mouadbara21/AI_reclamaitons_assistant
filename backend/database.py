"""
Database layer for PortNet Souscription — SQLite version.

Uses SQLite for maximum portability (no Docker dependency for the demo).
Simulates PortNet's real architecture:
- Documents stored on a file server (local storage/documents/ folder)
- GUIDs stored in the database referencing the physical files
- Validation reports stored as JSON text for flexible querying

Tables:
  souscriptions  — one row per subscription attempt
  documents      — one row per uploaded file, linked by souscription_id
"""

import sqlite3
import uuid
import json
import os
from typing import Optional
from datetime import datetime, timezone

# ─── Database path ────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "storage", "portnet_souscription.db")


def _get_conn() -> sqlite3.Connection:
    """Get a SQLite connection with row_factory for dict-like access."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ─── Schema initialisation ───────────────────────────────────────────

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS souscriptions (
    id                TEXT PRIMARY KEY,
    raison_sociale    TEXT,
    ice               TEXT,
    rc_number         TEXT,
    rc_city           TEXT,
    if_number         TEXT,
    tp_number         TEXT,
    siege_social      TEXT,
    gerant_nom        TEXT,
    gerant_prenom     TEXT,
    gerant_cin        TEXT,
    rib               TEXT,
    overall_status    TEXT,
    validation_report TEXT,
    rejection_reasons TEXT,
    created_at        TEXT
);

CREATE TABLE IF NOT EXISTS documents (
    id                TEXT PRIMARY KEY,
    souscription_id   TEXT REFERENCES souscriptions(id) ON DELETE CASCADE,
    guid              TEXT UNIQUE NOT NULL,
    original_filename TEXT,
    document_slot     TEXT,
    detected_type     TEXT,
    file_path         TEXT,
    file_size_bytes   INTEGER,
    doc_status        TEXT,
    created_at        TEXT
);

CREATE INDEX IF NOT EXISTS idx_documents_souscription
    ON documents(souscription_id);
"""


def init_db():
    """Create tables if they don't exist. Safe to call multiple times."""
    conn = _get_conn()
    conn.executescript(_SCHEMA_SQL)
    conn.commit()
    conn.close()
    print(f"[DB] SQLite database initialized at {DB_PATH}")


# ─── CRUD helpers ─────────────────────────────────────────────────────

def insert_souscription(
    raison_sociale: str,
    ice: str,
    rc_number: str,
    rc_city: str,
    if_number: str,
    tp_number: str,
    siege_social: str,
    gerant_nom: str,
    gerant_prenom: str,
    gerant_cin: str,
    rib: str,
) -> str:
    """Insert a new souscription row and return its UUID as string."""
    souscription_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    conn = _get_conn()
    conn.execute(
        """
        INSERT INTO souscriptions
            (id, raison_sociale, ice, rc_number, rc_city, if_number,
             tp_number, siege_social, gerant_nom, gerant_prenom,
             gerant_cin, rib, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (souscription_id, raison_sociale, ice, rc_number, rc_city,
         if_number, tp_number, siege_social, gerant_nom, gerant_prenom,
         gerant_cin, rib, now),
    )
    conn.commit()
    conn.close()
    return souscription_id


def insert_document(
    souscription_id: str,
    guid: str,
    original_filename: str,
    document_slot: str,
    file_path: str,
    file_size_bytes: int,
) -> str:
    """Insert a document row and return its UUID."""
    doc_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    conn = _get_conn()
    conn.execute(
        """
        INSERT INTO documents
            (id, souscription_id, guid, original_filename, document_slot,
             file_path, file_size_bytes, created_at)
        VALUES (?,?,?,?,?,?,?,?)
        """,
        (doc_id, souscription_id, guid, original_filename, document_slot,
         file_path, file_size_bytes, now),
    )
    conn.commit()
    conn.close()
    return doc_id


def update_souscription_result(
    souscription_id: str,
    overall_status: str,
    validation_report: dict,
    rejection_reasons: list,
):
    """Store the pipeline result in the souscription row."""
    conn = _get_conn()
    conn.execute(
        """
        UPDATE souscriptions
        SET overall_status    = ?,
            validation_report = ?,
            rejection_reasons = ?
        WHERE id = ?
        """,
        (
            overall_status,
            json.dumps(validation_report, ensure_ascii=False),
            json.dumps(rejection_reasons, ensure_ascii=False),
            souscription_id,
        ),
    )
    conn.commit()
    conn.close()


def update_document_result(
    doc_guid: str,
    detected_type: str,
    doc_status: str,
):
    """Update a document row with classification and status."""
    conn = _get_conn()
    conn.execute(
        """
        UPDATE documents
        SET detected_type = ?, doc_status = ?
        WHERE guid = ?
        """,
        (detected_type, doc_status, doc_guid),
    )
    conn.commit()
    conn.close()


def get_souscription(souscription_id: str) -> Optional[dict]:
    """Fetch a souscription with its documents."""
    conn = _get_conn()

    row = conn.execute(
        "SELECT * FROM souscriptions WHERE id = ?",
        (souscription_id,),
    ).fetchone()

    if not row:
        conn.close()
        return None

    result = dict(row)

    # Parse JSON fields
    if result.get("validation_report"):
        try:
            result["validation_report"] = json.loads(result["validation_report"])
        except (json.JSONDecodeError, TypeError):
            pass

    if result.get("rejection_reasons"):
        try:
            result["rejection_reasons"] = json.loads(result["rejection_reasons"])
        except (json.JSONDecodeError, TypeError):
            result["rejection_reasons"] = []

    # Fetch related documents
    docs = conn.execute(
        """
        SELECT * FROM documents
        WHERE souscription_id = ?
        ORDER BY created_at
        """,
        (souscription_id,),
    ).fetchall()

    result["documents"] = [dict(d) for d in docs]

    conn.close()
    return result
