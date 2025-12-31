"""
Society-level metrics for civilization analysis.

Key metrics:
- Gini coefficient (wealth inequality)
- Governance entropy (rule diversity)
- Dynasty concentration
- Social mobility
"""

from typing import List, Dict, Any
from collections import Counter
import numpy as np

from .civilization_agent import CivilizationAgent
from .governance import Rule, RuleCategory


def compute_gini(agents: List[CivilizationAgent]) -> float:
    """
    Compute Gini coefficient for wealth inequality.

    Gini = 0: Perfect equality (everyone has same wealth)
    Gini = 1: Maximum inequality (one agent has all wealth)

    Args:
        agents: List of agents

    Returns:
        float: Gini coefficient between 0 and 1
    """
    if not agents:
        return 0.0

    wealths = sorted([a.wealth for a in agents])
    n = len(wealths)

    if n == 1:
        return 0.0

    # Gini formula using cumulative sums
    cumsum = np.cumsum(wealths)

    # Gini = (2 * sum(i * x_i)) / (n * sum(x_i)) - (n + 1) / n
    numerator = 2 * sum((i + 1) * x for i, x in enumerate(wealths))
    denominator = n * sum(wealths)

    if denominator == 0:
        return 0.0

    gini = numerator / denominator - (n + 1) / n

    return float(max(0, min(1, gini)))


def compute_governance_entropy(rules: List[Rule]) -> float:
    """
    Compute entropy of rule categories.

    Higher entropy = more diverse governance (rules across many categories)
    Lower entropy = concentrated governance (rules in few categories)

    Args:
        rules: List of passed rules

    Returns:
        float: Entropy value (normalized to 0-1)
    """
    passed_rules = [r for r in rules if r.passed]

    if not passed_rules:
        return 0.0

    # Count categories
    categories = [r.category.value for r in passed_rules]
    counts = Counter(categories)

    # Compute entropy
    total = sum(counts.values())
    probs = [c / total for c in counts.values()]

    entropy = -sum(p * np.log(p + 1e-10) for p in probs)

    # Normalize by max possible entropy
    max_entropy = np.log(len(RuleCategory))

    return float(entropy / max_entropy)


def compute_wealth_concentration(agents: List[CivilizationAgent],
                                  top_n: int = 3) -> float:
    """
    Compute fraction of wealth held by top N agents.

    Args:
        agents: List of agents
        top_n: Number of top agents to consider

    Returns:
        float: Fraction of total wealth held by top N
    """
    if not agents:
        return 0.0

    wealths = sorted([a.wealth for a in agents], reverse=True)
    total = sum(wealths)

    if total == 0:
        return 0.0

    top_wealth = sum(wealths[:top_n])

    return top_wealth / total


def compute_social_mobility(
    agents: List[CivilizationAgent],
    previous_wealths: Dict[str, float]
) -> Dict[str, float]:
    """
    Compute social mobility metrics.

    Measures how much agents' wealth rankings have changed.

    Args:
        agents: Current agents
        previous_wealths: Previous generation's wealth by agent_id

    Returns:
        Dict with mobility metrics
    """
    if not agents or not previous_wealths:
        return {"upward": 0, "downward": 0, "stable": 0}

    # Get agents that existed in both periods
    continuing = [a for a in agents if a.id in previous_wealths]

    if not continuing:
        return {"upward": 0, "downward": 0, "stable": 0}

    # Previous ranks
    prev_sorted = sorted(previous_wealths.items(), key=lambda x: -x[1])
    prev_ranks = {aid: i for i, (aid, _) in enumerate(prev_sorted)}

    # Current ranks
    curr_sorted = sorted(continuing, key=lambda a: -a.wealth)
    curr_ranks = {a.id: i for i, a in enumerate(curr_sorted)}

    # Count mobility
    upward = 0
    downward = 0
    stable = 0

    for agent in continuing:
        prev_rank = prev_ranks.get(agent.id, len(prev_ranks))
        curr_rank = curr_ranks.get(agent.id, len(curr_ranks))

        if curr_rank < prev_rank - 1:  # Improved by more than 1 position
            upward += 1
        elif curr_rank > prev_rank + 1:  # Worsened by more than 1 position
            downward += 1
        else:
            stable += 1

    total = len(continuing)

    return {
        "upward": upward / total,
        "downward": downward / total,
        "stable": stable / total,
        "total_continuing": total
    }


def compute_specialization_by_class(
    agents: List[CivilizationAgent],
    n_classes: int = 3
) -> Dict[str, Dict[str, float]]:
    """
    Analyze specialization patterns by wealth class.

    Divides population into wealth classes and examines
    specialization patterns in each class.

    Args:
        agents: List of agents
        n_classes: Number of wealth classes

    Returns:
        Dict mapping class to specialization distribution
    """
    if not agents:
        return {}

    # Sort by wealth and divide into classes
    sorted_agents = sorted(agents, key=lambda a: -a.wealth)
    class_size = len(sorted_agents) // n_classes

    result = {}
    class_names = ["upper", "middle", "lower"][:n_classes]

    for i, class_name in enumerate(class_names):
        start = i * class_size
        end = (i + 1) * class_size if i < n_classes - 1 else len(sorted_agents)
        class_agents = sorted_agents[start:end]

        # Count specializations
        specs = [a.get_best_task_type() or "generalist" for a in class_agents]
        counts = Counter(specs)
        total = len(specs)

        result[class_name] = {
            spec: count / total for spec, count in counts.items()
        }

    return result


def compute_all_society_metrics(
    agents: List[CivilizationAgent],
    rules: List[Rule] = None,
    previous_wealths: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Compute all society metrics.

    Returns comprehensive metrics dictionary.
    """
    gini = compute_gini(agents)

    metrics = {
        "population": len(agents),
        "total_wealth": sum(a.wealth for a in agents),
        "mean_wealth": np.mean([a.wealth for a in agents]) if agents else 0,
        "gini": gini,
        "wealth_concentration_top3": compute_wealth_concentration(agents, 3),
        "wealth_concentration_top10pct": compute_wealth_concentration(
            agents, max(1, len(agents) // 10)
        ),
        "specialization_by_class": compute_specialization_by_class(agents),
    }

    if rules:
        metrics["governance_entropy"] = compute_governance_entropy(rules)
        metrics["n_passed_rules"] = len([r for r in rules if r.passed])
        metrics["rules_by_category"] = dict(Counter(
            r.category.value for r in rules if r.passed
        ))

    if previous_wealths:
        metrics["social_mobility"] = compute_social_mobility(agents, previous_wealths)

    return metrics
