import sqlite3
from run_case import run_case

FEED_STAGE = {17: 14, 25: 21}
N_LIST = [17, 25]
RR_LIST = [0.25, 0.5, 0.75, 1, 2, 3, 5, 8, 12]

conn = sqlite3.connect("data/thf.db")

specs = conn.execute(
    "SELECT p_bar, B_kmol_h FROM column_specs ORDER BY p_bar"
).fetchall()

with open("sql/runs.sql", "r", encoding="utf-8") as sql_file:
    conn.executescript(sql_file.read())

for p_bar, B in specs:
    for n in N_LIST:
        for rr in RR_LIST:

            try:
                row = run_case(p_bar, rr, n, FEED_STAGE[n], B)
            except Exception as e:
                row = {"p_bar": p_bar, "n_stages": n, "feed_stage": FEED_STAGE[n],
                       "reflux": rr, "B_kmol_h": B, "converged": 0,
                       "error_msg": str(e).splitlines()[0]}
                print(f"FAILED P={p_bar} N={n} RR={rr}: {e}")

            conn.execute("INSERT INTO runs (p_bar, n_stages, feed_stage, reflux, B_kmol_h, converged, error_msg, x_thf_top, x_thf_bottom, q_cond_kw, q_reb_kw, T_top_C, T_bottom_C, D_kmol_h, thf_err_rel) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (row.get("p_bar"), row.get("n_stages"), row.get("feed_stage"), row.get("reflux"), row.get("B_kmol_h"), row.get("converged"), row.get("error_msg"), row.get("x_thf_top"), row.get("x_thf_bottom"), row.get("q_cond_kw"), row.get("q_reb_kw"), row.get("T_top_C"), row.get("T_bottom_C"), row.get("D_kmol_h"), row.get("thf_err_rel")))

            conn.commit()

            print(f"P={p_bar} N={n} RR={rr} converged={row.get('converged')}")

conn.close()

