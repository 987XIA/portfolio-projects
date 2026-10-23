# Branch Operational Efficiency Assessment

## Project Overview

This project assesses the relative operational efficiency of branches using Data Envelopment Analysis (DEA). It reads local branch input/output data, builds and solves one DEA model per branch, and generates an Excel report.

The assessment compares branches in the supplied dataset. It supports operational performance review; it does not measure absolute performance, establish causation, or prescribe management decisions. The current workflow ends when the local Excel report is generated.

## Business Problem

Each branch consumes multiple resources (inputs) and produces multiple services or results (outputs). DEA evaluates branches relative to the peer group represented in the supplied data.

## Project Objectives

1. Read and parse the local branch input/output data.
2. Calculate relative efficiency scores for each branch using DEA.
3. Produce an Excel report with scores, source data, and model weights.

The implemented DEA formulation has not been reconciled against the original VBA/Solver setup. Interpret results as comparisons under this model.

## Technology Stack

| Component       | Proposed technology                                | Purpose                                       |
| --------------- | -------------------------------------------------- | --------------------------------------------- |
| Programming     | Python 3                                           | Workflow orchestration and business logic     |
| Data processing | pandas                                             | Structured input/output tables                |
| Optimization    | PuLP with a compatible LP solver                   | DEA linear programming models                 |
| Excel reporting | openpyxl                                           | Generate and format `.xlsx` reports           |
| Testing         | pytest                                             | Available for automated tests; test cases are a future improvement |

## Workflow

```text
Local sample_dea.txt
          |
          v
Read and parse input data
          |
          v
Build and solve DEA models
          |
          v
Generate local Excel report
```

The workflow ends with the Excel report. FTP transfer, cloud storage, email delivery, and scheduling are possible future improvements, not current deliverables.

## Input Data: DEA.txt

The legacy input is a comma-separated text file without a conventional header row for branch records.
Line 1 lists input factor names; line 2 lists output factor names.
Each subsequent branch occupies three lines: branch name, input values, and output values.
The number of input and output factors should be determined dynamically from the first two lines.

Example structure:

```text
Faculty,Support Staff,Supply Budget

Credit Hours,Research Pubs

Business

150,70,5

15.0,225

Education

60,20,3

5.4,70
```

### Parser Checks and Future Validation

The parser ignores blank lines, converts branch values to numbers, and checks that input/output counts match their factor names. Potential future checks include duplicate names, non-finite or negative values, and zero or otherwise unsuitable quantities.

## DEA Optimization Model

DEA compares decision-making units (DMUs), here the branches, using multiple inputs and outputs.
The implementation builds one constant-returns-to-scale (CCR) multiplier model for each evaluated branch.
For each evaluated branch, the model maximizes weighted outputs while normalizing its weighted inputs to 1 and limiting every branch's weighted outputs to its weighted inputs.

For evaluated branch `o`, maximize:

`sum_r(u[r] * y[r,o])`

subject to:

- `sum_i(v[i] * x[i,o]) = 1` (normalize the evaluated branch's weighted inputs)
- `sum_r(u[r] * y[r,j]) <= sum_i(v[i] * x[i,j])` for every branch `j`
- `u[r] >= 0` and `v[i] >= 0` for all output and input weights.

Here `x` and `y` represent input and output quantities, and `v` and `u` are input and output weights. The solved objective value is the branch's relative efficiency score: 1 indicates the observed efficiency frontier, while a value below 1 indicates lower relative efficiency within this dataset.

`src/dea_model.py` builds the models, and `src/report.py` solves them and writes the results to `output/dea_results.xlsx`. This implemented model has not been confirmed against the original VBA/Solver settings.

## Expected Report

The Excel workbook contains an **Efficiency Summary** (branch, solver status, and score), the original **Input Data** and **Output Data**, and the optimized **Weights** for each branch.

Run the complete workflow from the project directory:

```powershell
python src\parser.py
```

The workflow reads `data/sample_dea.txt` and writes `output/dea_results.xlsx`, replacing the previous report if one exists.

## Project Structure

```text
branch-efficiency-dea-automation/
├── data/
│   └── sample_dea.txt
├── output/
├── src/
│   ├── parser.py
│   ├── dea_model.py
│   ├── report.py
├── requirements.txt
└── README.md
```

Real operational data, credentials, and stakeholder email addresses must not be committed to a public repository.

## Validation and Future Improvements

The sample workflow was run end to end: all four sample models solved optimally, and the generated workbook was verified to contain the expected sheets and results. Python compilation also passed. There are currently no automated test files in `tests/`, so pytest collects no tests.

Possible future improvements include adding automated tests, strengthening input validation, and reconciling the implemented formulation with the original VBA/Solver setup. These are not required to complete the current assessment workflow, which ends with the Excel report.
