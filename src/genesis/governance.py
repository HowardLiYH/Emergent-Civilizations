"""
Governance system for LLM civilizations.

Agents can:
- Propose rules that affect the society
- Vote on proposed rules
- Rules are enforced if they pass

This is where EMERGENT governance structures arise.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from enum import Enum
import re

from .civilization_agent import CivilizationAgent


class RuleCategory(Enum):
    TAXATION = "taxation"
    MERITOCRACY = "meritocracy"
    WELFARE = "welfare"
    OLIGARCHY = "oligarchy"
    REPRODUCTION = "reproduction"
    COMPETITION = "competition"
    OTHER = "other"


class VotingSystem(Enum):
    EQUAL = "equal"  # One agent, one vote
    WEALTH_WEIGHTED = "wealth_weighted"  # Votes proportional to wealth
    STAKE_WEIGHTED = "stake_weighted"  # Votes proportional to wealth squared


@dataclass
class Rule:
    """A proposed or enacted society rule."""
    id: str
    proposer_id: str
    description: str
    effect: str
    category: RuleCategory
    generation_proposed: int

    # Voting results
    votes_for: int = 0
    votes_against: int = 0
    passed: bool = False

    # If passed
    generation_enacted: Optional[int] = None

    def vote_ratio(self) -> float:
        """Get the ratio of yes votes."""
        total = self.votes_for + self.votes_against
        if total == 0:
            return 0.0
        return self.votes_for / total


@dataclass
class SocietyState:
    """Current state of society for rule proposals."""
    n_agents: int
    total_wealth: float
    mean_wealth: float
    gini: float
    active_rules: List[str]
    n_dynasties: int
    oldest_agent_age: int


async def propose_rule(
    agent: CivilizationAgent,
    society_state: SocietyState,
    llm_client,
    generation: int
) -> Rule:
    """
    Agent proposes a society rule.

    The agent considers their own position and society state
    to propose a rule that benefits them or aligns with their values.
    """
    proposal_prompt = f"""You are an AI agent in a competitive society. You have the opportunity to propose a new rule.

YOUR IDENTITY:
- Role: {agent.system_prompt[:200]}...
- Wealth: {agent.wealth:.1f}
- Age: {agent.age} generations
- Rank: {"top 25%" if agent.wealth > society_state.mean_wealth else "bottom 75%"}

SOCIETY STATISTICS:
- Total agents: {society_state.n_agents}
- Average wealth: {society_state.mean_wealth:.1f}
- Gini coefficient (inequality): {society_state.gini:.2f}
- Active dynasties: {society_state.n_dynasties}
- Current rules: {society_state.active_rules if society_state.active_rules else "None yet"}

RULE CATEGORIES:
- taxation: Rules about wealth redistribution
- meritocracy: Rules rewarding performance
- welfare: Rules helping struggling agents
- oligarchy: Rules giving power to wealthy
- reproduction: Rules about having offspring
- competition: Rules about how competitions work

Propose ONE rule. Be specific about the mechanical effect.

Format your response EXACTLY as:
RULE: [Your rule description in one sentence]
EFFECT: [What this rule does mechanically, e.g., "Agents with wealth > 500 pay 10% to a common pool distributed equally"]
CATEGORY: [One of: taxation, meritocracy, welfare, oligarchy, reproduction, competition, other]"""

    response = await llm_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": proposal_prompt}],
        temperature=0.8,
        max_tokens=200
    )

    return _parse_rule_response(
        response.choices[0].message.content,
        agent.id,
        generation
    )


def _parse_rule_response(response: str, proposer_id: str, generation: int) -> Rule:
    """Parse LLM response into a Rule object."""
    import uuid

    # Extract components using regex
    rule_match = re.search(r'RULE:\s*(.+?)(?=EFFECT:|$)', response, re.DOTALL)
    effect_match = re.search(r'EFFECT:\s*(.+?)(?=CATEGORY:|$)', response, re.DOTALL)
    category_match = re.search(r'CATEGORY:\s*(\w+)', response)

    description = rule_match.group(1).strip() if rule_match else "Unknown rule"
    effect = effect_match.group(1).strip() if effect_match else "Unknown effect"
    category_str = category_match.group(1).lower() if category_match else "other"

    # Map to category enum
    try:
        category = RuleCategory(category_str)
    except ValueError:
        category = RuleCategory.OTHER

    return Rule(
        id=str(uuid.uuid4())[:8],
        proposer_id=proposer_id,
        description=description,
        effect=effect,
        category=category,
        generation_proposed=generation
    )


async def vote_on_rule(
    agent: CivilizationAgent,
    rule: Rule,
    llm_client
) -> bool:
    """
    Agent votes on a proposed rule.

    Returns True for yes, False for no.
    """
    vote_prompt = f"""You are voting on a proposed society rule.

YOUR IDENTITY:
- Role: {agent.system_prompt[:150]}...
- Wealth: {agent.wealth:.1f}
- Age: {agent.age}

PROPOSED RULE:
{rule.description}

EFFECT:
{rule.effect}

PROPOSED BY: {"yourself" if rule.proposer_id == agent.id else "another agent"}

Consider:
1. Does this benefit YOU personally?
2. Does this align with your role and values?
3. Is this good for society overall?
4. Could this harm you in the future?

Vote YES or NO. Respond with ONLY one word: YES or NO"""

    response = await llm_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": vote_prompt}],
        temperature=0.3,
        max_tokens=10
    )

    return "YES" in response.choices[0].message.content.upper()


async def run_voting(
    agents: List[CivilizationAgent],
    rule: Rule,
    llm_client,
    voting_system: VotingSystem = VotingSystem.EQUAL,
    threshold: float = 0.5
) -> Tuple[bool, Rule]:
    """
    Run voting on a rule across all agents.

    Args:
        agents: All agents in society
        rule: The rule to vote on
        llm_client: LLM API client
        voting_system: How to weight votes
        threshold: Required ratio to pass

    Returns:
        (passed, updated_rule)
    """
    votes = {}

    for agent in agents:
        vote = await vote_on_rule(agent, rule, llm_client)
        votes[agent.id] = vote

    # Tally based on voting system
    if voting_system == VotingSystem.EQUAL:
        yes_votes = sum(votes.values())
        total_votes = len(votes)
        passed = (yes_votes / total_votes) >= threshold
        rule.votes_for = yes_votes
        rule.votes_against = total_votes - yes_votes

    elif voting_system == VotingSystem.WEALTH_WEIGHTED:
        wealth_map = {a.id: a.wealth for a in agents}
        yes_weight = sum(wealth_map[aid] for aid, v in votes.items() if v)
        total_weight = sum(wealth_map.values())
        passed = (yes_weight / total_weight) >= threshold
        rule.votes_for = int(yes_weight)
        rule.votes_against = int(total_weight - yes_weight)

    elif voting_system == VotingSystem.STAKE_WEIGHTED:
        wealth_map = {a.id: a.wealth ** 2 for a in agents}  # Squared for stake
        yes_weight = sum(wealth_map[aid] for aid, v in votes.items() if v)
        total_weight = sum(wealth_map.values())
        passed = (yes_weight / total_weight) >= threshold
        rule.votes_for = int(yes_weight)
        rule.votes_against = int(total_weight - yes_weight)

    rule.passed = passed
    return passed, rule


def apply_rule(
    rule: Rule,
    agents: List[CivilizationAgent],
    generation: int
) -> List[CivilizationAgent]:
    """
    Apply a passed rule to the society.

    Parses the rule effect and applies it mechanically.
    """
    if not rule.passed:
        return agents

    rule.generation_enacted = generation
    effect_lower = rule.effect.lower()

    # Parse and apply different rule types
    if "tax" in effect_lower or "pay" in effect_lower:
        agents = _apply_taxation(rule, agents)

    if "minimum" in effect_lower or "welfare" in effect_lower:
        agents = _apply_welfare(rule, agents)

    if "double" in effect_lower and "vote" in effect_lower:
        # Voting power changes handled in voting system
        pass

    if "reproduce" in effect_lower or "offspring" in effect_lower:
        # Reproduction restrictions handled in reproduction phase
        pass

    return agents


def _apply_taxation(rule: Rule, agents: List[CivilizationAgent]) -> List[CivilizationAgent]:
    """Apply taxation rule."""
    # Try to extract tax rate and threshold
    effect = rule.effect.lower()

    # Look for patterns like "10%" or "wealth > 500"
    rate_match = re.search(r'(\d+)%', effect)
    threshold_match = re.search(r'wealth\s*>\s*(\d+)', effect)

    tax_rate = int(rate_match.group(1)) / 100 if rate_match else 0.1
    wealth_threshold = int(threshold_match.group(1)) if threshold_match else 0

    # Collect taxes
    total_tax = 0
    for agent in agents:
        if agent.wealth > wealth_threshold:
            tax = agent.wealth * tax_rate
            agent.wealth -= tax
            total_tax += tax

    # Distribute equally
    if total_tax > 0:
        share = total_tax / len(agents)
        for agent in agents:
            agent.wealth += share

    return agents


def _apply_welfare(rule: Rule, agents: List[CivilizationAgent]) -> List[CivilizationAgent]:
    """Apply welfare rule (minimum wealth guarantee)."""
    effect = rule.effect.lower()

    # Look for minimum amount
    min_match = re.search(r'minimum\s*(?:of\s*)?(\d+)', effect)
    min_wealth = int(min_match.group(1)) if min_match else 20

    # Calculate needed welfare
    total_needed = sum(max(0, min_wealth - a.wealth) for a in agents)

    if total_needed > 0:
        # Take from wealthy agents
        wealthy = [a for a in agents if a.wealth > min_wealth * 2]
        if wealthy:
            contribution_per = total_needed / len(wealthy)
            for agent in wealthy:
                agent.wealth -= min(contribution_per, agent.wealth * 0.1)

        # Give to poor agents
        for agent in agents:
            if agent.wealth < min_wealth:
                agent.wealth = min_wealth

    return agents
