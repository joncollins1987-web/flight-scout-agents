from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HandoffEdge:
    from_agent: str
    to_agent: str


HANDOFF_GRAPH = [
    HandoffEdge("planner_judge", "scout_aggregator_1"),
    HandoffEdge("planner_judge", "scout_aggregator_2"),
    HandoffEdge("planner_judge", "deduper_normalizer"),
    HandoffEdge("deduper_normalizer", "constraints_lawyer"),
    HandoffEdge("constraints_lawyer", "strategic_ranker"),
    HandoffEdge("strategic_ranker", "verifier"),
    HandoffEdge("verifier", "strategic_ranker"),
    HandoffEdge("strategic_ranker", "stopover_itinerary"),
    HandoffEdge("strategic_ranker", "final_presenter"),
    HandoffEdge("stopover_itinerary", "final_presenter"),
]
