import sqlite3
import chardet

def detect_encoding_and_correct(value):
    try:
        # Try to decode with utf-8
        return value.decode('utf-8')
    except UnicodeDecodeError:
        # If it fails, detect encoding and decode properly
        result = chardet.detect(value)
        return value.decode(result['encoding'])

def clean_table_data(conn, table_name):
    cursor = conn.cursor()
    # Get all column names
    cursor.execute(f'PRAGMA table_info({table_name})')
    columns = cursor.fetchall()
    text_columns = [col[1] for col in columns if col[2].lower() in ['text', 'char', 'varchar', 'clob']]

    for column in text_columns:
        cursor.execute(f'SELECT rowid, {column} FROM {table_name}')
        for row in cursor.fetchall():
            rowid, value = row
            if isinstance(value, bytes):
                cleaned_value = detect_encoding_and_correct(value)
                cursor.execute(f'UPDATE {table_name} SET {column} = ? WHERE rowid = ?', (cleaned_value, rowid))

def clean_database():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        clean_table_data(conn, table_name)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    clean_database()
