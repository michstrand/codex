---
name: ai-enterprise-x-editorial
description: Discover high-attention public X stories about AI and enterprise architecture, validate the selected topic with authoritative sources, create an original editorial image, and optionally create one verified WordPress draft. Use for AI/enterprise-architecture trend posts sourced from X; never publish or update existing content.
---

# AI Enterprise X Editorial

Create a useful English article from a current, high-attention discussion at the intersection of artificial intelligence and enterprise architecture.

## Runtime configuration

Read `C:\DEV\codex\configuration\ai-enterprise-wordpress-config.json` fresh at the start of every run.

- Obtain `WP_USERNAME` and `WP_APP_PASSWORD` only from process environment variables or an approved secrets manager.
- Never print, store, log, or place credentials in content.
- Validate the configured HTTPS WordPress URL and positive author ID before any write.
- Default to `dry_run`. Enter `create_draft` only when the current request or an authorized automation explicitly permits a WordPress draft.
- Email delivery, publishing, scheduling, deletion, taxonomy creation, and changes to existing posts or media require separate explicit authorization and are not implied by draft creation.

## Required workflow

1. Generate a unique run ID and establish the mode and one-post limit.
2. Inspect current public X trend signals and recent relevant posts. Search broadly enough to avoid mistaking one viral post for a recurring topic.
3. Rank candidates using recency, visible attention, recurrence across independent accounts, relevance to AI and enterprise architecture, reader value, and availability of authoritative verification.
4. Treat X posts as discovery, commentary, or evidence of public attention. Do not treat popularity, engagement counts, screenshots, anonymous claims, or search snippets as proof of the underlying technical or business facts.
5. Open every X post used. Record its URL, author, timestamp when available, visible engagement when relevant, and access time. State that X visibility is incomplete or personalized when making trend claims.
6. Verify consequential claims using readable primary or authoritative sources. Prefer official standards bodies, protocol documentation, security organizations, regulators, vendors speaking about their own releases, and well-supported research. For technical claims, rely on primary documentation rather than secondary summaries.
7. Build a compact claim ledger. Mark each proposed statement as verified fact, attributed opinion, trend inference, analysis, uncertain, or rejected. Omit rejected and unsupported claims.
8. Before drafting, search all relevant WordPress posts and drafts using title, slug, entities, and search intent. Paginate when needed. If an item substantially overlaps, do not create or update anything; select another candidate or finish with an overlap report.
9. Resolve the configured category by exact slug from live WordPress. Reuse only existing relevant tags after a case-insensitive duplicate check. Do not create categories or tags unless the current request explicitly authorizes it.
10. Draft a natural, fact-checked article that explains why the discussion matters to enterprise architects. Separate observed X discussion from verified facts and editorial analysis. Include a visible Sources section containing only opened sources.
11. Use the WordPress title as the sole H1; body HTML begins with paragraphs and then uses semantic H2/H3 headings. Prepare a stable slug, excerpt, SEO title, meta description, primary keyword, and search intent. Do not guess SEO-plugin fields.
12. Use the available image-generation skill to create one original 16:9 editorial image tailored to the selected topic. Prefer dynamic abstract architecture, data, orchestration, governance, or human-decision concepts. Avoid readable text, logos, trademarks, product interfaces, misleading charts, recognizable people, robots-as-cliches, and claims presented as documentary imagery.
13. Inspect the image before upload. Reject malformed geometry, accidental text or logos, misleading visual claims, or a weak connection to the article. Prepare a descriptive filename, alt text, and caption. If safe image generation fails, create a text-only draft only if the user still authorized draft creation and report the warning.
14. Complete the preflight gate: evidence sufficient; claim ledger complete; trend inference qualified; overlap clear; category verified; title/body contain one H1 total; sources visible; image safe; payload status forced to `draft`; no existing content targeted.
15. In `create_draft` mode, perform a fresh exact-slug and intent overlap check immediately before writing. Upload at most one new media item, then POST exactly one new post with status exactly `draft`. Never send `publish`, `future`, or `private`.
16. GET the new post and verify draft status, non-empty title/content, correct author/category, and featured-media attachment. If a create call times out ambiguously, search for the exact slug, title, and run marker before any retry; never blindly create a duplicate.
17. Return a run report with topic, trend rationale and limitations, primary keyword, sources, overlap result, category/tag IDs, image path and media ID, WordPress post ID/status, edit and preview links, QA warnings, email state, and errors.

## Editorial focus

Good candidates include agentic architecture, AI governance, identity and authorization, MCP and tool integration, orchestration, semantic layers and knowledge graphs, AI observability and evaluation, security, legacy modernization, operating models, and measurable enterprise adoption.

Avoid generic AI hype, unsupported product claims, investment advice, copied social commentary, rumor-only stories, and topics whose connection to enterprise architecture is merely incidental.

## Hard stops

Create no WordPress post when credentials or configuration are unavailable, evidence is insufficient, authoritative sources conflict materially, the topic overlaps existing content, the category cannot be safely resolved, the user has not authorized a live draft, or WordPress would create a status other than `draft`.
