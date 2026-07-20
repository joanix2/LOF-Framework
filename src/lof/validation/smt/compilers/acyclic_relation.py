from collections.abc import Sequence

import z3

from lof.validation.smt.constraint_definition import ConstraintDefinition
from lof.validation.smt.context import ConstraintContext
from lof.validation.smt.solver import NamedAssertion


class AcyclicRelationCompiler:
    constraint_type = "acyclic-relation"

    def compile(
        self,
        definition: ConstraintDefinition,
        context: ConstraintContext,
    ) -> Sequence[NamedAssertion]:
        assertions: list[NamedAssertion] = []
        kinds = set(definition.parameters.get("kinds", []))

        graph: dict[str, list[str]] = {}
        for rel in context.relations_index:
            if kinds and rel["kind"] not in kinds:
                continue
            graph.setdefault(rel["source"], []).append(rel["target"])

        visited: set[str] = set()
        path: list[str] = []

        def dfs(node: str) -> bool:
            if node in path:
                cycle = path[path.index(node) :] + [node]
                assertions.append(
                    NamedAssertion(
                        name=f"acyclic_{'_'.join(cycle)}",
                        expression=z3.BoolVal(False),
                        constraint_id=definition.id,
                        instance_ids=tuple(cycle),
                        json_paths=tuple(f"$.instances.{n}" for n in cycle),
                        metadata={"cycle": cycle},
                    )
                )
                return True
            if node in visited:
                return False
            visited.add(node)
            path.append(node)
            for neighbor in graph.get(node, []):
                if dfs(neighbor):
                    path.pop()
                    return True
            path.pop()
            return False

        for node in list(graph.keys()):
            dfs(node)

        if not assertions:
            assertions.append(
                NamedAssertion(
                    name="acyclic_all",
                    expression=z3.BoolVal(True),
                    constraint_id=definition.id,
                )
            )

        return assertions
