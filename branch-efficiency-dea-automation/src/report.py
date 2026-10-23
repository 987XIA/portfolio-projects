from pathlib import Path

import pandas as pd
from pulp import LpStatus, LpStatusOptimal, PULP_CBC_CMD, value


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_PATH = PROJECT_DIR / "output" / "dea_results.xlsx"


def generate_dea_report(models, df_inputs, df_outputs, output_path=DEFAULT_REPORT_PATH):
    """Solve DEA models and write their scores, weights, and source data to Excel."""
    branches = list(df_inputs.index)
    if not df_inputs.index.equals(df_outputs.index):
        raise ValueError("Input and output data must have the same branch indexes")
    if len(models) != len(branches):
        raise ValueError(
            f"Received {len(models)} models for {len(branches)} branches"
        )

    efficiency_rows = []
    weight_rows = []
    for unit_index, (branch, model) in enumerate(zip(branches, models)):
        status = model.solve(PULP_CBC_CMD(msg=False))
        if status != LpStatusOptimal:
            raise RuntimeError(
                f"DEA model for {branch!r} did not solve optimally: "
                f"{LpStatus[status]}"
            )

        efficiency = value(model.objective)
        if efficiency is None:
            raise RuntimeError(f"DEA model for {branch!r} has no objective value")

        efficiency_rows.append(
            {
                "Branch": branch,
                "Status": LpStatus[status],
                "Efficiency": efficiency,
            }
        )

        variables = model.variablesDict()
        weight_row = {"Branch": branch}
        for index, factor in enumerate(df_inputs.columns):
            variable = variables.get(f"input_weight_{unit_index}_{index}")
            if variable is None or variable.varValue is None:
                raise RuntimeError(
                    f"Missing solved input weight {factor!r} for {branch!r}"
                )
            weight_row[f"Input: {factor}"] = variable.varValue

        for index, factor in enumerate(df_outputs.columns):
            variable = variables.get(f"output_weight_{unit_index}_{index}")
            if variable is None or variable.varValue is None:
                raise RuntimeError(
                    f"Missing solved output weight {factor!r} for {branch!r}"
                )
            weight_row[f"Output: {factor}"] = variable.varValue

        weight_rows.append(weight_row)

    report_path = Path(output_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
        pd.DataFrame(efficiency_rows).to_excel(
            writer, sheet_name="Efficiency Summary", index=False
        )
        df_inputs.to_excel(writer, sheet_name="Input Data")
        df_outputs.to_excel(writer, sheet_name="Output Data")
        pd.DataFrame(weight_rows).to_excel(writer, sheet_name="Weights", index=False)

    return report_path
