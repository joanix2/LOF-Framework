from dataclasses import dataclass, field
from enum import Enum


class NodeState(Enum):
    INITIAL = "initial"
    TRANSFORMED = "transformed"
    FINAL = "final"


@dataclass
class GraphNode:
    instance_id: str
    type_id: str
    state: NodeState = NodeState.INITIAL
    source: str | None = None
    patches_applied: list[str] = field(default_factory=list)
    output_path: str | None = None


@dataclass
class CompilerEdge:
    source_node: str
    target_node: str
    patch_id: str | None = None


class CompilerGraph:
    def __init__(self):
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[CompilerEdge] = []

    def add_node(self, node: GraphNode) -> str:
        key = f"{node.instance_id}:{node.state.value}"
        self.nodes[key] = node
        return key

    def add_edge(self, source_key: str, target_key: str, patch_id: str | None = None) -> None:
        self.edges.append(CompilerEdge(source_key, target_key, patch_id))

    def get_node(self, key: str) -> GraphNode | None:
        return self.nodes.get(key)

    def get_final_key(self, instance_id: str) -> str | None:
        for key, node in self.nodes.items():
            if node.instance_id == instance_id and node.state == NodeState.FINAL:
                return key
        return None
