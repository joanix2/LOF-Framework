# LOF Framework — Language-Oriented Programming

**LOF** is a generative framework that transforms a declarative DSL into an autonomous software project (FastAPI + React). It validates the model before generation, produces code through Jinja templates and AST patches, then verifies the result with the project's native tools.

The generated project runs **independently** — it does not require LOF at runtime.

## Architecture

```mermaid
flowchart LR
    subgraph Source["📝 Source of Truth"]
        TYPES[("Types")]
        INST[("Instances")]
        TEMPL[("Templates")]
        PATCH[("Patches")]
        RULES[("Rules")]
    end

    subgraph LOF["⚡ LOF Framework"]
        COMPILER["Compiler<br/>Graph → Context → Render → Patch"]
        SMT["SMT Validator<br/>Z3"]
        REASON["Reasoning Engine<br/>Datalog"]
        GRAPH["Graph Engine<br/>NetworkX"]
    end

    subgraph Output["📦 Generated Project"]
        API["FastAPI Backend<br/>SQLAlchemy + Pydantic"]
        WEB["React Frontend<br/>TanStack Query + Zod"]
        DOCS[("Docs + Diagrams<br/>Mermaid")]
    end

    TYPES --> GRAPH
    INST --> GRAPH
    RULES --> REASON
    GRAPH --> COMPILER
    REASON --> COMPILER
    TEMPL --> COMPILER
    PATCH --> COMPILER
    COMPILER --> SMT
    SMT -->|SAT| COMPILER
    SMT -->|UNSAT| DIAG[("Diagnostics")]
    COMPILER --> API
    COMPILER --> WEB
    COMPILER --> DOCS

    style Source fill:#fef3c7,stroke:#d97706
    style LOF fill:#dbeafe,stroke:#2563eb
    style Output fill:#d1fae5,stroke:#059669
```

## Pipeline

```mermaid
flowchart TB
    subgraph Input["📥 Input Layer"]
        B[("Bronze<br/>Raw tickets<br/>Append-only")]
    end

    subgraph Semantic["🧠 Semantic Layer"]
        S[("Silver<br/>Open semantic graph<br/>spaCy NER + dependencies")]
        R["Reasoning<br/>Datalog fixpoint<br/>25 inference rules"]
        G[("Gold<br/>Canonical DSL<br/>Application model")]
    end

    subgraph Validation["✅ Validation Layer"]
        SCHEMA["JSON Schema<br/>Structural validation"]
        SMT["SMT Solver (Z3)<br/>Semantic consistency"]
        DECIDE{"SAT ?"}
    end

    subgraph Generation["⚙️ Generation Layer"]
        T["Jinja Templates<br/>Backend + Frontend"]
        P["AST Patches (LibCST)<br/>Structural transformations"]
        PROJ["📦 Generated Project<br/>FastAPI + React"]
    end

    subgraph Verification["🔍 Verification Layer"]
        LINT["Ruff + Prettier<br/>Static analysis"]
        TYPE["Pyright + tsc<br/>Type checking"]
        TEST["Pytest + Vitest<br/>Behavioral tests"]
        VALID["✅ Project Validated"]
    end

    B -->|spaCy extraction| S
    S -->|facts + provenance| R
    R -->|inferred facts| G
    G --> SCHEMA
    SCHEMA --> SMT
    SMT --> DECIDE
    DECIDE -->|"UNSAT / UNKNOWN"| DIAG[("📋 Diagnostics<br/>for LLM repair")]
    DIAG -.->|correction loop| G
    DECIDE -->|SAT| T
    T --> P
    P --> PROJ
    PROJ --> LINT
    LINT --> TYPE
    TYPE --> TEST
    TEST --> VALID

    style B fill:#fef3c7,stroke:#d97706,color:#000
    style S fill:#dbeafe,stroke:#2563eb,color:#000
    style R fill:#ede9fe,stroke:#7c3aed,color:#000
    style G fill:#d1fae5,stroke:#059669,color:#000
    style SMT fill:#fee2e2,stroke:#dc2626,color:#000
    style DECIDE fill:#fef3c7,stroke:#d97706,color:#000
    style DIAG fill:#fce7f3,stroke:#db2777,color:#000
    style PROJ fill:#dbeafe,stroke:#2563eb,color:#000
    style VALID fill:#d1fae5,stroke:#059669,color:#000
```

## Quick start

```bash
# Install
uv tool install lof-framework

# Create a project
lof new demo --profile fastapi-react --mode minimal
cd demo

# Compile
lof doctor
lof validate
lof compile
lof check

# Run (generated project is independent)
lof dev
```

Or without installing:

```bash
uvx lof-framework new demo --profile fastapi-react
```

## Generated project independence

The project in `generated/` is a fully standalone FastAPI + React application:

```bash
cd generated
make install
make test
make dev
```

No LOF runtime required.

## Modes

| Mode | Pipeline | Use case |
|------|----------|----------|
| **minimal** | Gold → validate → compile | Direct DSL authoring |
| **standard** | Tickets → Gold → compile | Assisted modeling |
| **intelligent** | Bronze → Silver → Reasoning → Gold → SMT → compile | Full pipeline with NER + inference |

## Project structure

```
my-project/
├── lof.toml           # Project configuration
├── app/
│   ├── bronze/        # Raw tickets (append-only)
│   ├── silver/        # Semantic graph
│   ├── gold/          # DSL application model
│   ├── rules/         # Inference rules
│   ├── constraints/   # SMT constraints
│   ├── templates/     # Jinja templates
│   ├── patches/       # AST patches
│   └── custom/        # User custom code
├── generated/         # Autonomous generated project
├── .lof/              # LOF internal data
└── tests/
```

## Installation from source

```bash
git clone <repo>
cd lof-framework
uv sync
uv run lof --help
```

## Status

**Alpha** — API is experimental and subject to change.

## License

MIT
