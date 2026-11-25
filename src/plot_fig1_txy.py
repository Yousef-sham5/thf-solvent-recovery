import csv
import matplotlib.pyplot as plt

files = ["data/txy_wilson_1.013bar.csv", "data/txy_wilson_8bar.csv"]

def read_txy_tables(path) -> tuple[list, list, list]:
    """
    This function reads the Txy data for pressures 1.013 and 8 bar with the Wilson property package.

    Args:
        path: Files named txy_wilson_1.013bar.csv and txy_wilson_8bar.csv in data folder.

    Returns:
        x_THF: List of compositions (between 0.00 and 1.00 mol frac.).
        T_bubble_C: List of bubble temperatures.
        T_dew_C: List of dew temperatures.
    """

    x_THF = []
    T_bubble_C = []
    T_dew_C = []

    with open(path, "r", newline="", encoding="utf-8-sig") as csv_file:
        rows = list(csv.DictReader(csv_file))

    for row in rows:
        x_THF.append(float(row["x_THF"]))
        T_bubble_C.append(float(row["T_bubble_C"]))
        T_dew_C.append(float(row["T_dew_C"]))

    return x_THF, T_bubble_C, T_dew_C


def read_validation_tables() -> tuple[list, list]:
    """
    This function reads the published azeotrope composition (AIDIC) and the Wilson azeotrope temperature from azeotrope_validation.csv.

    Returns:
        published_x: Published azeotrope composition.
        T_azeotrope: Wilson azeotrope temperature from DWSIM.
    """

    published_x = []
    T_azeotrope = []

    with open("data/azeotrope_validation.csv", "r", newline="", encoding="utf-8-sig") as csv_file:
        rows = list(csv.DictReader(csv_file))

    for row in rows:
        if row["property_package"] == "Wilson":
            published_x.append(float(row["published_x"]))
            T_azeotrope.append(float(row["T_azeotrope"]))

    return published_x, T_azeotrope


# Main plot:
if __name__ == "__main__":
    published_x, T_azeotrope = read_validation_tables()

    colors = ["coral", "cornflowerblue"]
    pressures = ["1.013 bar", "8 bar"]

    fig, ax = plt.subplots()

    for i, path in enumerate(files):
        x_THF, T_bubble_C, T_dew_C = read_txy_tables(path)

        color = colors[i]
        pressure = pressures[i]

        ax.plot(x_THF, T_bubble_C, color=color, linestyle="-", label=f"Bubble {pressure}")
        ax.plot(x_THF, T_dew_C, color=color, linestyle="--", label=f"Dew {pressure}")

    ax.set_title("THF-water Txy (Wilson) vs published azeotropes")
    ax.set_xlabel("THF mole fraction (x or y)")
    ax.set_ylabel("T (°C)")
    ax.set_xlim(0, 1)
    ax.grid(True, alpha=0.25)

    ax.scatter(published_x, T_azeotrope, color="black", marker="o", zorder=5, label="Published, AIDIC (Aspen Plus, NRTL)")

    ax.legend()

    fig.tight_layout()
    fig.savefig("figures/fig1_txy_validation.png", dpi=200)
