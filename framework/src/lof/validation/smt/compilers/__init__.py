from lof.validation.smt.compilers.acyclic_relation import AcyclicRelationCompiler
from lof.validation.smt.compilers.cardinality_compatible import CardinalityCompatibleCompiler
from lof.validation.smt.compilers.dependency_satisfied import DependencySatisfiedCompiler
from lof.validation.smt.compilers.field_type_compatible import FieldTypeCompatibleCompiler
from lof.validation.smt.compilers.operation_requires import OperationRequiresProjectionCompiler
from lof.validation.smt.compilers.registry import COMPILERS, get, register
from lof.validation.smt.compilers.relation_target import RelationTargetExistsCompiler
from lof.validation.smt.compilers.required_property import RequiredPropertyCompiler
from lof.validation.smt.compilers.unique_property import UniquePropertyCompiler

register(UniquePropertyCompiler())
register(RequiredPropertyCompiler())
register(RelationTargetExistsCompiler())
register(AcyclicRelationCompiler())
register(DependencySatisfiedCompiler())
register(CardinalityCompatibleCompiler())
register(FieldTypeCompatibleCompiler())
register(OperationRequiresProjectionCompiler())

__all__ = ["register", "get", "COMPILERS"]
