# THF-Water Distillation: Pressure Effects on the Azeotrope Limit

Status: in progress (started 17 Nov 2026).

## Overview

Tetrahydrofuran (THF) is a common pharmaceutical solvent. Recovering it from water is limited by a minimum-boiling azeotrope, and the azeotrope composition shifts with pressure. This project uses DWSIM, Python and SQLite to:

1. Check the thermodynamic model (NRTL and UNIQUAC) against published azeotrope data at 1.013 and 8 bar.
2. Run a single distillation column over a grid of pressures, reflux ratios and stage counts.
3. Store every run, including failed ones, in SQLite with a mass balance check.
4. Report how the best reachable top purity changes with pressure, and the reflux and reboiler duty needed to approach the azeotrope.

## Method (planned)

- Simulator: DWSIM Patreon Edition 10.2.16 (Windows). Files in `flowsheets/` were saved with this version.
- Feed: 6 wt% THF in water, 100 kmol/h (feed basis from the FOSSEE THF/water flowsheet based on Luyben 2008).
- Column: 17 stages, feed on stage 13, total condenser.
- Sweep: 9 pressures (1.013 to 8 bar) x 6 reflux ratios x 2 stage counts = 108 runs.

## Model validation

Pending. Results will be recorded in `data/phase0_azeotrope.csv`.

## Results

Pending.

## Limitations

Pending.

## Repository layout

| Folder | Contents |
|---|---|
| `flowsheets/` | DWSIM flowsheet files (`.dwxmz`) |
| `src/` | Python code that drives DWSIM and writes to the database |
| `sql/` | Database schema and queries |
| `data/` | Validation table and SQLite database |
| `figures/` | Plots and screenshots |
| `docs/` | Data dictionary |

## Sources

- AIDIC Chemical Engineering Transactions Vol. 61, THF-water extractive vs pressure-swing distillation: https://www.aidic.it/cet/17/61/235.pdf
- FOSSEE OpenModelica THF/water pressure-swing flowsheet (based on Luyben 2008): https://om.fossee.in/chemical/flowsheeting-project/download/abstract-file/77
- DWSIM tutorials: https://dwsim.org/tutorials/en/
