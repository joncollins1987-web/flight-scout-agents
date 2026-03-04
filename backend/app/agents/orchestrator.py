from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from app.agents.constraints_lawyer import ConstraintsOutput, apply_constraints
from app.agents.deduper_normalizer import NormalizedCandidateSet, normalize_and_dedupe
from app.agents.factory import AgentBundle, build_agent_bundle
from app.agents.final_presenter import FinalPresenterOutput, present_final
from app.agents.planner_judge import PlannerJudgeOutput, local_plan
from app.agents.schema_guard import BranchHardFailError, SchemaGuard
from app.agents.scout_aggregator_1 import ScoutAggregatorOutput as ScoutOneOutput
from app.agents.scout_aggregator_2 import ScoutAggregatorOutput as ScoutTwoOutput
from app.agents.stopover_itinerary import StopoverBatch, generate_stopover_plans
from app.agents.strategic_ranker import StrategicRankOutput, rank_itineraries
from app.agents.verifier import VerificationBatch, verify_itineraries
from app.core.artifact_store import ArtifactStore
from app.core.cache import expires_at
from app.core.config import settings
from app.core.logging import get_logger
from app.core.pricing import apply_verification_to_normalized
from app.core.retries import with_retries
from app.core.hashing import model_hash
from app.db.repositories import (
    create_run,
    get_candidates_for_run,
    get_final_result,
    get_latest_run_by_hash,
    get_latest_run_any_age,
    save_candidates,
    save_final_result,
    save_verified,
    update_run_status,
)
from app.schemas.itinerary import NormalizedItinerary, RawItineraryCandidate
from app.schemas.request import SearchRequest
from app.schemas.response import FinalSearchResult
from app.schemas.verification import VerifiedItinerary
from app.sources.aggregator_one import AggregatorOneSource
from app.sources.aggregator_two import AggregatorTwoSource

try:
    from agents import Runner, set_tracing_disabled
except Exception:  # pragma: no cover
    Runner = None  # type: ignore[assignment]
    set_tracing_disabled = None  # type: ignore[assignment]


logger = get_logger(__name__)


class FlightSearchOrchestrator:
    def __init__(self) -> None:
        self.guard = SchemaGuard()
        self.source_one = AggregatorOneSource()
        self.source_two = AggregatorTwoSource()
        self.agent_bundle: AgentBundle = build_agent_bundle(settings.openai_model)
        if set_tracing_disabled is not None:
            set_tracing_disabled(False)

    async def run_search(self, request: SearchRequest) -> FinalSearchResult:
        run_id = uuid.uuid4().hex
        run_started = datetime.now(timezone.utc)
        request_hash = model_hash(request)

        artifact_store = ArtifactStore(run_id)
        artifact_store.write_json("inputs.json", request.model_dump(mode="json"))
        create_run(run_id=run_id, request_hash=request_hash, request_json=request.model_dump_json(), status="started")

        warnings: list[str] = []
        cache_hit = False
        cache_expires = None

        try:
            planner_output = await self.guard.run(lambda: self._planner_step(request), PlannerJudgeOutput)
            artifact_store.append_log("planner_output", planner_output.model_dump(mode="json"))

            raw_candidates: list[RawItineraryCandidate] = []
            if not request.dry_run and not settings.enable_live_sources:
                warnings.append("Live sources are disabled on this deployment; returning fixture-projected results.")

            cached_run = get_latest_run_by_hash(
                request_hash=request_hash,
                ttl_minutes=settings.cache_ttl_minutes,
                exclude_run_id=run_id,
            )
            if cached_run and cached_run.run_id != run_id:
                cached_candidates = get_candidates_for_run(cached_run.run_id)
                if cached_candidates:
                    cache_hit = True
                    cache_expires = expires_at(cached_run.timestamp, settings.cache_ttl_minutes)
                    raw_candidates = [RawItineraryCandidate.model_validate(row) for row in cached_candidates]
                    artifact_store.append_log("cache_hit", {"source_run_id": cached_run.run_id, "candidate_count": len(raw_candidates)})

            if not raw_candidates:
                scout_results = await self._scout_parallel(request, planner_output.source_dispatch)
                for source_name, output in scout_results:
                    if output is None:
                        warnings.append(f"Scout branch failed: {source_name}")
                        continue
                    save_candidates(
                        run_id=run_id,
                        source=source_name,
                        candidates=[candidate.model_dump(mode="json") for candidate in output.candidates],
                    )
                    raw_candidates.extend(output.candidates)

            if not raw_candidates:
                warnings.append("No candidates found from enabled sources.")

            artifact_store.write_json("candidates.json", [candidate.model_dump(mode="json") for candidate in raw_candidates])

            normalized_output = await self.guard.run(
                lambda: self._dedupe_step(raw_candidates, request),
                NormalizedCandidateSet,
            )
            constrained_output = await self.guard.run(
                lambda: self._constraints_step(normalized_output.itineraries, request),
                ConstraintsOutput,
            )
            ranked_output = await self.guard.run(
                lambda: self._ranker_step(constrained_output.itineraries, request),
                StrategicRankOutput,
            )

            provisional = ranked_output.itineraries
            verify_n = max(3, request.max_verify_per_tab, settings.verify_top_n_per_tab)
            verify_queue = self._build_verify_queue(provisional, verify_n)

            verification_output = await self.guard.run(
                lambda: self._verify_step(verify_queue, request, artifact_store),
                VerificationBatch,
            )

            verified_map: dict[str, VerifiedItinerary] = {}
            for row in verification_output.verified:
                verified_map[row.itinerary_id] = row
                save_verified(
                    run_id=run_id,
                    verified_json=row.model_dump(mode="json"),
                    evidence_json=row.evidence.model_dump(mode="json") if row.evidence else {},
                )

            verify_ids = {item.itinerary_id for item in verify_queue}
            updated: list[NormalizedItinerary] = []
            for itinerary in provisional:
                verified = verified_map.get(itinerary.itinerary_id)
                candidate = apply_verification_to_normalized(itinerary, verified)
                if candidate.verified_total_price_usd is not None:
                    candidate = candidate.model_copy(update={"true_total_price_usd": candidate.verified_total_price_usd})
                if verified and verified.status == "failed":
                    failed_gotchas = candidate.gotchas + ["Verification failed for this itinerary in current run."]
                    candidate = candidate.model_copy(
                        update={
                            "gotchas": failed_gotchas,
                            "verification_status": "failed",
                            "true_total_price_usd": candidate.true_total_price_usd + 1000.0,
                        }
                    )
                elif verified and verified.material_price_change:
                    candidate = candidate.model_copy(
                        update={"gotchas": candidate.gotchas + ["Verified price changed materially from initial quote."]}
                    )
                elif itinerary.itinerary_id in verify_ids and not verified:
                    candidate = candidate.model_copy(
                        update={
                            "gotchas": candidate.gotchas + ["Verification branch missing; itinerary demoted."],
                            "true_total_price_usd": candidate.true_total_price_usd + 500.0,
                        }
                    )
                updated.append(candidate)

            reranked = await self.guard.run(
                lambda: self._ranker_step(updated, request),
                StrategicRankOutput,
            )

            stopover_output = await self.guard.run(
                lambda: self._stopover_step(reranked.itineraries, request),
                StopoverBatch,
            )
            stopover_map = {plan.itinerary_id: plan for plan in stopover_output.plans}

            final_output = await self.guard.run(
                lambda: self._final_step(
                    run_id=run_id,
                    generated_at=run_started,
                    request=request,
                    itineraries=reranked.itineraries,
                    stopover_map=stopover_map,
                    cache_hit=cache_hit,
                    cache_expires=cache_expires,
                    warnings=warnings,
                ),
                FinalPresenterOutput,
            )

            final_result = final_output.result
            artifact_store.write_json("verified.json", [item.model_dump(mode="json") for item in verification_output.verified])
            artifact_store.write_json("final.json", final_result.model_dump(mode="json"))
            save_final_result(run_id=run_id, final_json=final_result.model_dump(mode="json"))
            update_run_status(run_id, "completed")
            return final_result

        except Exception as exc:  # noqa: BLE001
            update_run_status(run_id, "failed")
            artifact_store.append_log("run_failed", {"error": str(exc)})
            logger.exception("search run failed", extra={"extra_payload": {"run_id": run_id}})

            fallback = self._cached_fallback(request_hash)
            if fallback:
                return fallback
            raise

    def _cached_fallback(self, request_hash: str) -> FinalSearchResult | None:
        run = get_latest_run_any_age(request_hash)
        if not run:
            return None
        final = get_final_result(run.run_id)
        if not final:
            return None
        return FinalSearchResult.model_validate(final)

    async def _planner_step(self, request: SearchRequest) -> dict[str, Any]:
        if self._use_live_agents(request) and self.agent_bundle.planner_judge is not None:
            return await self._run_live_agent(
                agent=self.agent_bundle.planner_judge,
                payload={"request": request.model_dump(mode="json"), "handoff_graph": "planner->scouts->deduper"},
            )
        return local_plan(request).model_dump(mode="json")

    async def _scout_parallel(
        self,
        request: SearchRequest,
        source_dispatch: list[str],
    ) -> list[tuple[str, ScoutOneOutput | ScoutTwoOutput | None]]:
        tasks: list[asyncio.Task] = []

        async def run_source(name: str) -> tuple[str, ScoutOneOutput | ScoutTwoOutput | None]:
            try:
                if name == "aggregator_one":
                    async def produce() -> dict[str, Any]:
                        result = await with_retries(
                            task_factory=lambda: self.source_one.search(request),
                            retries=self.source_one.config.max_retries,
                            backoff_ms=self.source_one.config.backoff_ms,
                        )
                        return ScoutOneOutput(source=name, candidates=result).model_dump(mode="json")

                    validated = await self.guard.run(produce, ScoutOneOutput)
                    return name, validated
                if name == "aggregator_two":
                    async def produce() -> dict[str, Any]:
                        result = await with_retries(
                            task_factory=lambda: self.source_two.search(request),
                            retries=self.source_two.config.max_retries,
                            backoff_ms=self.source_two.config.backoff_ms,
                        )
                        return ScoutTwoOutput(source=name, candidates=result).model_dump(mode="json")

                    validated = await self.guard.run(produce, ScoutTwoOutput)
                    return name, validated
                return name, None
            except BranchHardFailError:
                return name, None
            except Exception:
                return name, None

        for source_name in source_dispatch:
            tasks.append(asyncio.create_task(run_source(source_name)))

        if not tasks:
            return []
        return await asyncio.gather(*tasks)

    async def _dedupe_step(self, candidates: list[RawItineraryCandidate], request: SearchRequest) -> dict[str, Any]:
        if self._use_live_agents(request) and self.agent_bundle.deduper_normalizer is not None:
            return await self._run_live_agent(
                agent=self.agent_bundle.deduper_normalizer,
                payload={"request": request.model_dump(mode="json"), "candidates": [c.model_dump(mode="json") for c in candidates]},
            )
        return normalize_and_dedupe(candidates, request).model_dump(mode="json")

    async def _constraints_step(self, itineraries: list[NormalizedItinerary], request: SearchRequest) -> dict[str, Any]:
        if self._use_live_agents(request) and self.agent_bundle.constraints_lawyer is not None:
            return await self._run_live_agent(
                agent=self.agent_bundle.constraints_lawyer,
                payload={"request": request.model_dump(mode="json"), "itineraries": [i.model_dump(mode="json") for i in itineraries]},
            )
        return apply_constraints(itineraries, request).model_dump(mode="json")

    async def _ranker_step(self, itineraries: list[NormalizedItinerary], request: SearchRequest) -> dict[str, Any]:
        if self._use_live_agents(request) and self.agent_bundle.strategic_ranker is not None:
            return await self._run_live_agent(
                agent=self.agent_bundle.strategic_ranker,
                payload={"request": request.model_dump(mode="json"), "itineraries": [i.model_dump(mode="json") for i in itineraries]},
            )
        return rank_itineraries(itineraries, request).model_dump(mode="json")

    async def _verify_step(
        self,
        itineraries: list[NormalizedItinerary],
        request: SearchRequest,
        artifact_store: ArtifactStore,
    ) -> dict[str, Any]:
        if self._use_live_agents(request) and self.agent_bundle.verifier is not None:
            return await self._run_live_agent(
                agent=self.agent_bundle.verifier,
                payload={"request": request.model_dump(mode="json"), "itineraries": [i.model_dump(mode="json") for i in itineraries]},
            )
        return (await verify_itineraries(itineraries, request, artifact_store)).model_dump(mode="json")

    async def _stopover_step(self, itineraries: list[NormalizedItinerary], request: SearchRequest) -> dict[str, Any]:
        if self._use_live_agents(request) and self.agent_bundle.stopover_itinerary is not None:
            return await self._run_live_agent(
                agent=self.agent_bundle.stopover_itinerary,
                payload={"request": request.model_dump(mode="json"), "itineraries": [i.model_dump(mode="json") for i in itineraries]},
            )
        return generate_stopover_plans(itineraries, request).model_dump(mode="json")

    async def _final_step(
        self,
        run_id: str,
        generated_at: datetime,
        request: SearchRequest,
        itineraries: list[NormalizedItinerary],
        stopover_map: dict[str, Any],
        cache_hit: bool,
        cache_expires: datetime | None,
        warnings: list[str],
    ) -> dict[str, Any]:
        if self._use_live_agents(None) and self.agent_bundle.final_presenter is not None:
            return await self._run_live_agent(
                agent=self.agent_bundle.final_presenter,
                payload={
                    "run_id": run_id,
                    "generated_at": generated_at.isoformat(),
                    "cache_hit": cache_hit,
                    "cache_expires_at": cache_expires.isoformat() if cache_expires else None,
                    "warnings": warnings,
                    "itineraries": [i.model_dump(mode="json") for i in itineraries],
                    "stopover_plans": {k: v.model_dump(mode="json") for k, v in stopover_map.items()},
                },
            )
        return present_final(
            run_id=run_id,
            generated_at=generated_at,
            itineraries=itineraries,
            stopover_plans=stopover_map,
            cache_hit=cache_hit,
            cache_expires_at=cache_expires,
            warnings=warnings,
            metadata_extra=self._result_metadata(request),
        ).model_dump(mode="json")

    def _use_live_agents(self, request: SearchRequest | None) -> bool:
        if Runner is None:
            return False
        if not settings.openai_api_key:
            return False
        if request and request.dry_run:
            return False
        return True

    async def _run_live_agent(self, agent: Any, payload: dict[str, Any]) -> dict[str, Any]:
        if Runner is None:
            raise RuntimeError("agents SDK runner unavailable")

        result = await Runner.run(agent, input=json.dumps(payload))
        output = getattr(result, "final_output", result)
        if hasattr(output, "model_dump"):
            return output.model_dump(mode="json")
        if isinstance(output, str):
            return json.loads(output)
        if isinstance(output, dict):
            return output
        raise RuntimeError("Unexpected agent output type")

    def _build_verify_queue(self, itineraries: list[NormalizedItinerary], verify_n: int) -> list[NormalizedItinerary]:
        cheapest = sorted(itineraries, key=lambda i: (not i.verified, i.true_total_price_usd, i.total_travel_time_minutes))[:verify_n]
        nonstop = sorted(
            [i for i in itineraries if i.stops_count == 0],
            key=lambda i: (not i.verified, i.true_total_price_usd, i.total_travel_time_minutes),
        )[:verify_n]
        strategic = sorted(itineraries, key=lambda i: i.score.total_score if i.score else 0.0, reverse=True)[:verify_n]

        queue: dict[str, NormalizedItinerary] = {}
        for itinerary in cheapest + nonstop + strategic:
            queue[itinerary.itinerary_id] = itinerary
        return list(queue.values())

    def _result_metadata(self, request: SearchRequest) -> dict[str, str | int | float | bool | None]:
        data_mode = "live" if (settings.enable_live_sources and not request.dry_run) else "fixtures"
        return {
            "data_mode": data_mode,
            "request_dry_run": request.dry_run,
            "live_sources_enabled": settings.enable_live_sources,
        }


orchestrator = FlightSearchOrchestrator()
