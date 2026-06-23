import os
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor

_PROJECT_ROOT = Path(__file__).resolve().parent
_USE_LOCAL_PG = (_PROJECT_ROOT / ".local" / "pgdata").exists()

DB_CONFIG = {
    "host":     os.environ.get("DB_HOST",     "localhost"),
    "port":     int(os.environ.get("DB_PORT", 5433 if _USE_LOCAL_PG else 5432)),
    "dbname":   os.environ.get("DB_NAME",     "CS166_AUCTION_AND_BIDDING_DATABASE"),
    "user":     os.environ.get("DB_USER",     "postgres" if _USE_LOCAL_PG else "ishaanvenkat"),
    "password": os.environ.get("DB_PASSWORD", ""),
}
 
 
def get_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

def query(sql: str, params=None, fetchone=False, fetchall=False, commit=False):
    conn = get_connection()
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            
            if commit:
                conn.commit()
            
            if fetchone:
                return cur.fetchone()
            
            if fetchall:
                return cur.fetchall()
            
            return None
    
    except Exception:
        conn.rollback()
        raise
    
    finally:
        conn.close()