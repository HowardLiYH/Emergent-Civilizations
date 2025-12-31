"""
CivilizationAgent: Extended agent with economic and social dynamics.

Adds to GenesisAgent:
- Wealth accumulation
- Age tracking
- Parent/child relationships for dynasty tracking
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np
import uuid

from .agent import GenesisAgent, PromptEvolutionEvent


# Economic constants
STARTING_WEALTH = 100.0
REPRODUCTION_COST = 200.0
CHILD_STARTING_WEALTH = 50.0
PARTICIPATION_COST = 1.0  # Cost per competition round


@dataclass
class CivilizationAgent(GenesisAgent):
    """
    An LLM agent with economic and social dynamics.

    Extends GenesisAgent with:
        wealth: Accumulated from winning competitions
        age: Number of generations survived
        parent_id: ID of parent agent (None for founders)
        children_ids: IDs of offspring
    """
    wealth: float = STARTING_WEALTH
    age: int = 0
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)

    # Dynasty tracking
    dynasty_id: Optional[str] = None  # ID of founding ancestor

    @classmethod
    def create(cls, initial_prompt: str = None,
               wealth: float = STARTING_WEALTH) -> 'CivilizationAgent':
        """Create a new founder agent."""
        agent_id = str(uuid.uuid4())[:8]

        if initial_prompt is None:
            initial_prompt = (
                "I am a general-purpose AI assistant. "
                "I can help with various tasks including math, coding, logic, and language."
            )

        agent = cls(
            id=agent_id,
            system_prompt=initial_prompt,
            wealth=wealth,
            dynasty_id=agent_id  # Founders are their own dynasty
        )
        return agent

    @classmethod
    def create_offspring(cls, parent: 'CivilizationAgent',
                         child_prompt: str) -> 'CivilizationAgent':
        """Create an offspring from a parent."""
        child_id = str(uuid.uuid4())[:8]

        child = cls(
            id=child_id,
            system_prompt=child_prompt,
            wealth=CHILD_STARTING_WEALTH,
            parent_id=parent.id,
            dynasty_id=parent.dynasty_id,  # Inherit dynasty
            generation=parent.generation + 1
        )

        # Update parent's children list
        parent.children_ids.append(child_id)

        return child

    def can_reproduce(self) -> bool:
        """Check if agent has enough wealth to reproduce."""
        return self.wealth >= REPRODUCTION_COST

    def is_alive(self) -> bool:
        """Check if agent is still alive (has positive wealth)."""
        return self.wealth > 0

    def pay_participation_cost(self) -> None:
        """Deduct participation cost for a round."""
        self.wealth -= PARTICIPATION_COST

    def receive_reward(self, amount: float) -> None:
        """Receive wealth reward for winning."""
        self.wealth += amount

    def pay_reproduction_cost(self) -> None:
        """Pay cost to reproduce."""
        self.wealth -= REPRODUCTION_COST

    def age_one_generation(self) -> None:
        """Increment age by one generation."""
        self.age += 1

    def get_lineage_depth(self, agents_by_id: Dict[str, 'CivilizationAgent']) -> int:
        """Get depth of lineage (generations from founder)."""
        depth = 0
        current = self

        while current.parent_id and current.parent_id in agents_by_id:
            depth += 1
            current = agents_by_id[current.parent_id]

        return depth

    def __repr__(self) -> str:
        return (
            f"CivilizationAgent(id={self.id}, wealth={self.wealth:.1f}, "
            f"age={self.age}, children={len(self.children_ids)})"
        )


def create_civilization_population(
    n_agents: int,
    initial_prompt: str = None,
    initial_wealth: float = STARTING_WEALTH
) -> List[CivilizationAgent]:
    """Create a population of founder agents."""
    return [
        CivilizationAgent.create(initial_prompt, initial_wealth)
        for _ in range(n_agents)
    ]


def get_wealth_statistics(agents: List[CivilizationAgent]) -> Dict[str, float]:
    """Get wealth statistics for a population."""
    wealths = [a.wealth for a in agents]

    return {
        "total": sum(wealths),
        "mean": np.mean(wealths),
        "std": np.std(wealths),
        "min": min(wealths),
        "max": max(wealths),
        "median": np.median(wealths)
    }


def get_age_statistics(agents: List[CivilizationAgent]) -> Dict[str, float]:
    """Get age statistics for a population."""
    ages = [a.age for a in agents]

    return {
        "mean": np.mean(ages),
        "std": np.std(ages),
        "min": min(ages),
        "max": max(ages),
        "oldest_id": max(agents, key=lambda a: a.age).id
    }
