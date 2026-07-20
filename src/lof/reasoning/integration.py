from pathlib import Path

from lof.reasoning import DatalogEngine, FactEncoder, GoldMaterializer, get_profile
from lof.silver.graph import SilverGraph


def silver_to_gold_via_reasoning(
    silver: SilverGraph,
    output_dir: Path,
    profile_id: str = "fastapi-react",
) -> list[Path]:
    encoder = FactEncoder()
    facts = encoder.encode(silver)
    rules = get_profile(profile_id)
    engine = DatalogEngine(rules)
    result = engine.evaluate(facts)
    materializer = GoldMaterializer(rules)
    entities = materializer.materialize(result)
    return materializer.write_gold(entities, output_dir)
