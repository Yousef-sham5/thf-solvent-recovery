import os
import sys

import pythonnet
pythonnet.load("netfx")
import clr

F_KMOL_H = 2000.0
Z_THF = 0.06
THF = "Tetrahydrofuran"
WATER = "Water"

DWSIM_BIN = os.environ.get("DWSIM_BIN")
if not DWSIM_BIN:
    raise SystemExit("Set DWSIM_BIN to the DWSIM installation folder before running.")
for sub in ("", "unitops", "ppacks", "extenders"):
    sys.path.append(os.path.join(DWSIM_BIN, sub))
clr.AddReference("DWSIM.Automation")
clr.AddReference("DWSIM.Automation.FluentAPI")

from DWSIM.Automation.FluentAPI import Flowsheet, PropertyPackages, Q, FlowsheetSolveException  # noqa: E402 # pyright: ignore[reportMissingImports]


def run_case(p_bar, reflux, n_stages, feed_stage, B_kmol_h) -> dict:
    """
    This function takes inputs for the column and solves it. 
    Results are saved in a dict and if the column doesn't converge, an error message is stored.

    Args:
        p_bar: Column top pressure & feed pressure (bar).
        reflux: Reflux ratio.
        n_stages: Total number of stages in the column (including condenser & reboiler).
        feed_stage: Feed stage number from the top (condenser = stage 1).
        B_kmol_h: Bottoms flow rate (kmol/h).
    
    Returns:
        result: Dict with the inputs, converged (1 or 0) and error_msg. If converged, also x_thf_top, x_thf_bottom, q_cond_kw, q_reb_kw, T_top_C, T_bottom_C, D_kmol_h and thf_err_rel.
    """
    fs = (Flowsheet.Create("THF_column")
        .WithCompounds(THF, WATER)
        .WithPropertyPackage(PropertyPackages.Wilson))

    feed = (fs.AddMaterialStream("Feed")
            .WithPressure(Q.Bar(p_bar))
            .WithVaporFraction(0.0)
            .WithMolarFlow(Q.KmolPerHour(F_KMOL_H))
            .SetCompoundMolarFlow(THF, F_KMOL_H * Z_THF / 3.6) # calculating in mol/s
            .SetCompoundMolarFlow(WATER, F_KMOL_H * (1 - Z_THF) / 3.6)) # calculating in mol/s

    distillate = fs.AddMaterialStream("Distillate")
    bottoms = fs.AddMaterialStream("Bottoms")
    condenser_duty = fs.AddEnergyStream("Q_condenser")
    reboiler_duty = fs.AddEnergyStream("Q_reboiler")

    column = (fs.AddDistillationColumn("Column")
            .WithNumberOfStages(n_stages)
            .WithFeed(feed, f"Stage{feed_stage}")
            .WithDistillate(distillate)
            .WithBottoms(bottoms)
            .WithCondenserDuty(condenser_duty)
            .WithReboilerDuty(reboiler_duty)
            .WithCondenserSpec("Reflux Ratio", reflux)
            .WithReboilerSpec("Product Molar Flow Rate", Q.KmolPerHour(B_kmol_h))
            .WithTopPressure(Q.Bar(p_bar))
            .WithColumnPressureDrop(Q.Bar(0.0)))

    result = {"p_bar": p_bar, "n_stages": n_stages, "feed_stage": feed_stage,
              "reflux": reflux, "B_kmol_h": B_kmol_h}

    # if result didnt converge, store error msg
    try:
        fs.Solve()
    except FlowsheetSolveException as e:
        result["converged"] = 0
        result["error_msg"] = str(e).splitlines()[0]
        return result

    # otherwise we add final results
    result["converged"] = 1
    result["error_msg"] = None

    result["x_thf_top"] = distillate.OverallMoleFraction(THF)
    result["x_thf_bottom"] = bottoms.OverallMoleFraction(THF)
    result["q_cond_kw"] = condenser_duty.EnergyFlowKW
    result["q_reb_kw"] = reboiler_duty.EnergyFlowKW
    result["T_top_C"] = distillate.TemperatureK - 273.15
    result["T_bottom_C"] = bottoms.TemperatureK - 273.15
    result["D_kmol_h"] = distillate.MolarFlowMolPerSecond * 3.6

    B_out = bottoms.MolarFlowMolPerSecond * 3.6
    thf_in = F_KMOL_H * Z_THF
    thf_out = result["D_kmol_h"] * result["x_thf_top"] + B_out * result["x_thf_bottom"]

    result["thf_err_rel"] = abs(thf_in - thf_out) / thf_in

    return result


if __name__ == "__main__":
    print(run_case(1.013, 5, 17, 14, 1870.441))
    print(run_case(1.013, 5, 17, 14, 2100.0))