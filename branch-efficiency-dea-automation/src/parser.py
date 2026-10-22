import pandas as pd
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
data_folder = "data"
fn_dea_local = "sample_dea.txt"
fn_dea_cleansed = "dea_cleansed.txt"

var_inputs = None
var_outputs = None
var_units = None

data_inputs = None
data_outputs = None


def import_dea_data():
    """Read a text file from the project's data folder."""
    input_path = PROJECT_DIR / data_folder / fn_dea_local
    output_path = PROJECT_DIR / data_folder / "dea_cleansed.txt"

    lines = [
        line.strip()
        for line in input_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    lines_data = "\n".join(lines)
    if lines_data:
        lines_data += "\n"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(lines_data, encoding="utf-8")
    print(lines_data, end="")


def rearrange_data_for_modeling():
    global var_inputs, var_outputs, var_units, data_inputs, data_outputs

    path = PROJECT_DIR / data_folder / fn_dea_cleansed
    with path.open("r", encoding="utf-8") as fp:
        numbered_lines = enumerate(fp, start=1)

        def next_value():
            for line_number, line in numbered_lines:
                value = line.strip()
                if value:
                    return line_number, value
            return None, None

        def required_value(description):
            line_number, value = next_value()
            if value is None:
                raise ValueError(f"Missing {description} in {path}")
            return line_number, value

        def validate_values(value, unit, line_number):
            try:
                for item in value.split(","):
                    float(item.strip())
            except ValueError as error:
                raise ValueError(
                    f"Invalid numeric value for {unit!r} on line {line_number}"
                ) from error

        _, input_names = required_value("input factor names")
        _, output_names = required_value("output factor names")
        var_inputs = [name.strip() for name in input_names.split(",")]
        var_outputs = [name.strip() for name in output_names.split(",")]

        if not all(var_inputs) or not all(var_outputs):
            raise ValueError(f"Factor names cannot be empty in {path}")

        var_units = []
        data_inputs = []
        data_outputs = []

        while True:
            unit_line, unit = next_value()
            if unit is None:
                break

            input_line, input_values = required_value(
                f"input values for {unit!r} after line {unit_line}"
            )
            output_line, output_values = required_value(
                f"output values for {unit!r} after line {input_line}"
            )

            validate_values(input_values, unit, input_line)
            validate_values(output_values, unit, output_line)

            input_count = len(input_values.split(","))
            output_count = len(output_values.split(","))
            if input_count != len(var_inputs):
                raise ValueError(
                    f"{unit!r} has {input_count} input values; "
                    f"expected {len(var_inputs)}"
                )
            if output_count != len(var_outputs):
                raise ValueError(
                    f"{unit!r} has {output_count} output values; "
                    f"expected {len(var_outputs)}"
                )

            var_units.append(unit)
            data_inputs.append(
                [float(value.strip()) for value in input_values.split(",")]
            )
            data_outputs.append(
                [float(value.strip()) for value in output_values.split(",")]
            )

    print(f"Rearranged data for {len(var_units)} units")

    df_inputs = pd.DataFrame(
        data_inputs,
        columns=var_inputs,
        index=pd.Index(var_units, name="Branch"),
    )
    df_outputs = pd.DataFrame(
        data_outputs,
        columns=var_outputs,
        index=pd.Index(var_units, name="Branch"),
    )
    print("Input DataFrame:")
    print(df_inputs)
    print("Output DataFrame:")
    print(df_outputs)
    return df_inputs, df_outputs


def build_dea_model():
    pass


def report_dea_results():
    pass


if __name__ == "__main__":
    import_dea_data()
    rearrange_data_for_modeling()
    build_dea_model()
    report_dea_results()
