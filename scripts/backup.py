"""Automated database backup, verification, and restoration CLI tool.

Supports consistent SQLite backups using SQLite's online backup API,
atomic file writes, integrity verification (PRAGMA integrity_check, foreign_key_check),
SHA-256 manifest generation, safe restoration with collision prevention,
and metadata listing.

Usage:
    python scripts/backup.py backup [--db data/trainer.db] [--dir backups/]
    python scripts/backup.py verify backups/backup_20261017_120000.db
    python scripts/backup.py restore backups/backup_20261017_120000.db --dest data/restored.db [--force]
    python scripts/backup.py list [--dir backups/]
    python scripts/backup.py info backups/backup_20261017_120000.db
"""

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "data" / "trainer.db"
DEFAULT_BACKUP_DIR = ROOT / "backups"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def _is_same_path(p1: Path, p2: Path) -> bool:
    """Check if two paths refer to the same filesystem location, accounting for case and links."""
    p1 = Path(p1)
    p2 = Path(p2)
    try:
        if p1.exists() and p2.exists():
            return p1.resolve().samefile(p2.resolve())
    except (FileNotFoundError, OSError):
        pass
    return os.path.normcase(str(p1.resolve())) == os.path.normcase(str(p2.resolve()))


def create_backup(db_path: Path, out_path: Path = None, out_dir: Path = None) -> tuple[Path, Path, dict]:
    """Create a consistent SQLite backup using the SQLite backup API.

    Writes to an isolated temporary file, runs integrity verification, computes
    SHA-256 digest, creates a manifest, and finalizes atomically.
    """
    db_path = Path(db_path).resolve()
    if not db_path.exists():
        raise FileNotFoundError(f"Source database not found: {db_path}")
    if db_path.is_dir():
        raise ValueError(f"Source path is a directory, not a database file: {db_path}")

    if out_path:
        target_path = Path(out_path).resolve()
    else:
        dest_dir = Path(out_dir or DEFAULT_BACKUP_DIR).resolve()
        dest_dir.mkdir(parents=True, exist_ok=True)
        ts_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        target_path = dest_dir / f"backup_{ts_str}_{os.urandom(4).hex()}.db"

    manifest_path = target_path.with_suffix(".meta.json")
    tmp_target = target_path.with_suffix(f".tmp.{os.getpid()}")
    tmp_manifest = manifest_path.with_suffix(f".tmp.{os.getpid()}")

    # Check collisions before creating directories, temporary files, or replacing files
    if _is_same_path(target_path, db_path):
        raise ValueError("Cannot write backup over the active source database directly.")
    if _is_same_path(manifest_path, db_path):
        raise ValueError(f"Backup manifest path collides with the active source database: {manifest_path}")
    if _is_same_path(tmp_target, db_path) or _is_same_path(tmp_manifest, db_path):
        raise ValueError("Backup temporary staging file collides with the active source database.")
    if _is_same_path(target_path, manifest_path):
        raise ValueError("Backup destination file collides with its own manifest path.")

    target_path.parent.mkdir(parents=True, exist_ok=True)

    if tmp_target.exists():
        tmp_target.unlink()
    if tmp_manifest.exists():
        tmp_manifest.unlink()

    # Perform online backup
    src_conn = sqlite3.connect(str(db_path), timeout=30.0)
    dest_conn = sqlite3.connect(str(tmp_target), timeout=30.0)
    try:
        with dest_conn:
            src_conn.backup(dest_conn, pages=250)
    finally:
        dest_conn.close()
        src_conn.close()

    # Verify backup database integrity
    chk_conn = sqlite3.connect(str(tmp_target))
    try:
        integrity_rows = chk_conn.execute("PRAGMA integrity_check").fetchall()
        if not integrity_rows or integrity_rows[0][0].lower() != "ok":
            raise RuntimeError(f"Integrity check failed on backup copy: {integrity_rows}")

        fk_errors = chk_conn.execute("PRAGMA foreign_key_check").fetchall()
        if fk_errors:
            raise RuntimeError(f"Foreign key check failed on backup copy: {fk_errors}")

        # Extract schema version and record counts
        tables = {r[0] for r in chk_conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        schema_version = None
        if "schema_migrations" in tables:
            v_row = chk_conn.execute("SELECT MAX(version) FROM schema_migrations").fetchone()
            schema_version = v_row[0] if v_row else None

        counts = {}
        for tbl in ("trainees", "sessions", "events"):
            if tbl in tables:
                cnt = chk_conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
                counts[tbl] = cnt
            else:
                counts[tbl] = 0
    finally:
        chk_conn.close()

    # Compute checksum
    file_hash = _sha256(tmp_target)
    file_size = tmp_target.stat().st_size

    manifest = {
        "format_version": 1,
        "engine": "sqlite",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source_db": str(db_path),
        "backup_file": target_path.name,
        "sha256": file_hash,
        "size_bytes": file_size,
        "schema_version": schema_version,
        "table_counts": counts,
        "integrity_check": "ok",
    }

    # Atomically finalize target and manifest with rollback recovery on failure
    tmp_manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    prev_target_bytes = target_path.read_bytes() if target_path.exists() else None
    prev_manifest_bytes = manifest_path.read_bytes() if manifest_path.exists() else None

    try:
        os.replace(tmp_target, target_path)
        os.replace(tmp_manifest, manifest_path)
    except Exception as final_exc:
        # Roll back: restore previous files or clean up partially written artifacts
        rollback_errors = []
        if prev_target_bytes is not None:
            try:
                target_path.write_bytes(prev_target_bytes)
            except Exception as r_exc:
                rollback_errors.append(f"failed to restore previous target: {r_exc}")
        elif target_path.exists():
            try:
                target_path.unlink()
            except Exception as r_exc:
                rollback_errors.append(f"failed to remove incomplete target: {r_exc}")

        if prev_manifest_bytes is not None:
            try:
                manifest_path.write_bytes(prev_manifest_bytes)
            except Exception as r_exc:
                rollback_errors.append(f"failed to restore previous manifest: {r_exc}")
        elif manifest_path.exists():
            try:
                manifest_path.unlink()
            except Exception as r_exc:
                rollback_errors.append(f"failed to remove incomplete manifest: {r_exc}")

        if rollback_errors:
            err_msg = f"Backup finalization failed ({final_exc}) and rollback also failed: {'; '.join(rollback_errors)}"
            raise RuntimeError(err_msg) from final_exc
        raise
    finally:
        for p in (tmp_target, tmp_manifest):
            if p and p.exists():
                try:
                    p.unlink()
                except Exception:
                    pass

    return target_path, manifest_path, manifest


def verify_backup(backup_path: Path, manifest_path: Path = None, require_manifest: bool = True) -> tuple[bool, dict]:
    """Verify backup database integrity, foreign keys, schema version, and checksum.

    By default (require_manifest=True), strictly requires an accompanying manifest
    file with a valid matching SHA-256 digest, matching file size, matching schema version,
    and matching table record counts. If require_manifest=False (standalone unmanaged mode),
    verifies SQLite structure and integrity without requiring a manifest.
    """
    backup_path = Path(backup_path).resolve()
    if not backup_path.exists():
        return False, {"error": f"Backup file not found: {backup_path}"}

    manifest = None
    m_path = Path(manifest_path) if manifest_path else backup_path.with_suffix(".meta.json")
    if m_path.exists():
        try:
            manifest = json.loads(m_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return False, {"error": f"Failed to read manifest: {exc}"}

        if not isinstance(manifest, dict):
            return False, {"error": "Manifest must be a JSON object."}
    elif require_manifest:
        return False, {
            "error": f"Manifest file not found: {m_path}. Managed backups require an accompanying manifest with SHA-256 verification. Pass require_manifest=False or --allow-unmanaged to verify standalone SQLite databases."
        }

    # Strict manifest schema and field validation when manifest is present or required
    if manifest is not None or require_manifest:
        if manifest is None:
            return False, {"error": "Manifest is required but missing."}

        # format_version: strictly integer 1
        fmt_ver = manifest.get("format_version")
        if type(fmt_ver) is not int or fmt_ver != 1:
            return False, {"error": "Manifest must contain integer 'format_version' equal to 1."}

        # engine
        if manifest.get("engine") != "sqlite":
            return False, {"error": "Manifest 'engine' field must be 'sqlite'."}

        # timestamp_utc: must be full ISO 8601 datetime with explicit UTC timezone
        ts = manifest.get("timestamp_utc")
        if not ts or not isinstance(ts, str):
            return False, {"error": "Manifest must contain a valid ISO-8601 'timestamp_utc' string."}
        if "T" not in ts:
            return False, {"error": "Manifest 'timestamp_utc' must be a full ISO-8601 datetime containing time, not a date-only string."}
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception:
            return False, {"error": "Manifest 'timestamp_utc' is not a valid ISO-8601 timestamp."}
        if dt.tzinfo is None:
            return False, {"error": "Manifest 'timestamp_utc' must include an explicit UTC timezone."}
        offset = dt.utcoffset()
        if offset is None or offset.total_seconds() != 0:
            return False, {"error": "Manifest 'timestamp_utc' must specify UTC timezone (offset zero / 'Z')."}

        # source_db and backup_file
        if not manifest.get("source_db") or not isinstance(manifest.get("source_db"), str):
            return False, {"error": "Manifest must contain a non-empty string 'source_db'."}
        if not manifest.get("backup_file") or not isinstance(manifest.get("backup_file"), str):
            return False, {"error": "Manifest must contain a non-empty string 'backup_file'."}
        if manifest.get("backup_file") != backup_path.name:
            return False, {
                "error": f"Manifest 'backup_file' mismatch: expected {backup_path.name}, got {manifest.get('backup_file')}"
            }

        # sha256
        expected_hash = manifest.get("sha256")
        if not expected_hash or not isinstance(expected_hash, str) or len(expected_hash) != 64:
            return False, {"error": "Manifest is missing or has invalid 64-character hex 'sha256' field."}
        try:
            int(expected_hash, 16)
        except ValueError:
            return False, {"error": "Manifest 'sha256' is not a valid hexadecimal string."}

        actual_hash = _sha256(backup_path)
        if actual_hash.lower() != expected_hash.lower():
            return False, {
                "error": f"SHA-256 checksum mismatch: expected {expected_hash}, got {actual_hash}"
            }

        # size_bytes
        expected_size = manifest.get("size_bytes")
        if expected_size is None or isinstance(expected_size, bool) or not isinstance(expected_size, int) or expected_size < 0:
            return False, {"error": "Manifest is missing or has invalid non-negative integer 'size_bytes' field."}
        actual_size = backup_path.stat().st_size
        if actual_size != expected_size:
            return False, {
                "error": f"File size mismatch: manifest records {expected_size} bytes, got {actual_size} bytes"
            }

        # schema_version
        expected_schema_v = manifest.get("schema_version")
        if expected_schema_v is None or isinstance(expected_schema_v, bool) or not isinstance(expected_schema_v, int) or expected_schema_v < 1:
            return False, {"error": "Manifest is missing or has invalid positive integer 'schema_version' field."}

        # table_counts
        table_counts = manifest.get("table_counts")
        if not isinstance(table_counts, dict):
            return False, {"error": "Manifest is missing or has invalid dictionary 'table_counts' field."}
        required_tables = {"trainees", "sessions", "events"}
        if set(table_counts.keys()) != required_tables:
            return False, {
                "error": f"Manifest 'table_counts' must contain exactly tables {sorted(required_tables)}, got {sorted(table_counts.keys())}"
            }
        for tbl, cnt in table_counts.items():
            if isinstance(cnt, bool) or not isinstance(cnt, int) or cnt < 0:
                return False, {
                    "error": f"Manifest table count for '{tbl}' must be a non-negative integer, got {cnt!r}"
                }

        # integrity_check
        if manifest.get("integrity_check") != "ok":
            return False, {"error": "Manifest 'integrity_check' must be 'ok'."}

    # Now verify SQLite database contents and structure
    try:
        conn = sqlite3.connect(str(backup_path), timeout=15.0)
        try:
            integrity = conn.execute("PRAGMA integrity_check").fetchall()
            if not integrity or integrity[0][0].lower() != "ok":
                return False, {"error": f"Integrity check failed: {integrity}"}

            fk = conn.execute("PRAGMA foreign_key_check").fetchall()
            if fk:
                return False, {"error": f"Foreign key check failed: {fk}"}

            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
            for req_tbl in ("trainees", "sessions", "events"):
                if req_tbl not in tables:
                    return False, {"error": f"Database is missing required application table '{req_tbl}'"}

            schema_version = None
            if "schema_migrations" in tables:
                v = conn.execute("SELECT MAX(version) FROM schema_migrations").fetchone()
                schema_version = v[0] if v else None
            elif require_manifest or manifest is not None:
                return False, {"error": "Database is missing required 'schema_migrations' table"}

            counts = {}
            for tbl in ("trainees", "sessions", "events"):
                counts[tbl] = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]

            if manifest is not None:
                if schema_version != manifest["schema_version"]:
                    return False, {
                        "error": f"Schema version mismatch: manifest records {manifest['schema_version']}, database has {schema_version}"
                    }

                for tbl, expected_count in manifest["table_counts"].items():
                    actual_cnt = counts.get(tbl, 0)
                    if actual_cnt != expected_count:
                        return False, {
                            "error": f"Table '{tbl}' record count mismatch: manifest records {expected_count}, database has {actual_cnt}"
                        }

            return True, {
                "backup_file": str(backup_path),
                "integrity_check": "ok",
                "foreign_key_check": "ok",
                "checksum_verified": bool(manifest and manifest.get("sha256")),
                "schema_version": schema_version,
                "table_counts": counts,
                "manifest": manifest,
                "unmanaged": manifest is None,
            }
        finally:
            conn.close()
    except Exception as exc:
        return False, {"error": f"SQLite error during verification: {exc}"}


def restore_backup(backup_path: Path, dest_path: Path, force: bool = False, verify_first: bool = True, require_manifest: bool = True) -> tuple[bool, str]:
    """Safely restore a verified backup to a destination database path.

    Refuses to restore over the source backup file. Requires `force=True`
    if destination already exists. Writes via temporary file and atomic replace.
    """
    backup_path = Path(backup_path).resolve()
    dest_path = Path(dest_path).resolve()

    if not backup_path.exists():
        return False, f"Backup file not found: {backup_path}"

    if _is_same_path(dest_path, backup_path):
        return False, "Cannot restore a backup over itself."

    if dest_path.exists() and not force:
        return False, f"Destination database already exists: {dest_path}. Use --force to allow overwrite."

    if verify_first:
        valid, details = verify_backup(backup_path, require_manifest=require_manifest)
        if not valid:
            return False, f"Pre-restore verification failed: {details.get('error')}"

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_dest = dest_path.with_suffix(f".tmp_restore.{os.getpid()}")
    if _is_same_path(tmp_dest, backup_path):
        return False, "Temporary restore destination collides with the backup file."
    if tmp_dest.exists():
        tmp_dest.unlink()

    src_conn = sqlite3.connect(str(backup_path), timeout=30.0)
    dest_conn = sqlite3.connect(str(tmp_dest), timeout=30.0)
    try:
        with dest_conn:
            src_conn.backup(dest_conn, pages=250)
    except Exception as exc:
        if tmp_dest.exists():
            try:
                tmp_dest.unlink()
            except Exception:
                pass
        return False, f"Failed to stage database copy: {exc}"
    finally:
        dest_conn.close()
        src_conn.close()

    # Verify restored target
    chk_conn = sqlite3.connect(str(tmp_dest))
    integrity = None
    try:
        integrity = chk_conn.execute("PRAGMA integrity_check").fetchall()
        if not integrity or integrity[0][0].lower() != "ok":
            return False, f"Restored file failed integrity check: {integrity}"
    except Exception as exc:
        return False, f"Integrity check failed: {exc}"
    finally:
        chk_conn.close()
        if not integrity or integrity[0][0].lower() != "ok":
            if tmp_dest.exists():
                try:
                    tmp_dest.unlink()
                except Exception:
                    pass

    # Atomically replace destination without delete-before-rename window
    try:
        os.replace(tmp_dest, dest_path)
    except Exception as exc:
        if tmp_dest.exists():
            try:
                tmp_dest.unlink()
            except Exception:
                pass
        return False, f"Failed to replace destination database: {exc}"

    return True, f"Successfully restored to {dest_path}"


def list_backups(dir_path: Path = None) -> list[dict]:
    """Scan backup directory and return list of backups with status."""
    dir_path = Path(dir_path or DEFAULT_BACKUP_DIR).resolve()
    if not dir_path.exists():
        return []

    results = []
    for db_file in sorted(dir_path.glob("*.db"), reverse=True):
        m_file = db_file.with_suffix(".meta.json")
        info = {
            "file": db_file.name,
            "path": str(db_file),
            "size_kb": round(db_file.stat().st_size / 1024, 1),
            "has_manifest": m_file.exists(),
        }
        if m_file.exists():
            try:
                m = json.loads(m_file.read_text(encoding="utf-8"))
                info["timestamp"] = m.get("timestamp_utc")
                info["schema_version"] = m.get("schema_version")
                info["table_counts"] = m.get("table_counts")
            except Exception:
                pass
        results.append(info)
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description="AEGIS Database Backup and Recovery Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # backup
    p_backup = subparsers.add_parser("backup", help="Create a consistent online backup")
    p_backup.add_argument("--db", default=str(DEFAULT_DB), help="Path to source SQLite database")
    p_backup.add_argument("--out", help="Explicit target file path for the backup")
    p_backup.add_argument("--dir", default=str(DEFAULT_BACKUP_DIR), help="Output directory for backups")

    # verify
    p_verify = subparsers.add_parser("verify", help="Verify backup integrity and checksum")
    p_verify.add_argument("backup_file", help="Path to backup .db file")
    p_verify.add_argument("--manifest", help="Optional path to manifest JSON")
    p_verify.add_argument("--allow-unmanaged", action="store_true", help="Allow verifying standalone SQLite file without an accompanying manifest")

    # restore
    p_restore = subparsers.add_parser("restore", help="Restore backup to destination path")
    p_restore.add_argument("backup_file", help="Path to backup .db file")
    p_restore.add_argument("--dest", required=True, help="Destination database file path")
    p_restore.add_argument("--force", action="store_true", help="Allow overwriting existing destination database")
    p_restore.add_argument("--skip-verify", action="store_true", help="Skip pre-restore verification")
    p_restore.add_argument("--allow-unmanaged", action="store_true", help="Allow restoring standalone SQLite file without an accompanying manifest")

    # list
    p_list = subparsers.add_parser("list", help="List backups in directory")
    p_list.add_argument("--dir", default=str(DEFAULT_BACKUP_DIR), help="Directory to scan")

    # info
    p_info = subparsers.add_parser("info", help="Display backup metadata and status")
    p_info.add_argument("backup_file", help="Path to backup .db file")

    args = parser.parse_args(argv)

    if args.command == "backup":
        try:
            target, manifest_path, meta = create_backup(
                db_path=Path(args.db),
                out_path=Path(args.out) if args.out else None,
                out_dir=Path(args.dir) if args.dir else None,
            )
            print(f"[OK] Backup created successfully:")
            print(f"  Database : {target} ({meta['size_bytes']} bytes)")
            print(f"  Manifest : {manifest_path}")
            print(f"  SHA-256  : {meta['sha256']}")
            print(f"  Version  : v{meta['schema_version']}")
            print(f"  Counts   : {meta['table_counts']}")
            return 0
        except Exception as exc:
            print(f"[ERROR] Backup failed: {exc}", file=sys.stderr)
            return 1

    elif args.command == "verify":
        valid, details = verify_backup(
            backup_path=Path(args.backup_file),
            manifest_path=Path(args.manifest) if args.manifest else None,
            require_manifest=not args.allow_unmanaged,
        )
        if valid:
            print(f"[OK] Backup verification passed for {args.backup_file}")
            print(f"  Integrity Check  : {details.get('integrity_check')}")
            print(f"  Foreign Keys     : {details.get('foreign_key_check')}")
            print(f"  Checksum Match   : {details.get('checksum_verified')}")
            print(f"  Schema Version   : v{details.get('schema_version')}")
            print(f"  Table Records    : {details.get('table_counts')}")
            return 0
        else:
            print(f"[FAIL] Backup verification failed: {details.get('error')}", file=sys.stderr)
            return 1

    elif args.command == "restore":
        success, msg = restore_backup(
            backup_path=Path(args.backup_file),
            dest_path=Path(args.dest),
            force=args.force,
            verify_first=not args.skip_verify,
            require_manifest=not args.allow_unmanaged,
        )
        if success:
            print(f"[OK] {msg}")
            return 0
        else:
            print(f"[ERROR] Restoration failed: {msg}", file=sys.stderr)
            return 1

    elif args.command == "list":
        backups = list_backups(Path(args.dir))
        if not backups:
            print(f"No backups found in {args.dir}")
            return 0
        print(f"Found {len(backups)} backup(s) in {args.dir}:")
        for b in backups:
            print(f"  - {b['file']} ({b['size_kb']} KB, schema v{b.get('schema_version')}, time: {b.get('timestamp')})")
        return 0

    elif args.command == "info":
        valid, details = verify_backup(Path(args.backup_file))
        if not valid:
            print(f"[INVALID] {details.get('error')}", file=sys.stderr)
            return 1
        m = details.get("manifest") or {}
        print(f"Backup Information: {args.backup_file}")
        print(f"  Created UTC : {m.get('timestamp_utc', 'unknown')}")
        print(f"  Source DB   : {m.get('source_db', 'unknown')}")
        print(f"  SHA-256     : {m.get('sha256', 'unknown')}")
        print(f"  Version     : v{details.get('schema_version')}")
        print(f"  Counts      : {details.get('table_counts')}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
