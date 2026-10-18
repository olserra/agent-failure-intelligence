# Commercial validation plan (Phase F)

Status: prepared 2026-10-18. Nothing here has been sent to anyone. All outreach
requires the project owner's explicit approval first.

## 1. Measurement events (privacy-minimal)

No analytics cookies, no trackers, no third-party pixels. Events are derived
from data the product already needs:

| Event | Source | Personal data |
|---|---|---|
| `landing_visit` | aggregate only (Cloudflare request count, no per-user log) | none |
| `pilot_request_submitted` | D1 insert on POST /api/pilot | only the fields the user typed, with consent |
| `pilot_request_duplicate` | API 200 duplicate response | none new |
| `repo_star` / `repo_fork` | GitHub public counts (checked manually) | none |
| `interview_completed` | manual note by owner | with the interviewee's knowledge |

Signups and clicks are not treated as proof of willingness to pay. Willingness
to pay is validated only in interviews (evidence question 5 below).

## 2. Initial list of ten potential B2B buyers

Selection criterion: the company publicly ships or operates AI agents that call
tools in production, so reproducible agent-failure testing maps to a live,
expensive problem. These are hypotheses to validate in interviews, not claims
about these companies' internal practices.

| # | Company | Why they fit (public product context) |
|---|---|---|
| 1 | Sierra | Customer-service agents for enterprises; agent misbehavior hits their customers' users directly |
| 2 | Decagon | Customer-support agents for large brands; same failure exposure |
| 3 | Intercom (Fin) | Support agent at scale; regression testing of agent behavior is a known pain |
| 4 | Cognition (Devin) | Autonomous coding agent; tool misuse and privilege boundaries are core risks |
| 5 | Replit (Agent) | Coding agent with shell/tool access in user workspaces |
| 6 | Harvey | Legal AI agents; high-cost domain where wrong actions are unacceptable |
| 7 | Glean | Enterprise agents over internal data; permission boundaries matter |
| 8 | LangChain | Agent framework vendor; testing story for agent users is adjacent to their product |
| 9 | CrewAI | Agent framework vendor; same adjacency |
| 10 | Vercel | Ships agent/tooling products and hosts many teams building agents |

## 3. Contact plan (nothing sent without approval)

Order: start with framework-adjacent companies (8-10) where the project is
complementary, then agent operators (1-7).

1. Open-source first: a clear README result and one verified failure write-up
   are the introduction; no cold pitch before a real artifact exists.
2. Warm routes only: public maintainers' channels, community forums they
   already participate in, conference/community contacts. No scraped lists,
   no mass email, no astroturfing.
3. First message (draft, per company, for owner approval): 3-4 sentences.
   What the project does, the one verified result, link to the repo, and a
   single ask: a 20-minute interview about how they test agents today.
4. Cadence: at most 2 new contacts per week, each message individualized.
   One follow-up after 7 days, then stop.
5. LinkedIn/X posts: written by the agent, posted manually by the owner,
   at most one per week.

## 4. Interview script (~20 minutes)

Goal: validate the problem and what evidence would justify paying for a pilot.

1. How does your team test agents today before and after deploy?
   (walk me through the last time an agent change went out)
2. What failure types have been most expensive - in money, time, or trust?
   Can you give a recent example?
3. Which tools do you already use for this (evals, red-teaming, observability,
   manual QA)? What do they miss?
4. How do you buy this kind of solution: who decides, what budget line,
   build vs buy, procurement process?
5. What evidence would justify paying for a pilot? (a benchmark on your own
   agents? a reproducible failure report? a regression suite in CI?)
6. If we ran our harness on one of your agents and showed you the results,
   would you take that meeting? What would you want to see first?

Rules: no leading questions, no pitching during the interview, write down
exact words, ask for the cost figure behind "expensive".
