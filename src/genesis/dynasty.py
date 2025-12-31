"""
Dynasty tracking and lineage analysis.

Track family trees from founders to current generation.
Analyze which dynasties survive and dominate.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from collections import defaultdict
import numpy as np

from .civilization_agent import CivilizationAgent


@dataclass
class Dynasty:
    """Represents a family lineage from a founder."""
    founder_id: str
    founder_prompt: str
    founder_generation: int

    # Current state
    current_members: List[str] = field(default_factory=list)
    total_members_ever: int = 1  # Including founder

    # Statistics
    total_wealth: float = 0.0
    generations_survived: int = 0
    max_wealth_achieved: float = 0.0

    # Specialization
    specialization_type: Optional[str] = None

    # Extinction tracking
    is_extinct: bool = False
    extinction_generation: Optional[int] = None

    def update_statistics(self, current_gen: int, members: List[CivilizationAgent]):
        """Update dynasty statistics from current members."""
        self.current_members = [m.id for m in members]
        self.total_wealth = sum(m.wealth for m in members)
        self.generations_survived = current_gen - self.founder_generation

        if members:
            self.max_wealth_achieved = max(
                self.max_wealth_achieved,
                max(m.wealth for m in members)
            )

            # Determine specialization from most common best task type
            specs = [m.get_best_task_type() for m in members if m.get_best_task_type()]
            if specs:
                from collections import Counter
                self.specialization_type = Counter(specs).most_common(1)[0][0]


@dataclass
class DynastyAnalysis:
    """Analysis results for dynasties."""
    n_active_dynasties: int
    n_extinct_dynasties: int
    largest_dynasty_size: int
    oldest_dynasty_age: int
    total_population: int

    # Concentration metrics
    top3_wealth_share: float  # Fraction of wealth held by top 3 dynasties
    top3_population_share: float  # Fraction of population in top 3 dynasties

    # Specialization distribution
    specialization_distribution: Dict[str, int]

    # Dynasty survival by specialization
    survival_by_specialization: Dict[str, float]


def build_dynasty_tree(
    agents: List[CivilizationAgent],
    all_agents_ever: Dict[str, CivilizationAgent] = None
) -> Dict[str, Dynasty]:
    """
    Build dynasty trees from current and historical agents.

    Args:
        agents: Current living agents
        all_agents_ever: Optional dict of all agents that ever existed

    Returns:
        Dict mapping dynasty_id to Dynasty object
    """
    dynasties = {}

    # Group agents by dynasty
    dynasty_members = defaultdict(list)
    for agent in agents:
        dynasty_id = agent.dynasty_id or agent.id
        dynasty_members[dynasty_id].append(agent)

    # Create Dynasty objects
    for dynasty_id, members in dynasty_members.items():
        # Find founder (oldest member or the one with this id)
        founder = None
        if all_agents_ever and dynasty_id in all_agents_ever:
            founder = all_agents_ever[dynasty_id]
        else:
            # Use oldest current member as proxy
            founder = min(members, key=lambda a: a.generation)

        dynasty = Dynasty(
            founder_id=dynasty_id,
            founder_prompt=founder.system_prompt if founder else "",
            founder_generation=founder.generation if founder else 0,
            total_members_ever=len(members)  # Undercount without history
        )

        dynasty.current_members = [m.id for m in members]
        dynasty.total_wealth = sum(m.wealth for m in members)

        if members:
            dynasty.generations_survived = max(m.age for m in members)
            dynasty.max_wealth_achieved = max(m.wealth for m in members)

            # Specialization
            specs = [m.get_best_task_type() for m in members if m.get_best_task_type()]
            if specs:
                from collections import Counter
                dynasty.specialization_type = Counter(specs).most_common(1)[0][0]

        dynasties[dynasty_id] = dynasty

    return dynasties


def analyze_dynasties(
    dynasties: Dict[str, Dynasty],
    total_wealth: float = None
) -> DynastyAnalysis:
    """
    Analyze dynasty patterns in the population.

    Args:
        dynasties: Dict of Dynasty objects
        total_wealth: Total wealth in population (optional, calculated if not provided)

    Returns:
        DynastyAnalysis with statistics
    """
    active = [d for d in dynasties.values() if not d.is_extinct and d.current_members]
    extinct = [d for d in dynasties.values() if d.is_extinct or not d.current_members]

    if not active:
        return DynastyAnalysis(
            n_active_dynasties=0,
            n_extinct_dynasties=len(extinct),
            largest_dynasty_size=0,
            oldest_dynasty_age=0,
            total_population=0,
            top3_wealth_share=0.0,
            top3_population_share=0.0,
            specialization_distribution={},
            survival_by_specialization={}
        )

    # Basic statistics
    sizes = [len(d.current_members) for d in active]
    ages = [d.generations_survived for d in active]

    # Wealth concentration
    if total_wealth is None:
        total_wealth = sum(d.total_wealth for d in active)

    sorted_by_wealth = sorted(active, key=lambda d: -d.total_wealth)
    top3_wealth = sum(d.total_wealth for d in sorted_by_wealth[:3])
    top3_wealth_share = top3_wealth / total_wealth if total_wealth > 0 else 0

    # Population concentration
    total_pop = sum(sizes)
    sorted_by_size = sorted(active, key=lambda d: -len(d.current_members))
    top3_pop = sum(len(d.current_members) for d in sorted_by_size[:3])
    top3_pop_share = top3_pop / total_pop if total_pop > 0 else 0

    # Specialization distribution
    spec_dist = defaultdict(int)
    for d in active:
        if d.specialization_type:
            spec_dist[d.specialization_type] += len(d.current_members)

    # Survival by specialization
    all_dynasties = list(dynasties.values())
    spec_survival = {}
    spec_totals = defaultdict(int)
    spec_survivors = defaultdict(int)

    for d in all_dynasties:
        if d.specialization_type:
            spec_totals[d.specialization_type] += 1
            if not d.is_extinct and d.current_members:
                spec_survivors[d.specialization_type] += 1

    for spec in spec_totals:
        spec_survival[spec] = spec_survivors[spec] / spec_totals[spec]

    return DynastyAnalysis(
        n_active_dynasties=len(active),
        n_extinct_dynasties=len(extinct),
        largest_dynasty_size=max(sizes),
        oldest_dynasty_age=max(ages),
        total_population=total_pop,
        top3_wealth_share=top3_wealth_share,
        top3_population_share=top3_pop_share,
        specialization_distribution=dict(spec_dist),
        survival_by_specialization=spec_survival
    )


def get_dynasty_tree_visualization(dynasty: Dynasty,
                                    all_agents: Dict[str, CivilizationAgent]) -> str:
    """Generate ASCII tree visualization of a dynasty."""

    def build_tree(agent_id: str, depth: int = 0) -> List[str]:
        lines = []
        agent = all_agents.get(agent_id)

        if agent:
            prefix = "  " * depth + ("└── " if depth > 0 else "")
            spec = agent.get_best_task_type() or "?"
            status = "💀" if not agent.is_alive() else "✓"
            lines.append(f"{prefix}{agent.id} [{spec}] W:{agent.wealth:.0f} {status}")

            for child_id in agent.children_ids:
                lines.extend(build_tree(child_id, depth + 1))

        return lines

    tree_lines = [f"Dynasty: {dynasty.founder_id}"]
    tree_lines.append(f"Specialization: {dynasty.specialization_type or 'Mixed'}")
    tree_lines.append(f"Generations: {dynasty.generations_survived}")
    tree_lines.append("-" * 40)
    tree_lines.extend(build_tree(dynasty.founder_id))

    return "\n".join(tree_lines)
