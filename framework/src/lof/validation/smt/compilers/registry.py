
from lof.validation.smt.solver import ConstraintCompiler

_COMPILERS: dict[str, ConstraintCompiler] = {}


def register(compiler: ConstraintCompiler) -> None:
    _COMPILERS[compiler.constraint_type] = compiler


def get(constraint_type: str) -> ConstraintCompiler | None:
    return _COMPILERS.get(constraint_type)


COMPILERS = _COMPILERS
