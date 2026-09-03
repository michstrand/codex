# Editorial Argument Guidelines

Use these rules for every article produced by this skill. The goal is identifiable expert reasoning, not prose engineered to appear human.

## Required editorial brief

Before writing, state internally:

- one defensible thesis about what readers overlook, misunderstand, or should do differently;
- one realistic enterprise scenario that makes the architecture concrete;
- one non-obvious insight derived from the evidence;
- one material trade-off or cost of the preferred design;
- one failure mode and its operational consequences;
- one current assumption, term, or industry practice the article challenges;
- one falsifiable recommendation expressed as an architecture test.

Do not draft until all seven elements are supported. They may overlap in the article, but none may be replaced by generic advice.

## Build an argument, not a survey

- Select a specific claim rather than a broad topic. A complete catalogue of developments is not an argument.
- Prefer depth on three to five ideas that materially support the thesis. Give the most important issue disproportionate space when warranted.
- Start from reasoning, then use sources as evidence. Avoid constructing the article as a sequence of source summaries.
- Explain each inferential step between an observation and a recommendation, especially where agent tool use changes trust boundaries, authority, recoverability, or accountability.
- Be precise about social evidence. A few X posts show that practitioners are discussing an idea; they do not establish consensus unless broader evidence supports that claim.

## Make architecture operational

- Introduce a concrete business scenario early, such as approving a payment, modifying a customer record, processing a claim, or deploying software. Revisit it when testing design choices.
- Focus on failure boundaries: expired authorization during execution, partial success across systems, misunderstood business terminology, rejected human approval, unavailable dependencies, or a later audit.
- Turn abstractions into questions. For identity, ask whose authority is exercised, how it is revoked, and which identity appears in the audit log. Apply the same treatment to memory, control planes, semantic layers, agentic meshes, and similar terms.
- Challenge ambiguous terminology by defining what it means operationally in this particular architecture.
- Separate durable principles—authorization, accountability, recoverability, business invariants—from temporary scaffolding imposed by current models, vendors, or products.

## Show costs and disagreement

- Explain the trade-offs created by recommendations, including latency, complexity, centralized dependencies, organizational ownership, reduced autonomy, cost, and developer friction where relevant.
- Include an informed point of disagreement: something current practice may overestimate, underestimate, or standardize prematurely. Support it with reasoning and evidence rather than provocation.
- Make recommendations falsifiable. Prefer a test such as “an auditor can reconstruct the authorizing identity, invoked tools, policy decisions, and outcome” over “improve observability.”

## Composition and editing

- Vary section logic. A section may follow a failure scenario, interrogate a term, analyze evidence, weigh a trade-off, or establish a design test. Do not repeat a mechanical claim–source–implication template.
- Use “not X, but Y” reframing sparingly. Avoid perfectly balanced lists unless the items form a genuine taxonomy.
- End with decisions, tests, an unresolved design problem, or the strongest implication. Do not recap the entire article or use generic claims about being “best positioned.”
- On the final pass, ask what new fact, distinction, consequence, or reasoning each paragraph gives the reader. Rewrite or delete paragraphs whose only message is that the topic matters.

## QA record

The run report must name the thesis and the seven required editorial elements. It must also record one example of a paragraph removed or rewritten during the information-density pass, or state that every paragraph passed with a concrete reason.
