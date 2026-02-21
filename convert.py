import csv
import sqlite3

def create_table(cursor, table_name, columns):
    columns_str = ', '.join(columns)
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})")

def insert_data(cursor, table_name, columns, data):
    placeholders = ', '.join(['?' for _ in range(len(columns))])
    cursor.executemany(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})", data)

def csv_to_sqlite(csv_file, db_file, table_name, columns):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    create_table(cursor, table_name, columns)

    with open(csv_file, 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Lewati header
        data = [row for row in csvreader]

    insert_data(cursor, table_name, columns, data)

    conn.commit()
    conn.close()

# Contoh penggunaan:
csv_file = 'manhwa.csv'
db_file = 'manhwa.db'
table_name = 'manhwa'
columns = ['id', 'title', 'year', 'status', 'genres', 'chapters', 'popularity', 'score', 'mean_score', 'description'] # Ganti dengan nama kolom sebenarnya dari CSV Anda

if __name__ == "__main__":
    csv_to_sqlite(csv_file, db_file, table_name, columns)
