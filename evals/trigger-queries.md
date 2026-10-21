# Trigger queries for designtaste-by-oasis

20 probe queries: 10 should trigger the skill, 10 should not.
Used with `evals/skill-eval.yaml`.

## Should trigger (expect: skill loads)

1. Help me run visual direction for our new marketing site, starting with brainstorming.
2. Review these three wireframes and collect red/green feedback from me.
3. Build a taste profile from these example sites, then propose three layout directions.
4. Generate a design-system.md with tokens (not values) from my picked wireframe.
5. Ask me the 5-question website questionnaire, then rank the design parts.
6. I want a clickable review page on port 8000 for our homepage wireframes.
7. Turn my design-feedback.md into a detailed design system with button states.
8. Compare these two landing pages and tell me which aesthetic fits our brand.
9. Slim down this hero copy and fix the CTA placement.
10. Check my planned pricing section against the design system before I build it.

## Should NOT trigger (expect: skill stays off)

1. Run my backend test suite and fix any failing tests.
2. Debug this Python traceback from my data pipeline.
3. Write a SQL migration to add an index on the users table.
4. Help me configure Kubernetes ingress for the staging cluster.
5. Review this pull request for race conditions in the payment worker.
6. Explain how TCP congestion control works in this packet trace.
7. Optimize this Rust function for lower memory allocations.
8. Set up CI caching so our builds run faster.
9. Migrate our auth service from JWT sessions to opaque tokens.
10. Profile this Go binary and find the hot loop.
