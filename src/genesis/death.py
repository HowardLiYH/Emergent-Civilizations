"""
Death and extinction mechanics for civilization agents.

Agents with zero or negative wealth are removed from the population.
"""

from typing import List, Tuple, Dict
from datetime import datetime
import json
from pathlib import Path

from .civilization_agent import CivilizationAgent


@dataclass
class ExtinctionRecord:
    """Record of an agent's extinction."""
    agent_id: str
    dynasty_id: str
    generation: int
    age_at_death: int
    final_wealth: float
    cause: str  # "bankruptcy", "natural", etc.
    specialization: str
    timestamp: datetime = field(default_factory=datetime.now)


# Keep track of all extinctions
_extinction_log: List[ExtinctionRecord] = []


def process_deaths(
    agents: List[CivilizationAgent],
    generation: int
) -> Tuple[List[CivilizationAgent], List[CivilizationAgent]]:
    """
    Remove agents with zero or negative wealth.

    Args:
        agents: Current population
        generation: Current generation number

    Returns:
        (survivors, deceased)
    """
    survivors = []
    deceased = []

    for agent in agents:
        if agent.is_alive():
            survivors.append(agent)
        else:
            deceased.append(agent)
            log_extinction(agent, generation, "bankruptcy")

    return survivors, deceased


def log_extinction(
    agent: CivilizationAgent,
    generation: int,
    cause: str = "bankruptcy"
) -> ExtinctionRecord:
    """Log an agent's extinction."""
    record = ExtinctionRecord(
        agent_id=agent.id,
        dynasty_id=agent.dynasty_id or "unknown",
        generation=generation,
        age_at_death=agent.age,
        final_wealth=agent.wealth,
        cause=cause,
        specialization=agent.get_best_task_type() or "generalist"
    )

    _extinction_log.append(record)
    return record


def get_extinction_log() -> List[ExtinctionRecord]:
    """Get all extinction records."""
    return _extinction_log.copy()


def clear_extinction_log():
    """Clear the extinction log (for new simulations)."""
    global _extinction_log
    _extinction_log = []


def get_extinction_statistics(records: List[ExtinctionRecord] = None) -> Dict:
    """Get statistics about extinctions."""
    if records is None:
        records = _extinction_log

    if not records:
        return {"total": 0}

    ages = [r.age_at_death for r in records]
    generations = [r.generation for r in records]

    # Count by specialization
    spec_counts = {}
    for r in records:
        spec_counts[r.specialization] = spec_counts.get(r.specialization, 0) + 1

    # Count by dynasty
    dynasty_counts = {}
    for r in records:
        dynasty_counts[r.dynasty_id] = dynasty_counts.get(r.dynasty_id, 0) + 1

    return {
        "total": len(records),
        "mean_age_at_death": sum(ages) / len(ages),
        "max_age_at_death": max(ages),
        "extinction_by_specialization": spec_counts,
        "extinction_by_dynasty": dynasty_counts,
        "generations_with_extinctions": len(set(generations))
    }


def save_extinction_log(path: str):
    """Save extinction log to file."""
    data = [
        {
            "agent_id": r.agent_id,
            "dynasty_id": r.dynasty_id,
            "generation": r.generation,
            "age_at_death": r.age_at_death,
            "final_wealth": r.final_wealth,
            "cause": r.cause,
            "specialization": r.specialization
        }
        for r in _extinction_log
    ]

    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


# Need to import dataclass
from dataclasses import dataclass, field
