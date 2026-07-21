"""Inference rules for the mobile-field profile (Expo + React Native)."""

from lof.reasoning.models import Conclusion, Condition, Rule

MOBILE_FIELD_RULES = [
    Rule(
        id="employee_creates_mission",
        description="An employee is assigned to missions they can work on",
        mode="certain",
        category="projection",
        when=[
            Condition(predicate="employee", vars=["eid"]),
            Condition(predicate="assigned_to", vars=["eid", "mid"]),
        ],
        then=[Conclusion(predicate="can_work_on", vars=["eid", "mid"])],
    ),
    Rule(
        id="mission_has_status",
        description="A mission always has a current status",
        mode="certain",
        category="projection",
        when=[Condition(predicate="mission", vars=["mid"])],
        then=[Conclusion(predicate="has_status", vars=["mid"])],
    ),
    Rule(
        id="requires_equipment_check",
        description="Mission requires equipment check before starting",
        mode="certain",
        category="projection",
        when=[Condition(predicate="mission", vars=["mid"])],
        then=[Conclusion(predicate="requires_checklist", vars=["mid", "_equipment"])],
    ),
    Rule(
        id="requires_safety_check",
        description="Mission requires safety checklist before starting",
        mode="certain",
        category="projection",
        when=[Condition(predicate="mission", vars=["mid"])],
        then=[Conclusion(predicate="requires_checklist", vars=["mid", "_safety"])],
    ),
    Rule(
        id="entity_to_screen",
        description="Entity type maps to a screen",
        mode="certain",
        category="projection",
        when=[Condition(predicate="type", vars=["type_id"])],
        then=[Conclusion(predicate="requires_projection", vars=["type_id", "_screen"])],
    ),
    Rule(
        id="operation_to_service",
        description="Operation maps to a service method",
        mode="certain",
        category="projection",
        when=[
            Condition(predicate="type", vars=["type_id"]),
            Condition(predicate="has_operation", vars=["type_id", "op"]),
        ],
        then=[Conclusion(predicate="requires_projection", vars=["op", "_service_method"])],
    ),
]

__all__ = ["MOBILE_FIELD_RULES"]
