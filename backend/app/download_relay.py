"""Fila de downloads na Oracle — worker na LAN baixa e envia o arquivo."""

from __future__ import annotations

import json
import sqlite3
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from app.config import settings

_LOCK = threading.Lock()
# Sem heartbeat do worker, job claimed volta para pending (evita órfão após restart).
_CLAIM_LEASE_SEC = 3 * 60
_PENDING_WORKER_TIMEOUT_SEC = 120


def _db_path() -> Path:
    root = Path(settings.downloads_dir)
    if not root.is_absolute():
        root = Path(__file__).resolve().parent.parent / root
    root.mkdir(parents=True, exist_ok=True)
    return root / "download_relay.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_db_path()), timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    with _LOCK:
        conn = _connect()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS download_jobs (
                    id TEXT PRIMARY KEY,
                    video_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    worker_id TEXT,
                    claimed_at REAL,
                    error TEXT,
                    client_meta_json TEXT,
                    user_id TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_download_jobs_status ON download_jobs(status)"
            )
            try:
                conn.execute(
                    "ALTER TABLE download_jobs ADD COLUMN priority INTEGER NOT NULL DEFAULT 0"
                )
            except sqlite3.OperationalError:
                pass
            conn.commit()
        finally:
            conn.close()


_init_db()


def _open_job_id_for_video(video_id: str) -> str | None:
    with _LOCK:
        conn = _connect()
        try:
            row = conn.execute(
                """
                SELECT id FROM download_jobs
                WHERE video_id = ? AND status = 'pending'
                ORDER BY created_at ASC
                LIMIT 1
                """,
                (video_id,),
            ).fetchone()
        finally:
            conn.close()
    return str(row["id"]) if row else None


def enqueue(
    video_id: str,
    *,
    user_id: str | None = None,
    client_meta: dict[str, Any] | None = None,
) -> str:
    with _LOCK:
        conn = _connect()
        try:
            _requeue_stale_claims(conn)
            conn.commit()
        finally:
            conn.close()

    priority = 0
    if client_meta and client_meta.get("downloadPriority") is not None:
        try:
            priority = int(client_meta["downloadPriority"])
        except (TypeError, ValueError):
            priority = 0

    existing = _open_job_id_for_video(video_id)
    if existing:
        _bump_job_priority(existing, priority)
        return existing
    job_id = uuid.uuid4().hex
    now = time.time()
    meta_json = json.dumps(client_meta or {}, ensure_ascii=False)
    with _LOCK:
        conn = _connect()
        try:
            conn.execute(
                """
                INSERT INTO download_jobs
                (id, video_id, status, client_meta_json, user_id, priority, created_at, updated_at)
                VALUES (?, ?, 'pending', ?, ?, ?, ?, ?)
                """,
                (job_id, video_id, meta_json, user_id, priority, now, now),
            )
            conn.commit()
        finally:
            conn.close()
    return job_id


def _bump_job_priority(job_id: str, priority: int) -> None:
    if priority <= 0:
        return
    now = time.time()
    with _LOCK:
        conn = _connect()
        try:
            conn.execute(
                """
                UPDATE download_jobs
                SET priority = CASE WHEN ? > priority THEN ? ELSE priority END,
                    updated_at = ?
                WHERE id = ? AND status IN ('pending', 'claimed')
                """,
                (priority, priority, now, job_id),
            )
            conn.commit()
        finally:
            conn.close()


def _requeue_stale_claims(conn: sqlite3.Connection) -> None:
    cutoff = time.time() - _CLAIM_LEASE_SEC
    now = time.time()
    conn.execute(
        """
        UPDATE download_jobs
        SET status = 'pending', worker_id = NULL, claimed_at = NULL, updated_at = ?
        WHERE status = 'claimed' AND updated_at < ?
        """,
        (now, cutoff),
    )


def release_worker_claims(*, worker_id: str) -> int:
    """Devolve jobs claimed deste worker para pending (ex.: ao reiniciar o serviço)."""
    now = time.time()
    with _LOCK:
        conn = _connect()
        try:
            conn.execute(
                """
                UPDATE download_jobs
                SET status = 'pending', worker_id = NULL, claimed_at = NULL, updated_at = ?
                WHERE status = 'claimed' AND worker_id = ?
                """,
                (now, worker_id),
            )
            n = conn.total_changes
            conn.commit()
        finally:
            conn.close()
    return n


def touch_job(job_id: str, *, worker_id: str) -> bool:
    """Heartbeat — estende o lease enquanto o worker baixa/envia."""
    now = time.time()
    with _LOCK:
        conn = _connect()
        try:
            conn.execute(
                """
                UPDATE download_jobs
                SET updated_at = ?
                WHERE id = ? AND status = 'claimed' AND worker_id = ?
                """,
                (now, job_id, worker_id),
            )
            ok = conn.total_changes == 1
            conn.commit()
        finally:
            conn.close()
    return ok


def claim_next(*, worker_id: str) -> dict[str, Any] | None:
    now = time.time()
    with _LOCK:
        conn = _connect()
        try:
            _requeue_stale_claims(conn)
            row = conn.execute(
                """
                SELECT id, video_id, client_meta_json, user_id
                FROM download_jobs
                WHERE status = 'pending'
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
                """
            ).fetchone()
            if not row:
                return None
            conn.execute(
                """
                UPDATE download_jobs
                SET status = 'claimed', worker_id = ?, claimed_at = ?, updated_at = ?
                WHERE id = ? AND status = 'pending'
                """,
                (worker_id, now, now, row["id"]),
            )
            if conn.total_changes != 1:
                conn.commit()
                return None
            conn.commit()
        finally:
            conn.close()

    meta: dict[str, Any] = {}
    try:
        meta = json.loads(row["client_meta_json"] or "{}")
    except (TypeError, ValueError):
        pass
    return {
        "jobId": row["id"],
        "videoId": row["video_id"],
        "clientMeta": meta,
        "userId": row["user_id"],
    }


def get_job(job_id: str) -> dict[str, Any] | None:
    with _LOCK:
        conn = _connect()
        try:
            row = conn.execute(
                "SELECT * FROM download_jobs WHERE id = ?", (job_id,)
            ).fetchone()
        finally:
            conn.close()
    if not row:
        return None
    return dict(row)


def mark_completed(job_id: str, *, worker_id: str | None = None) -> None:
    now = time.time()
    with _LOCK:
        conn = _connect()
        try:
            conn.execute(
                """
                UPDATE download_jobs
                SET status = 'completed', error = NULL, updated_at = ?
                WHERE id = ? AND status IN ('claimed', 'pending')
                """,
                (now, job_id),
            )
            conn.commit()
        finally:
            conn.close()


def mark_failed(job_id: str, error: str, *, worker_id: str | None = None) -> None:
    now = time.time()
    msg = (error or "falha")[:2000]
    with _LOCK:
        conn = _connect()
        try:
            conn.execute(
                """
                UPDATE download_jobs
                SET status = 'failed', error = ?, updated_at = ?
                WHERE id = ?
                """,
                (msg, now, job_id),
            )
            conn.commit()
        finally:
            conn.close()


def wait_for_job(
    job_id: str,
    *,
    timeout_sec: float = 15 * 60,
    poll_sec: float = 0.8,
) -> dict[str, Any]:
    """Bloqueia até completed/failed ou timeout."""
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        with _LOCK:
            conn = _connect()
            try:
                _requeue_stale_claims(conn)
                conn.commit()
            finally:
                conn.close()
        job = get_job(job_id)
        if not job:
            raise RuntimeError("job não encontrado")
        status = job.get("status")
        if status == "completed":
            return job
        if status == "failed":
            raise RuntimeError(job.get("error") or "download remoto falhou")
        if status == "pending":
            created = float(job.get("created_at") or 0)
            if created and time.time() - created > _PENDING_WORKER_TIMEOUT_SEC:
                msg = (
                    "Worker LAN não pegou o download (serviço parado ou bloqueio Cloudflare na API). "
                    "Reinicie rutsfy-worker na LAN."
                )
                mark_failed(job_id, msg)
                raise RuntimeError(msg)
        if status == "claimed":
            updated = float(job.get("updated_at") or 0)
            if updated and time.time() - updated > _CLAIM_LEASE_SEC + 30:
                # Órfão — wait_for_job força requeue na próxima volta do loop
                with _LOCK:
                    conn = _connect()
                    try:
                        _requeue_stale_claims(conn)
                        conn.commit()
                    finally:
                        conn.close()
                continue
        time.sleep(poll_sec)
    raise TimeoutError("tempo esgotado aguardando download na LAN")
