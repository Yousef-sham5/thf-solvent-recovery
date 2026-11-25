import sqlite3
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from settings import P_GRID, RR_GRID

PRESSURE_CMAP = LinearSegmentedColormap.from_list(name="pressure", colors=["coral", "orchid", "cornflowerblue"])

# Same as sql/queries.sql query no.1 with the addition of q_reb_kw  
QUERY_1 = """
          SELECT p_bar, n_stages, reflux, q_reb_kw FROM runs
          WHERE converged = 1 AND thf_err_rel < 1e-3
          ORDER BY p_bar, reflux, n_stages;
          """

# Same as sql/queries.sql query no.3
QUERY_3 = """
          WITH plateau AS (
          SELECT p_bar, x_thf_top AS x_plateau
          FROM runs
          WHERE n_stages = 25 
            AND reflux = 12 
            AND converged = 1
          )
          SELECT r.p_bar, r.n_stages, MIN(r.reflux) AS min_reflux, r.q_reb_kw
          FROM runs AS r
          JOIN plateau AS p ON r.p_bar = p.p_bar
          WHERE r.x_thf_top >= 0.999 * p.x_plateau
            AND r.converged = 1
            AND r.thf_err_rel < 1e-3
          GROUP BY r.p_bar, r.n_stages
          ORDER BY r.n_stages, r.p_bar;
          """


def read_query(query) -> list[tuple]:
    """
    This function runs one SELECT on thf.db and returns the rows.

    Args:
        query: SQL SELECT statement to execute.
    
    Returns:
        rows: Query output.
    """

    conn = sqlite3.connect("file:data/thf.db?mode=ro", uri=True) # read-only mode
    rows = conn.execute(query).fetchall()
    conn.close()

    return rows


def plot_duty(runs, min_rr_points, n_stages, x_scale, file_name) -> None:
    """
    This function plots reboiler duty vs reflux ratio for one stage count and one x-axis scale, and saves one PNG.

    Args:
        runs: Query no.1's output (list).
        min_rr_points: Query no.3's output (list).
        n_stages: Number of stages (17/25).
        x_scale: The x-axis scale (linear/log).
        file_name: The final figure's file name.
    """

    fig, ax = plt.subplots(figsize=(8, 5))

    min_reflux_n = []
    q_reb_min_reflux = []

    for row in min_rr_points:
        if row[1] == n_stages:
            min_reflux_n.append(row[2])
            q_reb_min_reflux.append(row[3])

    for i, p in enumerate(P_GRID):
        reflux = []
        q_reb = []

        for row in runs:
            if row[0] == p and row[1] == n_stages:
                reflux.append(row[2])
                q_reb.append(row[3])

        ax.plot(reflux, q_reb, color=PRESSURE_CMAP(i / (len(P_GRID) - 1)), marker=".", linestyle="-", label=f"{p} bar")

    ax.scatter(min_reflux_n, q_reb_min_reflux, facecolors="none", edgecolors="black", marker="D", zorder=5, label="Smallest grid RR reaching 99.9% of plateau")

    if x_scale == "log":
        ax.set_xscale("log")
        ax.set_xticks(RR_GRID)
        ax.set_xticklabels([f"{rr:g}" for rr in RR_GRID])
        ax.minorticks_off()

    ax.set_title(f"Reboiler duty vs reflux ratio, N = {n_stages} ({x_scale} RR axis)")
    ax.set_xlabel("Reflux ratio, RR")
    ax.set_ylabel("Reboiler duty, Q_reb (kW)")
    ax.grid(True, alpha=0.25)

    ax.legend(loc="upper left", fontsize="small")
        
    fig.tight_layout()
    fig.savefig(file_name, dpi=200)
    plt.close(fig)
        

if __name__ == "__main__":
    runs = read_query(QUERY_1) # query no.1 rows
    min_rr_points = read_query(QUERY_3) # query no.3 rows

    plot_duty(runs, min_rr_points, 17, "linear", "figures/fig3a_duty_vs_rr_n17_linear.png")
    plot_duty(runs, min_rr_points, 17, "log", "figures/fig3a_duty_vs_rr_n17_log.png")
    plot_duty(runs, min_rr_points, 25, "linear", "figures/fig3b_duty_vs_rr_n25_linear.png")
    plot_duty(runs, min_rr_points, 25, "log", "figures/fig3b_duty_vs_rr_n25_log.png")