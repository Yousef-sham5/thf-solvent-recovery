import sqlite3
import matplotlib.pyplot as plt

# Same as sql/queries.sql query no.2
QUERY_2 = """
            SELECT r.p_bar, MAX(r.x_thf_top) AS max_x_thf_top, a.x_azeotrope, (MAX(r.x_thf_top) / a.x_azeotrope) AS ratio
            FROM runs AS r
            INNER JOIN azeotropes AS a ON r.p_bar = a.p_bar
            WHERE r.converged = 1 
                AND r.thf_err_rel < 1e-3 
                AND a.property_package = 'Wilson'
            GROUP BY r.p_bar, a.x_azeotrope
            ORDER BY r.p_bar;
          """

def read_query2() -> tuple[list, list, list]:
    """
    This function executes sql/queries.sql query no.2 which returns the best (maximum) THF 
    composition at each pressure along with the Wilson azeotrope composition.

    Returns:
        p_bar: List of the 9 sweep pressures (bar).
        max_x_thf_top: List of the maximum THF distillate composition at each pressure (max over N and RR).
        x_azeotrope: List of calculated azeotrope compositions with Wilson.
    """

    p_bar = []
    max_x_thf_top = []
    x_azeotrope = []

    conn = sqlite3.connect("file:data/thf.db?mode=ro", uri=True) # read-only mode

    # executes query 2
    rows = conn.execute(QUERY_2).fetchall()

    for row in rows:
        p_bar.append(row[0])
        max_x_thf_top.append(row[1])
        x_azeotrope.append(row[2])

    conn.close()

    return p_bar, max_x_thf_top, x_azeotrope


if __name__ == "__main__":
    p_bar, max_x_thf_top, x_azeotrope = read_query2()

    fig, ax = plt.subplots()

    ax.plot(p_bar, x_azeotrope, color="cornflowerblue", marker=".", linestyle="-", linewidth=2, label="Wilson azeotrope (Txy)")

    ax.scatter(p_bar, max_x_thf_top, color="coral", edgecolors="white", marker="o", s=55, linewidths=1.2, zorder=5, label="Best column top (max over N and RR)")

    ax.set_title("Best top THF vs pressure (Wilson)")
    ax.set_xlabel("P (bar)")
    ax.set_ylabel("THF mole fraction at top, x_THF")
    ax.grid(True, alpha=0.25)

    ax.legend()

    fig.tight_layout()
    fig.savefig("figures/fig2_top_thf_vs_pressure.png", dpi=200)
