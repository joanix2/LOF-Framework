"""Z3 solver adapter implementing SemanticSolverPort."""

from collections.abc import Sequence

import z3

from lof.validation.smt.constraint_definition import (
    ConstraintDefinition,
    ConstraintViolation,
    SolverResult,
)
from lof.validation.smt.context import ConstraintContext
from lof.validation.smt.solver import NamedAssertion


class Z3SolverAdapter:
    def validate(
        self, context: "ConstraintContext", constraints: Sequence[ConstraintDefinition]
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
                        )
                    ],
                )

        for a in all_assertions:
            solver.assert_and_track(a.expression, a.name)

        check = solver.check()

        if check == z3.sat:
            return SolverResult(status="sat")

        if check == z3.unsat:
            core = list(solver.unsat_core())
            core_names = [str(d) for d in core] if core else []
            core_as = (
                [a for a in all_assertions if a.name in core_names]
                if core_names
                else all_assertions
            )  # noqa: E501
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
                for a in core_as
            ] or [
                ConstraintViolation(
                    constraint_id="root",
                    code="UNSAT",
                    message="Model is unsatisfiable.",
                    unsat_core=core_names,
                )
            ]
            return SolverResult(status="unsat", diagnostics=violations)

        return SolverResult(status="unknown")
