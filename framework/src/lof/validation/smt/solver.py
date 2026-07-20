from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

import z3

from lof.validation.smt.constraint_definition import (
    ConstraintDefinition,
    ConstraintViolation,
    SolverResult,
)
from lof.validation.smt.context import ConstraintContext


@dataclass(frozen=True)
class NamedAssertion:
    name: str
    expression: object
    constraint_id: str
    instance_ids: tuple[str, ...] = field(default_factory=tuple)
    type_ids: tuple[str, ...] = field(default_factory=tuple)
    json_paths: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)


class ConstraintCompiler(Protocol):
    constraint_type: str

    def compile(
        self,
        definition: ConstraintDefinition,
        context: "ConstraintContext",
    ) -> Sequence[NamedAssertion]:
        ...


class SemanticSolver(Protocol):
    def validate(
        self,
        context: "ConstraintContext",
        constraints: Sequence[ConstraintDefinition],
    ) -> SolverResult:
        ...


class Z3SemanticSolver:
    def validate(
        self,
        context: "ConstraintContext",
        constraints: Sequence[ConstraintDefinition],
    ) -> SolverResult:
        solver = z3.Solver()
        all_assertions: list[NamedAssertion] = []

        for constraint in constraints:
            if not constraint.enabled:
                continue
            from lof.validation.smt.compilers.registry import COMPILERS
            compiler = COMPILERS.get(constraint.type)
            if compiler is None:
                continue
            try:
                assertions = compiler.compile(constraint, context)
                all_assertions.extend(assertions)
            except Exception as e:
                return SolverResult(
                    status="unknown",
                    diagnostics=[
                        ConstraintViolation(
                            constraint_id=constraint.id,
                            code="COMPILER_ERROR",
                            message=f"Compiler '{constraint.type}' failed: {e}",
                            hint="Check constraint parameters.",
                        )
                    ],
                )

        for a in all_assertions:
            solver.assert_and_track(a.expression, a.name)

        check_result = solver.check()

        if check_result == z3.sat:
            return SolverResult(status="sat")

        if check_result == z3.unsat:
            core = list(solver.unsat_core())
            core_names = [str(d) for d in core] if core else []
            core_assertions = [a for a in all_assertions if a.name in core_names] or all_assertions

            violations = [
                ConstraintViolation(
                    constraint_id=a.constraint_id,
                    code="UNSAT_CORE",
                    message=a.metadata.get("message", f"Constraint violated: {a.name}"),
                    hint=a.metadata.get("hint"),
                    instance_ids=list(a.instance_ids),
                    type_ids=list(a.type_ids),
                    json_paths=list(a.json_paths),
                    unsat_core=core_names,
                    values=dict(a.metadata),
                )
                for a in core_assertions
            ]

            if not violations:
                violations.append(
                    ConstraintViolation(
                        constraint_id="root",
                        code="UNSAT",
                        message="Model is unsatisfiable.",
                        unsat_core=core_names,
                    )
                )
            return SolverResult(status="unsat", diagnostics=violations)

        return SolverResult(status="unknown")
