"""
Hydroponics Platform — Local Offline Storage Buffer
Provides persistent SQLite buffering when cloud / MQTT connectivity is unavailable.
"""

import sqlite3
import json
import logging
import threading
from typing import List, Dict, Any, Tuple

logger = logging.getLogger("StorageBuffer")

class StorageBuffer:
    def __init__(self, db_path: str = "edge_telemetry_buffer.db", max_records: int = 10000):
        self._db_path = db_path
        self._max_records = max_records
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with self._lock:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS telemetry_queue (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        topic TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()

    def push(self, topic: str, payload_dict: Dict[str, Any]) -> bool:
        """Pushes an unsent message into the offline SQLite queue."""
        with self._lock:
            try:
                payload_str = json.dumps(payload_dict)
                with sqlite3.connect(self._db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO telemetry_queue (topic, payload) VALUES (?, ?)",
                        (topic, payload_str)
                    )
                    # Enforce max records limit (drop oldest if exceeded)
                    cursor.execute("""
                        DELETE FROM telemetry_queue WHERE id IN (
                            SELECT id FROM telemetry_queue ORDER BY id ASC 
                            LIMIT MAX(0, (SELECT COUNT(*) FROM telemetry_queue) - ?)
                        )
                    """, (self._max_records,))
                    conn.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to buffer message in SQLite: {e}")
                return False

    def peek_batch(self, limit: int = 50) -> List[Tuple[int, str, Dict[str, Any]]]:
        """Retrieves oldest pending records for flushing."""
        with self._lock:
            records = []
            try:
                with sqlite3.connect(self._db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT id, topic, payload FROM telemetry_queue ORDER BY id ASC LIMIT ?",
                        (limit,)
                    )
                    rows = cursor.fetchall()
                    for r_id, topic, payload_str in rows:
                        try:
                            parsed = json.loads(payload_str)
                            records.append((r_id, topic, parsed))
                        except Exception:
                            # Drop corrupted record
                            cursor.execute("DELETE FROM telemetry_queue WHERE id = ?", (r_id,))
                            conn.commit()
            except Exception as e:
                logger.error(f"Failed to read from buffer: {e}")
            return records

    def delete_batch(self, record_ids: List[int]) -> bool:
        """Removes successfully transmitted records from queue."""
        if not record_ids:
            return True
        with self._lock:
            try:
                with sqlite3.connect(self._db_path) as conn:
                    cursor = conn.cursor()
                    placeholders = ",".join("?" for _ in record_ids)
                    cursor.execute(f"DELETE FROM telemetry_queue WHERE id IN ({placeholders})", record_ids)
                    conn.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to delete batch from buffer: {e}")
                return False

    def get_pending_count(self) -> int:
        with self._lock:
            try:
                with sqlite3.connect(self._db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM telemetry_queue")
                    row = cursor.fetchone()
                    return row[0] if row else 0
            except Exception:
                return 0
