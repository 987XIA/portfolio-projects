from pulp import LpMaximize, LpProblem, LpVariable, lpSum


def build_dea_model(var_inputs, var_outputs, var_units, data_inputs, data_outputs):
    """Build one DEA optimization model for each decision-making unit."""
    if any(
        value is None
        for value in (var_inputs, var_outputs, var_units, data_inputs, data_outputs)
    ):
        raise ValueError("DEA data must be provided before building the model")

    models = []
    for unit_index in range(len(var_units)):
        input_weights = [
            LpVariable(f"input_weight_{unit_index}_{index}", lowBound=0)
            for index in range(len(var_inputs))
        ]
        output_weights = [
            LpVariable(f"output_weight_{unit_index}_{index}", lowBound=0)
            for index in range(len(var_outputs))
        ]
        problem = LpProblem(f"DEA_{unit_index}", LpMaximize)
        problem += lpSum(
            output_weights[index] * data_outputs[unit_index][index]
            for index in range(len(var_outputs))
        )
        problem += lpSum(
            input_weights[index] * data_inputs[unit_index][index]
            for index in range(len(var_inputs))
        ) == 1, f"normalize_{unit_index}"

        for peer_index in range(len(var_units)):
            weighted_outputs = lpSum(
                output_weights[index] * data_outputs[peer_index][index]
                for index in range(len(var_outputs))
            )
            weighted_inputs = lpSum(
                input_weights[index] * data_inputs[peer_index][index]
                for index in range(len(var_inputs))
            )
            problem += (
                weighted_outputs <= weighted_inputs,
                f"efficiency_{unit_index}_{peer_index}",
            )

        models.append(problem)

    return models
