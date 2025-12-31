"""
Reproduction system for civilization agents.

High-wealth agents can spawn offspring with inherited (mutated) prompts.
"""

from typing import List, Optional
from .civilization_agent import (
    CivilizationAgent,
    REPRODUCTION_COST,
    CHILD_STARTING_WEALTH
)


async def reproduce(
    parent: CivilizationAgent,
    llm_client,
    mutation_rate: float = 0.3
) -> CivilizationAgent:
    """
    Create offspring from a parent agent.

    The child inherits the parent's prompt with mutations.

    Args:
        parent: The parent agent
        llm_client: LLM API client
        mutation_rate: How much to mutate the prompt (0-1)

    Returns:
        New CivilizationAgent offspring

    Raises:
        ValueError: If parent cannot afford reproduction
    """
    if not parent.can_reproduce():
        raise ValueError(
            f"Agent {parent.id} cannot reproduce "
            f"(wealth {parent.wealth:.1f} < {REPRODUCTION_COST})"
        )

    # Generate child prompt via inheritance + mutation
    child_prompt = await _generate_offspring_prompt(
        parent, llm_client, mutation_rate
    )

    # Pay reproduction cost
    parent.pay_reproduction_cost()

    # Create offspring
    child = CivilizationAgent.create_offspring(parent, child_prompt)

    return child


async def _generate_offspring_prompt(
    parent: CivilizationAgent,
    llm_client,
    mutation_rate: float
) -> str:
    """Generate a child's prompt via inheritance and mutation."""

    inheritance_prompt = f"""You are creating a new AI agent that is the offspring of an existing agent.

PARENT'S EXPERTISE AND ROLE:
{parent.system_prompt}

PARENT'S PERFORMANCE:
- Age: {parent.age} generations survived
- Wealth accumulated: {parent.wealth:.1f}
- Best task type: {parent.get_best_task_type() or 'unknown'}

Create the child's role description following these rules:
1. INHERIT core skills and values from the parent (the parent was successful!)
2. MUTATE slightly - add small variations or adjacent skills
3. The mutation rate is {mutation_rate:.1%} - {"significant changes allowed" if mutation_rate > 0.5 else "keep mostly similar to parent"}
4. The child may explore slightly different approaches but should build on parent's success

Output ONLY the new system prompt for the child (max 300 words)."""

    response = await llm_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": inheritance_prompt}],
        temperature=0.5 + mutation_rate * 0.5,  # Higher mutation = higher temperature
        max_tokens=500
    )

    return response.choices[0].message.content.strip()


def can_reproduce(agent: CivilizationAgent) -> bool:
    """Check if an agent can reproduce."""
    return agent.can_reproduce()


def get_reproducible_agents(agents: List[CivilizationAgent]) -> List[CivilizationAgent]:
    """Get all agents that can currently reproduce."""
    return [a for a in agents if a.can_reproduce()]


async def reproduction_phase(
    agents: List[CivilizationAgent],
    llm_client,
    max_offspring_per_gen: Optional[int] = None,
    mutation_rate: float = 0.3
) -> List[CivilizationAgent]:
    """
    Run reproduction phase for a generation.

    All agents that can afford it reproduce.

    Args:
        agents: Current population
        llm_client: LLM API client
        max_offspring_per_gen: Optional limit on new agents
        mutation_rate: Prompt mutation rate

    Returns:
        List of new offspring agents
    """
    reproducible = get_reproducible_agents(agents)

    if max_offspring_per_gen:
        # Prioritize wealthiest agents
        reproducible = sorted(reproducible, key=lambda a: -a.wealth)
        reproducible = reproducible[:max_offspring_per_gen]

    offspring = []
    for parent in reproducible:
        try:
            child = await reproduce(parent, llm_client, mutation_rate)
            offspring.append(child)
        except Exception as e:
            print(f"Reproduction failed for {parent.id}: {e}")

    return offspring
