# North-star questions

The 8 questions /discovery Phase 1 walks you through. Answer in your own words — short is fine, honest is mandatory. Each answer is recorded in the idea brief with a source tag (see bottom).

This file is the question bank. Your answers live in `docs/discovery/idea-brief-v<N>.md`; the canonical north-star is written at approve-exit to `docs/product/north-star.md`.

## 1. Who is it for?

Name the **primary** segment archetype and, if there is one, a **secondary** segment. Be specific enough that you could picture one real person in each. "Developers" is too broad; "solo technical founders shipping their first SaaS, ~20 hr/week" is a segment.

## 2. What's their problem?

The problem as *they* experience it — in their words, not yours. What do they currently do instead, and why does that hurt?

## 3. How does it solve the problem?

The mechanism. Not the feature list — the causal story for why this makes the problem go away or shrink.

## 4. What does this? (high-level description)

One or two sentences describing the thing itself. If you had to put it on a landing page header, what would it say?

## 5. Biggest risks?

The 2-4 things most likely to kill this. Be adversarial with yourself — market risk, execution risk, "nobody actually wants this" risk, "I can't build this" risk. Phase 3 will pressure-test these; name them now.

## 6. Why now?

What changed that makes this viable or necessary today and not two years ago? If nothing changed, that is itself an answer worth noticing.

## 7. Why am I the right person? (founder-fit)

What do you specifically bring — domain knowledge, unfair access, lived experience of the problem, technical fit? "I want to" is not founder-fit.

## 8. Skills I have / missing / how to close the gap

List the skills this needs. Mark which you have, which you don't, and for each gap: hire / learn / partner / tool-around-it. Then state an honest advisory verdict for this idea as it stands:

- **build** — fit is strong enough to proceed to Phase 2 research.
- **pivot** — the problem is real but this framing or this founder-fit is wrong.
- **kill** — the gaps or risks are terminal.

This verdict is advisory only — Phase 3's challenge memo produces the binding verdict. But say it out loud now.

## Answering "I don't know"

For any question you can't answer confidently, /discovery offers three paths — pick one per question:

- **A — Hear AI recommendation.** Chat-Claude proposes an answer; you accept it as-is or edit it.
- **B — Defer to Phase 2 research.** The question becomes a research input; Phase 2 tries to answer it.
- **C — Keep open.** Revisit at the end of Phase 1 once the other answers are in.

## Source tags

Every field in the idea brief carries one tag, so downstream phases know how much weight to give it:

- `(user)` — you answered it directly.
- `(ai-recommended)` — came from path A; chat-Claude proposed it. Phase 3's Skeptic scrutinizes these harder.
- `(research-pending)` — came from path B; waiting on Phase 2.
- `(open)` — came from path C; still unanswered.

An approve-exit while 3+ fields are still `(research-pending)` is allowed but downgrades the run to `DONE_WITH_CONCERNS`.
