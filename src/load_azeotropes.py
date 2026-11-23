import csv
import sqlite3
from settings import P_GRID

conn = sqlite3.connect("data/thf.db")

with open("sql/azeotropes.sql", "r", encoding="utf-8") as sql_file:
    conn.executescript(sql_file.read())

with open("sql/column_specs.sql", "r", encoding="utf-8") as sql_file:
    conn.executescript(sql_file.read())

with open("data/azeotrope_by_pressure.csv", "r", newline="", encoding="utf-8-sig") as csv_file:
    rows = list(csv.DictReader(csv_file))

    for row in rows:
        p = float(row['P_bar'])

        if p not in P_GRID:
            raise ValueError(f"{p} bar is not in P_GRID")
    
        conn.execute("INSERT INTO azeotropes (property_package, p_bar, x_azeotrope, T_azeotrope) VALUES (?, ?, ?, ?)", (row['property_package'], p, float(row['x_azeotrope']), float(row['T_azeotrope'])))


conn.commit()

# TESTS
print(conn.execute("SELECT COUNT(*) FROM azeotropes").fetchone()) 
# Expected output: (18,)

print(conn.execute("SELECT property_package, COUNT(*) FROM azeotropes GROUP BY property_package").fetchall())
# Expected output: [('NRTL', 9), ('Wilson', 9)]

print(conn.execute("SELECT * FROM azeotropes WHERE p_bar = 1.013").fetchall())
# Expected output: [('NRTL', 1.013, 0.833, 64.04), ('Wilson', 1.013, 0.8336, 64.07)]

print(conn.execute("SELECT p_bar, x_azeotrope FROM azeotropes WHERE property_package = 'Wilson' ORDER BY p_bar").fetchall())
# Expected output: [(1.013, 0.8336), ... (8.0, 0.649)]

print(conn.execute("SELECT * FROM column_specs").fetchall())
# Expected output: [(1.013, 0.8336, 129.559, 1870.441), ... (8.0, 0.649, 166.41, 1833.59)]

conn.close()