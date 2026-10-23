# Branch Operational Efficiency Assessment

**Python | pandas | PuLP | openpyxl | Data Envelopment Analysis (DEA)**

## Project Overview

This project implements a local Python workflow to assess the relative operational efficiency of branches using **Data Envelopment Analysis (DEA)**. The program reads branch input/output data from a structured text file, formulates and solves a linear programming model for each branch, and generates an Excel workbook containing efficiency scores, source data, and optimized model weights.

The workflow was inspired by a legacy Excel/VBA-based efficiency assessment process. It demonstrates a Python approach to data preparation, optimization, and reporting; **it has not been verified as an exact replacement for the original Excel/VBA Solver model**.

DEA compares branches within the supplied peer group. Its scores indicate *relative* efficiency under the implemented model, not absolute performance, causal effects, or prescribed management actions.

## Business Problem

Branches consume different combinations of resources (**inputs**) to produce services or operational results (**outputs**). Comparing them using a single metric may overlook differences in the resources used and outcomes produced.

DEA provides a framework for evaluating multiple inputs and outputs together, helping analysts identify branches on the observed efficiency frontier and branches that score below that frontier. The results can support comparative operational performance reviews, subject to the quality and representativeness of the input data.

## Implemented Features

- Parses a locally stored, comma-separated text file in the legacy three-line-per-branch format.
- Ignores blank lines, converts input/output values to numbers, and checks that each record has the expected number of values.
- Builds a **constant-returns-to-scale (CCR) DEA multiplier model** for each branch using PuLP.
- Solves the branch-level linear programs and captures solver status, relative efficiency scores, and optimized weights.
- Produces an Excel workbook with separate sheets for efficiency results, original inputs, original outputs, and model weights.

## Technology Stack

| Component | Technology | Role |
| --- | --- | --- |
| Programming | Python 3 | Local workflow and analysis logic |
| Data processing | pandas | Structured input/output data |
| Optimization | PuLP and a compatible LP solver | CCR DEA linear programming |
| Excel reporting | openpyxl | Workbook creation and formatting |
| Testing | Manual end-to-end verification | Current validation approach; automated pytest tests are not yet implemented |

## Workflow

```text
Local data/sample_dea.txt
          |
          v
Read and parse input/output records
          |
          v
Build branch-level DEA models with PuLP
          |
          v
Solve models and collect scores and weights
          |
          v
Generate output/dea_results.xlsx
```

The current workflow is **local only**. FTP transfers, Google Drive uploads, email delivery, and scheduling are not implemented.

## Input Data Format

The input is a comma-separated text file with a custom layout:

1. First nonblank line: names of the input factors.
2. Second nonblank line: names of the output factors.
3. Each branch then occupies three nonblank lines: branch name, input values, and output values.

Example (`data/sample_dea.txt`):

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

### Implemented Parser Checks

- Skips blank lines in the source file.
- Converts branch input and output values to numeric types.
- Checks that the number of input/output values matches the respective factor-name count.

Additional checks—such as duplicate branch names, non-finite values, negative values, and unsuitable zeros—are potential future enhancements. Support for different numbers of input/output factors should be verified against the implementation before relying on it for new datasets.

## DEA Optimization Model

A **decision-making unit (DMU)** is a branch. The implementation formulates a **CCR multiplier model** separately for each evaluated branch.

For branch \(o\), the objective is to maximize weighted outputs:


$$
max \sum_r u_r y_{ro}
$$
Subject to:

$$
\sum_i v_i x_{io}=1
\\
\sum_r u_r y_{rj}\leq\sum_i v_i x_{ij}
\quad\text{for every branch }j
\\u_r\geq0,\qquad v_i\geq0
$$
Where:

- \(x_{ij}\): input \(i\) used by branch \(j\).
- \(y_{rj}\): output \(r\) produced by branch \(j\).
- \(v_i\): weight assigned to input \(i\).
- \(u_r\): weight assigned to output \(r\).

With this model, an optimal efficiency score of **1** places a branch on the observed efficiency frontier; a score **below 1** indicates lower relative efficiency in the supplied dataset. Scores should only be interpreted for models with an appropriate optimal solver status.

`src/dea_model.py` constructs the DEA models. `src/report.py` solves them and writes the Excel output. The model has **not** been reconciled with the original VBA/Excel Solver configuration.

## Generated Excel Report

The workflow writes `output/dea_results.xlsx`, with the following information:

| Worksheet | Contents | Purpose |
| --- | --- | --- |
| Efficiency Summary | Branch, solver status, efficiency score | Compare relative branch efficiency and inspect solution status |
| Input Data | Original input quantities | Trace results back to the source resources |
| Output Data | Original output quantities | Review the outputs used in the model |
| Weights | Optimized input/output weights by branch | Inspect the model's selected factor weights |

Running the script again **overwrites the existing report** at this path.

## Project Structure

The project is intended to live inside a larger `portfolio-project` GitHub repository as its own folder:

```text
portfolio-project/
└── dea-automation/                  # Folder name may vary in your repository
    ├── README.md
    ├── requirements.txt
    ├── data/
    │   └── sample_dea.txt
    ├── src/
    │   ├── parser.py
    │   ├── dea_model.py
    │   └── report.py
    └── output/                      # Generated workbook saved here
```

## How to Run

From the **DEA project folder**, install the dependencies listed in `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

Then run:

```powershell
python src\parser.py
```

The program reads `data/sample_dea.txt` and generates `output/dea_results.xlsx`. This command reflects the completed project workflow described in the existing implementation README.

## Validation and Project Outcome

The local sample workflow was executed end to end. **All four sample branch models solved to optimality**, and the generated Excel workbook was checked for its expected sheets and results. Python compilation also passed.

The completed project demonstrates how Python can combine structured data processing, linear programming, and standardized spreadsheet reporting in one repeatable local analytical workflow. It is a **working DEA assessment**, not a production-integrated automation service or a verified one-for-one migration of the legacy VBA solution.

**Testing limitation:** There are currently no automated test cases in the project; `pytest` does not collect tests.

## Limitations and Future Improvements

- Reconcile the implemented DEA objective, constraints, and numerical results with the legacy Excel/VBA Solver setup.
- Add automated parser, model, and report tests with `pytest`.
- Expand input validation to handle duplicate names, invalid numeric values, negative quantities, and edge cases.
- Verify and document dynamic support for datasets with different counts of input and output factors.
- Consider optional FTP ingestion, cloud storage, email distribution, and scheduled execution after the local workflow is fully validated.

## Data and Repository Safety

Use only public, synthetic, or appropriately anonymized branch data in a public GitHub portfolio. Do not commit confidential operational data, API credentials, or stakeholder contact information. Generated reports should also be reviewed before publication.
