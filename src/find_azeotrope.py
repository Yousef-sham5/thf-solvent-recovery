import csv
import glob
import os

files = sorted(glob.glob("data/txy_*bar.csv"))
# print(len(files))


def read_table(path) -> tuple[list, list]:
    """
    This function reads all Txy data at different pressures for property packages NRTL and Wilson.
    It saves THF composition & bubble temperature with a step count of 100 from composition 0.00 to 1.00.

    Args:
        path: Files named txy_*bar.csv in data folder.

    Returns:
        x: List of compositions (between 0.00 and 1.00 mol frac.).
        tb: List of bubble temperatures. 
    """

    x = [] # THF composition
    tb = [] # bubble temperature

    with open(path, newline="", encoding="utf-8-sig") as file:
        rows = list(csv.DictReader(file))

    for row in rows:
        x.append(float(row['x_THF']))
        tb.append(float(row['T_bubble_C']))

    return x, tb


def slopes_and_midpoints(x, tb) -> tuple[list, list]:
    """
    This function calculates the slopes at each step and the composition midpoints.

    Args:
        x: List of compositions (between 0.00 and 1.00 mol frac.).
        tb: List of bubble temperatures.

    Returns:
        s: List of slopes at each step.
        m: List of midpoints.  
    """
    s = [] # slope
    m = [] # midpoint

    for k in range(len(x) - 1):
        s.append(round((tb[k+1] - tb[k]) / (x[k+1] - x[k]), 2))
        m.append(round((x[k] + x[k+1]) / 2, 3))

    return s, m


def slope_signs(s) -> list:
    """
    This function takes the signs of the slope list and records the sign at each step.

    Args:
        s: List of slopes at each step.
    
    Returns:
        signs: List of signs at each step (pos, zero or neg).
    """
    signs = []

    for k in range(len(s)):
        if s[k] < 0:
            signs.append('neg')
        elif s[k] == 0:
            signs.append('zero')
        else:
            signs.append('pos')

    return signs


def find_sign_changes(x, signs) -> tuple[int, int, int]:
    """
    This function calculates the number of sign changes from negative to positive and saves the index.

    Args:
        x: List of compositions (between 0.00 and 1.00 mol frac.).
        signs: List of signs at each step (pos, zero or neg).

    Returns:
        k: Index of the last negative slope before the sign change (None if not exactly one sign change).
        j: Index of the first positive slope after the sign change (j = k + 1, unless zero slopes sit in between).
        n: Number of sign changes
    """

    hits = [] # index of slope change

    for k in range(len(signs) - 1):
        if signs[k] == 'neg':
            j = k + 1
            while j < len(signs) and signs[j] == 'zero':
                j += 1
            if j < len(signs) and signs[j] == 'pos':
                hits.append((k, j))

    # one sign change means its fine, otherwise the values shall not pass
    if len(hits) == 0:
        print("No azeotrope found")
        return None, None, 0
    elif len(hits) > 1:
        print("CHECK: more than one sign change, at x =", [x[k] for k, j in hits])
        return None, None, len(hits)

    k, j = hits[0]
    n = len(hits)

    return k, j, n


def calc_azeotrope(x, tb, s, m, k, j) -> tuple[float, float]:
    """
    This function calculates the azeotrope composition and azeotrope temperature.

    Args:
        x: List of compositions (between 0.00 and 1.00 mol frac.).
        tb: List of bubble temperatures.
        s: List of slopes at each step.
        m: List of midpoints. 
        k: Index of the last negative slope before the sign change.
        j: Index of the first positive slope after the sign change (j = k + 1 is a normal minimum, j > k + 1 is a flat bottom).

    Returns:
        x0: Azeotrope composition
        T0: Azeotrope temperature (C)
    """
    if j == k + 1:
        # normal minimum: x0 where the slope crosses zero
        x0 = m[k] + (m[k+1] - m[k]) * (-s[k]) / (s[k+1] - s[k])

        # T0
        if x0 >= x[k+1]:
            i = k + 1
        else:
            i = k
        T0 = round(tb[i] + (x0 - x[i]) / (x[i+1] - x[i]) * (tb[i+1] - tb[i]), 2)
    else:
        # flat bottom: T is equal from x[k+1] to x[j], so take the midpoint
        x0 = (x[k+1] + x[j]) / 2
        T0 = round(tb[k+1], 2)

    return x0, T0


def parse_name(path) -> tuple[str, str]:
    """
    This function extracts the model and pressure depending on the csv.

    Args:
        path: Files named txy_*bar.csv in data folder.
    
    Returns:
        model: Property package name.
        pressure: Pressure value as a string (bar).
    """
    name = os.path.basename(path)
    name = name.replace(".csv", "")
    parts = name.split("_")

    names = {'wilson': 'Wilson', 'nrtl': 'NRTL'}

    model = names[parts[1]]
    pressure = parts[2].replace("bar", "")

    return model, pressure


if __name__ == "__main__":
    rows = []

    for path in files:
        model, p = parse_name(path)
        x, tb = read_table(path)

        if not x:
            print(f"{model}, {p} bar: Empty & skipped.")
            continue

        s, m = slopes_and_midpoints(x, tb)
        signs = slope_signs(s)
        k, j, n = find_sign_changes(x, signs)

        if k is None:
            print(f"{model}, {p} bar: There are {n} sign changes, check by hand.")
            continue

        x0, T0 = calc_azeotrope(x, tb, s, m, k, j)

        print(f"{model:<7}{p:>6} bar   x_azeotrope = {x0:.4f}   T_azeotrope = {T0:.2f} C")

        rows.append([model, p, f"{x0:.4f}", f"{T0:.2f}"])

    rows.sort(key=lambda r: (r[0], float(r[1])))
    out_path = "data/azeotrope_by_pressure.csv"

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["property_package", "P_bar", "x_azeotrope", "T_azeotrope"])
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {out_path}")