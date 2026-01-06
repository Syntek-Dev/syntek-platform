# Syntek Dev Suite - Self-Learning Metrics

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

This folder contains data for the self-learning system that improves agent performance over time.

## Table of Contents

- [Syntek Dev Suite - Self-Learning Metrics](#syntek-dev-suite---self-learning-metrics)
  - [Table of Contents](#table-of-contents)
  - [Folder Structure](#folder-structure)
  - [How It Works](#how-it-works)
  - [Configuration](#configuration)
  - [Commands](#commands)
  - [Privacy](#privacy)

## Folder Structure

```
docs/METRICS/
├── config.json              # System configuration
├── runs/                    # Agent run records
├── feedback/                # User feedback on agent responses
├── aggregates/              # Daily/weekly performance summaries
│   ├── daily/
│   └── weekly/
├── variants/                # A/B test prompt variants
├── optimisations/           # LLM-generated prompt improvements
│   ├── pending/             # Awaiting review/application
│   ├── applied/             # Successfully applied
│   └── rejected/            # Rejected improvements
└── templates/               # Analysis prompt templates
```

## How It Works

1. **Run Recording**: Each agent invocation is logged with inputs, outputs, and metadata
2. **Feedback Collection**: Users provide ratings and comments via `/syntek-dev-suite:learning-feedback`
3. **Aggregation**: Daily/weekly summaries are generated from run data
4. **Optimisation**: LLM analyses patterns and suggests prompt improvements
5. **Application**: High-confidence improvements are auto-applied (if enabled)

## Configuration

See `config.json` for current settings:

- `enabled`: Whether the learning system is active
- `auto_optimisation_enabled`: Whether to auto-apply high-confidence improvements
- `min_runs_for_analysis`: Minimum runs before generating optimisations
- `feedback_required_for_optimisation`: Minimum feedback entries needed
- `auto_apply_confidence_threshold`: Confidence level for auto-application

## Commands

| Command                               | Purpose                                 |
| ------------------------------------- | --------------------------------------- |
| `/syntek-dev-suite:learning-feedback` | Provide feedback on last agent response |
| `/syntek-dev-suite:learning-optimise` | Review and apply prompt improvements    |
| `/syntek-dev-suite:learning-ab-test`  | Manage A/B tests for prompts            |

## Privacy

- All data is stored locally in this repository
- No data is sent to external services
- Feedback is anonymised before aggregation
- Run records contain only metadata, not full conversation content
