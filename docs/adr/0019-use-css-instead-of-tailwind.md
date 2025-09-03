# Use plain CSS instead of Tailwind

Date: 2025-09-03

## Status

Accepted

## Context

For styling our frontend, several options were considered. Initially, we evaluated **Tailwind CSS** because it offers fast development with utility classes and ensures consistent design.  

However, during setup we encountered configuration issues that would require extra effort to resolve. Additionally, the benefits of Tailwind for our current project are limited, as we do not require highly complex or design-heavy interfaces.  

The team already has solid experience with plain CSS, making it the simpler and more direct solution.  

### Alternatives Considered

- **Tailwind CSS** — modern utility-first approach, but caused configuration problems and introduced unnecessary overhead.  
- **Plain CSS (possibly modularized)** — straightforward, no setup overhead, already familiar to the team.  

## Decision

We will use **plain CSS** for styling the frontend.  

This enables us to:  
- Start immediately without additional tooling hurdles.  
- Leverage the team’s existing knowledge.  
- Maintain full control over styles without framework dependencies.  

## Consequences

- Fewer built-in design utilities compared to Tailwind.  
- We must ensure style consistency (spacing, colors, components) ourselves.  
- No additional build or configuration issues from Tailwind.  
- The project remains leaner and easier to maintain.  
