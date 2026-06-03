import os
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "host":     os.environ.get("DB_HOST",     "localhost"),
    "port":     int(os.environ.get("DB_PORT", 5432)),
    "dbname":   os.environ.get("DB_NAME",     "CS166_AUCTION_AND_BIDDING_DATABASE"),
    "user":     os.environ.get("DB_USER",     "ishaanvenkat"),
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