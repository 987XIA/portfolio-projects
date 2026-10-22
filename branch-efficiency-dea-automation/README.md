# Branch Operational Efficiency Analysis Automation

## Project Overview

This project modernizes a legacy Excel/VBA-based branch performance analysis workflow into a Python-based automation pipeline.
The case study concerns Queen's Financial Alliance (QFA), which compares the relative operational efficiency of its branches using Data Envelopment Analysis (DEA).
The planned solution reads branch input/output data, solves linear programming models with PuLP, generates Excel reports, and supports automated delivery to stakeholders.

**Project status:** In development. The original Solver formulation and external integration details require confirmation.

## Business Problem

QFA operates more than 20 branches across North America and needs a consistent way to compare their operational performance.
Each branch consumes multiple resources (inputs) and produces multiple services or results (outputs).
Management needs relative efficiency scores, benchmarks, and evidence to inform performance improvement and resource allocation.
DEA evaluates branches relative to the observed peer group; it does not measure absolute performance or establish causation.

## Project Objectives

1. Replace manual or VBA-dependent processing with reproducible Python code.
2. Read and validate the existing `DEA.txt` input format.
3. Reproduce the legacy DEA optimization logic using PuLP, subject to model verification.
4. Calculate and compare efficiency results for each branch.
5. Export understandable Excel reports for business stakeholders.
6. Add FTP data transfer, Google Drive storage, and email distribution after the local workflow is validated.

## Planned Technology Stack

| Component       | Proposed technology                                | Purpose                                       |
| --------------- | -------------------------------------------------- | --------------------------------------------- |
| Programming     | Python 3                                           | Workflow orchestration and business logic     |
| Data processing | pandas                                             | Structured input/output tables                |
| Optimization    | PuLP with a compatible LP solver                   | DEA linear programming models                 |
| Excel reporting | openpyxl                                           | Generate and format `.xlsx` reports           |
| File transfer   | FTP client (protocol and security to be confirmed) | Retrieve or transfer input files              |
| Cloud storage   | Google Drive API                                   | Store generated reports                       |
| Notifications   | Email integration (method to be confirmed)         | Deliver results to stakeholders               |
| Testing         | pytest                                             | Validate parsing, optimization, and reporting |

## Proposed Workflow

```text
FTP source / local dea.txt
          |
          v
Read and validate input data
          |
          v
Build branch input/output matrices
          |
          v
Run DEA linear programs with PuLP
          |
          v
Validate scores against legacy results
          |
          v
Generate Excel report
          |
          +----> Google Drive storage
          |
          +----> Email distribution
```

The first release will run locally; external services will be integrated in a later phase.

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

### Input Validation Rules

- Ignore only intentionally permitted blank lines; document how they are handled.
- Ensure each branch record contains exactly three logical lines.
- Ensure input and output value counts match their respective factor-name counts.
- Convert numeric values safely and reject missing, malformed, or non-finite values.
- Reject duplicate branch names and duplicate factor names unless explicitly supported.
- Check non-negativity and flag zero or otherwise unsuitable values for DEA model review.
- Return actionable error messages that identify the affected branch or line.

## DEA Optimization Model

DEA compares decision-making units (DMUs), here the branches, using multiple inputs and outputs.
The historical document suggests normalization of weighted inputs to 1 and maximization of weighted outputs for each evaluated branch.
A candidate constant-returns-to-scale (CCR) multiplier formulation is shown below, but **it is not yet verified as the legacy model**.

For evaluated branch `o`, maximize `sum_r(u[r] * y[r,o])`, subject to:

- `sum_i(v[i] * x[i,o]) = 1`
- `sum_r(u[r] * y[r,j]) <= sum_i(v[i] * x[i,j])` for every branch `j`
- `u[r] >= 0` and `v[i] >= 0`, subject to any verified additional bounds.

Here `x` represents inputs, `y` outputs, `v` input weights, and `u` output weights.
One linear program is solved per evaluated branch; PuLP formulates the model and a solver computes the optimum.
The final mathematical formulation, orientation, weight restrictions, and interpretation of efficiency must be checked against the original VBA/Solver settings and legacy outputs.

## Expected Report

The Python version will aim to preserve the business meaning of the legacy report.

1. **Efficiency Summary:** branch name, efficiency score, and efficient/inefficient classification where justified by the verified model.
2. **Original Data:** the source input and output quantities for each branch.
3. **Optimization Results:** optimized weights and/or weighted input/output values, with definitions matching the legacy report.
   Optional charts and rankings can be added after numeric validation.

## Proposed Repository Structure

```text
branch-dea-automation/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── sample_dea.txt
├── src/
│   ├── parser.py
│   ├── dea_model.py
│   ├── report.py
│   └── pipeline.py
├── tests/
│   ├── test_parser.py
│   └── test_dea_model.py
└── output/
```

The structure is a proposed target, not a claim that these modules have already been implemented.
Real operational data, credentials, and stakeholder email addresses must not be committed to a public repository.

## Development Milestones

| Milestone                  | Deliverable                         | Acceptance criteria                                         |
| -------------------------- | ----------------------------------- | ----------------------------------------------------------- |
| M1 — Input parser          | `src/parser.py` and parser tests    | Correctly parse the actual `dea.txt` into validated tables  |
| M2 — Single-unit DEA       | First PuLP model                    | Solve one branch and inspect solver status and constraints  |
| M3 — All-unit DEA          | Efficiency results for every branch | Produce one traceable result per branch                     |
| M4 — Legacy reconciliation | Comparison against VBA output       | Explain and resolve material score differences              |
| M5 — Local reporting       | Excel workbook                      | Generate a readable workbook from a single local run        |
| M6 — Delivery automation   | FTP, Drive, and email workflow      | Demonstrate a controlled end-to-end run with error handling |

## Milestone 1: TXT Parsing and Validation

**Input:** the existing `dea.txt` file, stored locally outside version control if it contains sensitive data.
**Output:** factor-name lists and a structured table with one row per branch and columns for all input and output factors.
**Implementation tasks:** inspect encoding and line endings; parse headers; group three-line branch records; validate values; create DataFrames; write unit tests.
**Definition of done:** every source branch appears exactly once, values map to the correct factors, and invalid files produce clear errors.
**Checkpoint:** compare the parsed output manually against several records in the source file before beginning optimization.

### Parser functions

`import_dea_data()` reads `data/sample_dea.txt`, removes blank lines and
surrounding whitespace, and writes the result to `data/dea_cleansed.txt`.

`rearrange_data_for_modeling()` reads the cleansed file line by line. It reads
the input and output factor names, then reads each branch name and its input
and output value lines. It validates that the values are numeric and that
their counts match the factor names, then splits each value line on commas,
trims surrounding whitespace, and converts each value to a float.

After parsing, `var_inputs` and `var_outputs` contain factor-name lists,
`var_units` contains branch names, and `data_inputs` and `data_outputs` each
contain a list of float values for every branch. Items at the same index in
these lists refer to the same branch. For example, the Business branch has
input values `[150.0, 70.0, 5.0]` and output values `[15.0, 225.0]`.
The function returns two pandas DataFrames: `(df_inputs, df_outputs)`.
Each DataFrame has one row per branch, its corresponding factors as columns,
and branch names as the index. For example:

```python
df_inputs, df_outputs = rearrange_data_for_modeling()
```

## Verification and Open Questions

- Obtain or reconstruct the exact legacy Solver objective, variable cells, and constraints.
- Confirm whether the original model uses CCR, another DEA formulation, or additional weight restrictions.
- Confirm the meanings of optimized input/output values in the legacy report.
- Confirm FTP transfer direction, protocol security, authentication, and scheduling.
- Confirm Google Drive destination, access permissions, and email delivery method.
- Confirm whether real branch data can be used in a public portfolio; otherwise use synthetic data.

## Current Status and Next Step

The legacy design documentation and partial data-flow diagram have been reviewed, and the actual `dea.txt` input file is available to the project owner.
The immediate next step is **M1: build and test the TXT parser** before implementing DEA optimization.
