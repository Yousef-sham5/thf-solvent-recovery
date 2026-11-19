import csv
import glob
import os

files = sorted(glob.glob("data/txy_*bar.csv"))
# print(len(files))


def read_table(path):
  x = [] # THF composition
  tb = [] # bubble temperature

  with open(path, newline="", encoding="utf-8-sig") as file:
    reader = list(csv.DictReader(file))

  for i in reader:
    x.append(float(i['x_THF']))
    tb.append(float(i['T_bubble_C']))

  return x, tb



def find_azeotrope(x, tb):
  s = [] # slope
  m = [] # midpoint
  signs = []
  hits = [] # index of slope change

  # slope and midpoints
  for k in range(len(x) - 1):
    s.append(round((tb[k+1] - tb[k]) / (x[k+1] - x[k]), 2))
    m.append(round((x[k] + x[k+1]) / 2, 3))

  # signs
  for k in range(len(s)):
    if s[k] < 0:
      signs.append('neg')
    elif s[k] == 0:
      signs.append('zero')
    else:
      signs.append('pos')

  for k in range(len(signs) - 1):
    if signs[k] == 'neg':
      j = k + 1
      while j < len(signs) and signs[j] == 'zero':
        j += 1
      if j < len(signs) and signs[j] == 'pos':
        hits.append((k, j))

  # stop early unless there is exactly one sign change
  if len(hits) == 0:
    print("No azeotrope found")
    return None, None, 0
  elif len(hits) > 1:
    print("CHECK: more than one sign change, at x =", [x[k] for k, j in hits])
    return None, None, len(hits)

  k, j = hits[0]

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

  return x0, T0, len(hits)



def parse_name(path):
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

    x0, T0, n = find_azeotrope(x, tb) # n is number of sign changes

    if x0 is None:
      print(f"{model}, {p} bar: There are {n} sign changes, check by hand.")
      continue

    print(f"{model:<7}{p:>6} bar   x_azeotrope = {x0:.4f}   T_azeotrope = {T0:.2f} C")

    rows.append([model, p, f"{x0:.4f}", f"{T0:.2f}"])

  rows.sort(key=lambda r: (r[0], float(r[1])))
  out_path = "data/azeotrope_by_pressure.csv"

  with open(out_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["property_package", "P_bar", "x_azeotrope", "T_azeotrope"])
    writer.writerows(rows)

  print(f"Wrote {len(rows)} rows to {out_path}")