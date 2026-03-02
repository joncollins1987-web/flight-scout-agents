from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.agents.constraints_lawyer import ConstraintsOutput
from app.agents.deduper_normalizer import NormalizedCandidateSet
from app.agents.final_presenter import FinalPresenterOutput
from app.agents.planner_judge import PlannerJudgeOutput
from app.agents.scout_aggregator_1 import ScoutAggregatorOutput as ScoutOneOutput
from app.agents.scout_aggregator_2 import ScoutAggregatorOutput as ScoutTwoOutput
from app.agents.stopover_itinerary import StopoverBatch
from app.agents.strategic_ranker import StrategicRankOutput
from app.agents.verifier import VerificationBatch

try:
    from agents import Agent
except Exception:  # pragma: no cover
    Agent = None  # type: ignore[assignment]


@dataclass
class AgentBundle:
    planner_judge: Any
    scout_aggregator_1: Any
    scout_aggregator_2: Any
    deduper_normalizer: Any
    constraints_lawyer: Any
    verifier: Any
    strategic_ranker: Any
    stopover_itinerary: Any
    final_presenter: Any


def build_agent_bundle(model: str) -> AgentBundle:
    if Agent is None:
        return AgentBundle(
            planner_judge=None,
            scout_aggregator_1=None,
            scout_aggregator_2=None,
            deduper_normalizer=None,
            constraints_lawyer=None,
            verifier=None,
            strategic_ranker=None,
            stopover_itinerary=None,
            final_presenter=None,
        )

    scout_one = Agent(
        name="Scout_Aggregator_1",
        handoff_description="Scouts source 1 and returns strict RawItineraryCandidate JSON.",
        instructions="Return only JSON matching ScoutAggregatorOutput.",
        model=model,
        output_type=ScoutOneOutput,
    )
    scout_two = Agent(
        name="Scout_Aggregator_2",
        handoff_description="Scouts source 2 and returns strict RawItineraryCandidate JSON.",
        instructions="Return only JSON matching ScoutAggregatorOutput.",
        model=model,
        output_type=ScoutTwoOutput,
    )
    deduper = Agent(
        name="Deduper_Normalizer",
        handoff_description="Normalizes and deduplicates raw candidate data.",
        instructions="Return only JSON matching NormalizedCandidateSet.",
        model=model,
        output_type=NormalizedCandidateSet,
    )
    constraints = Agent(
        name="Constraints_Lawyer",
        handoff_description="Flags fare and connection constraints.",
        instructions="Return only JSON matching ConstraintsOutput.",
        model=model,
        output_type=ConstraintsOutput,
    )
    verifier = Agent(
        name="Verifier",
        handoff_description="Verifies prices/rules and returns strict verification JSON.",
        instructions="Return only JSON matching VerificationBatch.",
        model=model,
        output_type=VerificationBatch,
    )
    ranker = Agent(
        name="Strategic_Ranker",
        handoff_description="Ranks itineraries with explainable weighted scoring.",
        instructions="Return only JSON matching StrategicRankOutput.",
        model=model,
        output_type=StrategicRankOutput,
    )
    stopover = Agent(
        name="Stopover_Itinerary",
        handoff_description="Generates short stopover plans for long layovers.",
        instructions="Return only JSON matching StopoverBatch.",
        model=model,
        output_type=StopoverBatch,
    )
    final_presenter = Agent(
        name="Final_Presenter",
        handoff_description="Builds final tabbed response object.",
        instructions="Return only JSON matching FinalPresenterOutput.",
        model=model,
        output_type=FinalPresenterOutput,
    )
    planner = Agent(
        name="Planner_Judge",
        handoff_description="Validates search intent and dispatches specialist agents.",
        instructions=(
            "Validate request, expand date combinations, set scoring policy, and hand off to scout/deduper agents. "
            "Return JSON only."
        ),
        model=model,
        output_type=PlannerJudgeOutput,
        handoffs=[scout_one, scout_two, deduper],
    )
    # Additional explicit handoff topology on downstream agents.
    deduper.handoffs = [constraints]
    constraints.handoffs = [ranker]
    ranker.handoffs = [verifier, stopover, final_presenter]
    verifier.handoffs = [ranker]
    stopover.handoffs = [final_presenter]

    return AgentBundle(
        planner_judge=planner,
        scout_aggregator_1=scout_one,
        scout_aggregator_2=scout_two,
        deduper_normalizer=deduper,
        constraints_lawyer=constraints,
        verifier=verifier,
        strategic_ranker=ranker,
        stopover_itinerary=stopover,
        final_presenter=final_presenter,
    )
