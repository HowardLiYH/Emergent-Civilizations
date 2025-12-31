# Experiments

This folder contains experiment scripts for Paper 3: Emergent Civilizations.

## Experiment Suite

| Script | Description |
|--------|-------------|
| `exp_dynasty.py` | Dynasty formation (50 agents, 200 gen) |
| `exp_inequality.py` | Wealth inequality emergence |
| `exp_governance.py` | Governance emergence (100 agents, 300 gen) |
| `exp_voting.py` | Voting system comparison |
| `exp_parallel.py` | 10 parallel civilizations |
| `exp_scale.py` | Scale to 1000 agents |

## Running Experiments

```bash
# Run dynasty experiment
python experiments/exp_dynasty.py --output results/dynasties/

# Run governance experiment
python experiments/exp_governance.py --output results/governance/

# Run parallel civilizations
python experiments/exp_parallel.py --output results/parallel/
```

## Configuration

See `.cursor/plans/paper3_civilizations.plan.md` for detailed experiment configurations.
