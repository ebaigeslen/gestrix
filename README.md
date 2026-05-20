# Gestrix

Gestrix is an intelligent SEO co-work agent.

It lets users generate top-tier, SEO-optimized product descriptions (and later: blog posts, tags, product names, internal links) through a team of AI agents. Users open a chat, optionally provide a product name, keywords, niche, writing style, sample structure, focus keyword, or reference links, then pick a skill. An orchestrator routes the request through specialist sub-agents and produces a finished description with a live preview alongside the chat.

## Agent team

| Agent | MVP? | Role |
|---|---|---|
| Orchestrator | yes | Routes the user request, decides which sub-agents to call, manages handoffs |
| Writer | yes | Produces the final product description from all gathered context |
| Naming | optional in MVP | Generates a product name only if the user didn't provide one |
| Keyword | optional in MVP | Finds focus keyword + semantics only if the user didn't provide them |
| Researcher | phase 2 | Tavily-powered deep research, toggle in chat |
| Evaluator | phase 2 | Scores Writer output against a rubric, triggers one revision pass |

## MVP scope

The MVP ships one skill: `product-description-writer`. Blog post writer, tag generator, and internal-linker land in later phases.

## Status

This project is in progress and will be completed in one week.
