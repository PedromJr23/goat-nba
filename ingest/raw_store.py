"""Camada raw: payload imutável em disco + log em DuckDB. Idempotente por (source, url, sha256)."""
import hashlib
import json
import pathlib
import uuid
from datetime import datetime, timezone

import duckdb

SCHEMA_SQL = (pathlib.Path(__file__).resolve().parent.parent / "sql" / "00_schemas.sql").read_text()


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def new_run_id():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:6]


class RawStore:
    def __init__(self, db_path, raw_dir):
        self.db_path = str(db_path)
        self.raw_dir = pathlib.Path(raw_dir)
        pathlib.Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def connect(self):
        return duckdb.connect(self.db_path)

    def init(self):
        con = self.connect()
        try:
            con.execute(SCHEMA_SQL)
        finally:
            con.close()

    def lookup(self, source, url):
        """Último fetch bem-sucedido (HTTP 200) para a URL, ou None. Serve de cache."""
        con = self.connect()
        try:
            row = con.execute(
                "SELECT raw_id, payload_path FROM raw.fetch_log "
                "WHERE source=? AND url=? AND http_status=200 ORDER BY fetched_at DESC LIMIT 1",
                [source, url],
            ).fetchone()
        finally:
            con.close()
        return {"raw_id": row[0], "payload_path": row[1]} if row else None

    def save(self, *, source, endpoint, url, params, status, payload, ext, run_id, terms_ref, note=None):
        """Grava payload (bytes) e registra no log. Retorna raw_id."""
        params_json = json.dumps(params, sort_keys=True, default=str)
        now = _now()
        if status != 200 or payload is None:
            raw_id = hashlib.sha256(f"{source}|{url}|{status}|{now.isoformat()}".encode()).hexdigest()[:16]
            self._insert(raw_id, run_id, source, endpoint, url, params_json, now, status, None, None, None, terms_ref, note)
            return raw_id

        sha = hashlib.sha256(payload).hexdigest()
        raw_id = hashlib.sha256(f"{source}|{url}|{sha}".encode()).hexdigest()[:16]
        path = self.raw_dir / source / sha[:2] / f"{sha}.{ext}"
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        con = self.connect()
        try:
            exists = con.execute("SELECT 1 FROM raw.fetch_log WHERE raw_id=?", [raw_id]).fetchone()
            if exists:  # mesmo conteúdo já registrado: apenas atualiza a data de verificação
                con.execute("UPDATE raw.fetch_log SET last_verified_at=? WHERE raw_id=?", [now, raw_id])
                return raw_id
        finally:
            con.close()
        self._insert(raw_id, run_id, source, endpoint, url, params_json, now, status, str(path), sha, len(payload), terms_ref, note)
        return raw_id

    def _insert(self, raw_id, run_id, source, endpoint, url, params_json, now, status, path, sha, size, terms_ref, note):
        con = self.connect()
        try:
            con.execute(
                "INSERT INTO raw.fetch_log VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                [raw_id, run_id, source, endpoint, url, params_json, now, status, path, sha, size, terms_ref, now, note],
            )
        finally:
            con.close()
