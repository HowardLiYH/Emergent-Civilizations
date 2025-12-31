# Agent Context: Emergent Civilizations (Paper 3)

**This file provides context for AI agents working on this project.**

---

## Project Origin

This project is **Paper 3** of a three-paper research series on emergent specialization:

| Paper | Folder | Focus |
|-------|--------|-------|
| Paper 1 | `emergent_specialization/` | Rule-based agents with Thompson Sampling |
| Paper 2 | `emergent_prompt_evolution/` | LLM agents with evolvable prompts |
| **Paper 3** | `emergent_civilizations/` (THIS) | Society dynamics (reproduction, governance) |

---

## Core Research Claim

**"LLM agent societies, through reproduction, death, and self-governance mechanisms, develop emergent social structures including wealth inequality, dynasties, and political systems."**

---

## Prerequisite: Paper 2

This paper **BUILDS ON Paper 2**. Paper 2 establishes:
- GenesisAgent with evolvable prompts
- Competition engine with winner-take-all
- Prompt evolution mechanism
- Specialization metrics (LSI)

Paper 3 **EXTENDS** with:
- Economic dynamics (wealth, reproduction, death)
- Dynasty tracking
- Governance (rule proposals, voting)
- Society-level metrics

---

## Key Design Decisions (From v1.5 Conversation)

### 1. Population Scale
- Start with 100 agents
- Scale to **1000 agents** for full emergence
- Run **10 parallel civilizations** with different conditions

### 2. Society Dynamics
- **Reproduction**: High-wealth agents spawn offspring with inherited prompts
- **Death**: Zero-wealth agents are removed
- **Governance**: Agents propose and vote on society rules

### 3. Governance Emergence
We do NOT program specific rules. Agents create their own:
- Taxation rules
- Meritocracy rules
- Welfare rules
- Oligarchy rules

---

## Key Files

| File | Purpose |
|------|---------|
| `src/genesis/civilization_agent.py` | Extended agent with wealth, lineage |
| `src/genesis/reproduction.py` | Offspring creation with inheritance |
| `src/genesis/death.py` | Death/extinction mechanics |
| `src/genesis/dynasty.py` | Dynasty tracking and analysis |
| `src/genesis/governance.py` | Rule proposals, voting, enforcement |
| `src/genesis/society_metrics.py` | Gini, governance entropy, mobility |

### Base Files (From Paper 2)
| File | Purpose |
|------|---------|
| `src/genesis/agent.py` | Base GenesisAgent |
| `src/genesis/tasks.py` | Task system |
| `src/genesis/competition.py` | Competition engine |
| `src/genesis/evolution.py` | Prompt evolution |
| `src/genesis/metrics.py` | LSI metrics |

---

## Experiments to Run

| Exp | Description | Scale |
|-----|-------------|-------|
| 1 | Dynasty Formation | 50 agents, 200 gen |
| 2 | Inequality Emergence | 50 agents, 200 gen |
| 3 | Governance Emergence | 100 agents, 300 gen |
| 4 | Voting System Comparison | 3 × 100 agents |
| 5 | Parallel Civilizations | 10 × 100 agents |
| 6 | Scale to 1000 | 1000 agents, 500 gen |

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Top 3 dynasties control | > 50% of population |
| Gini coefficient | > 0.4 at convergence |
| Passed rule types | > 5 distinct categories |
| Voting system effect | Different structures emerge |
| Cross-civilization variance | Significant differences |

---

## Expected Emergent Phenomena

### Emergent Rule Types (Not Programmed!)
| Category | Example |
|----------|---------|
| Taxation | "Wealthy agents pay 10% to common pool" |
| Meritocracy | "Only top performers can reproduce" |
| Welfare | "Minimum wealth guarantee of 20" |
| Oligarchy | "High-wealth agents get double votes" |

### Emergent Social Structures
- **Dynasties**: Family lines persisting across generations
- **Social Classes**: Wealth stratification
- **Political Factions**: Voting coalitions

---

## Related Documents

- `docs/WILD_IDEAS_NEXT_LEVEL_RESEARCH.md` - Original brainstorm
- `.cursor/plans/paper3_civilizations.plan.md` - Detailed plan
- `../emergent_specialization/docs/conversation_v1.5.md` - Full conversation history
- `../emergent_prompt_evolution/` - Paper 2 foundation

---

## Cost Estimate

~$26,000 for all experiments (GPT-4 pricing)

---

## Timeline

13 weeks to paper submission (NeurIPS 2027 / Nature Machine Intelligence)

---

## Relationship to Paper 2

```
Paper 2 (Foundation)          Paper 3 (Extension)
─────────────────────         ─────────────────────
GenesisAgent            →     CivilizationAgent
Prompt Evolution        →     Prompt Inheritance
Competition             →     Competition + Economy
LSI Metrics             →     LSI + Gini + Governance
                              + Dynasties
                              + Governance
```

Paper 3 **cites Paper 2** for the foundational mechanisms.
