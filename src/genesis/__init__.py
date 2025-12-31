"""
Genesis: LLM Agent Civilization Framework

Paper 3: Emergent Governance in Self-Organizing LLM Civilizations

This package extends Paper 2's prompt evolution with:
- Economic dynamics (wealth, reproduction, death)
- Dynasty tracking and lineage analysis
- Governance (rule proposals, voting, enforcement)
- Society metrics (Gini, governance entropy)
"""

# Import from base genesis (Paper 2 foundation)
from .agent import GenesisAgent
from .tasks import Task, TaskPool, TaskType
from .competition import CompetitionEngine, CompetitionResult
from .evolution import evolve_prompt_directed, evolve_prompt_random
from .metrics import compute_lsi, compute_semantic_specialization

# Paper 3 extensions
from .civilization_agent import CivilizationAgent
from .reproduction import reproduce, can_reproduce
from .death import process_deaths, log_extinction
from .dynasty import Dynasty, build_dynasty_tree, analyze_dynasties
from .governance import Rule, propose_rule, vote_on_rule, apply_rule
from .society_metrics import compute_gini, compute_governance_entropy
from .civilization import CivilizationSimulation

__all__ = [
    # Base (from Paper 2)
    'GenesisAgent',
    'Task',
    'TaskPool',
    'TaskType',
    'CompetitionEngine',
    'CompetitionResult',
    'evolve_prompt_directed',
    'evolve_prompt_random',
    'compute_lsi',
    'compute_semantic_specialization',

    # Paper 3 extensions
    'CivilizationAgent',
    'reproduce',
    'can_reproduce',
    'process_deaths',
    'log_extinction',
    'Dynasty',
    'build_dynasty_tree',
    'analyze_dynasties',
    'Rule',
    'propose_rule',
    'vote_on_rule',
    'apply_rule',
    'compute_gini',
    'compute_governance_entropy',
    'CivilizationSimulation',
]

__version__ = '0.1.0'
