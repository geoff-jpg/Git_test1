# OpenAI's October 2026 mathematics release: fields, highlights, and the Riemann zeta function

*Report compiled 7 October 2026. Sources: the public repository [openai/math](https://github.com/openai/math) (cloned and read directly) and press coverage listed at the end.*

> **Caveat up front.** All results below are **claims by OpenAI** about output from an unreleased internal model. The README says that "some of the unformalized results could have issues". Sam Altman has described them as not yet confirmed by outside mathematicians. I did not compile the Lean proofs myself (roughly 26 million lines of Lean code), and I have not checked any proof.

## 1. What was released

| Item | Figure |
|---|---|
| Release date | 6 October 2026 (date on `overview.pdf`) |
| Manuscripts | **722** PDFs with LaTeX sources, in `preprints/` |
| Result families | **372**. Families are numbered 001–**377** with five gaps, which is probably where the "377" figure comes from. |
| Subject areas | 17 |
| Lean formalisation | `lean/formalization.yaml` lists **162 manuscripts** with a formalized main result. **235 of 372 families** have a Lean scope page (`lean/docs/NNN.md`), but the scope is often partial. |
| Reasoning summaries | Abridged model "reasoning traces" for only **10** results |
| Licence | Apache-2.0 |
| How it was produced | Over the evaluation, the model was posed about 4,000 open problems. Each result used about 3 hours of "ChatGPT Pro thinking compute" on average. Results were grouped and filtered for significance. |

**Exceptions to the standard procedure, per the README:** the zero-free region for the Riemann zeta function, and the Hodge conjecture for CM abelian varieties. The 11/12 zeta write-up was also "human edited for readability". This matters for the zeta question in Section 3.

## 2. Fields covered

| Subject (OpenAI's classification) | Families | With Lean page | Selected headline claims (family number) |
|---|---:|---:|---|
| Theoretical computer science | 40 | 32 | Unique Games Conjecture (102); **L = RL = BPL** (103); matrix multiplication exponent ≤ 9/4 (107); integer multiplication below n log n (109); hardness of 3-colouring (106); Subset Sum in O(2^0.49n) (138) |
| Combinatorics | 37 | 33 | Plane cannot be 5-coloured (158); Borsuk fails in dim 9 (156); Sidorenko counterexamples (161); circulant Hadamard conjecture (179); Erdős reciprocal-sum / quasipolynomial Szemerédi (159) |
| Algebraic & complex geometry | 36 | 7 | **Rational Hodge conjecture for CM abelian varieties & K3 products** (032); Fujita freeness (038); Nagata's conjecture (039); Bloch's conjecture for surfaces (040); MMP termination for fourfolds (056) |
| Number theory | 31 | 16 | **Quasi-Riemann hypothesis** (003); **Hilbert's tenth problem over ℚ** (004); **Catalan's constant irrational** (005); full BSD formula in Selmer corank ≤ 1 (002); Goldfeld's conjecture (006); two-point Chowla (007); irrationality exponent of π is 2 (017); Artin primitive roots: infinitude for every base (029) |
| Probability & statistical mechanics | 29 | 19 | Mézard–Parisi formula for diluted spin glasses (221); no infinite critical clusters on quasi-transitive graphs (213); Benjamini–Schramm nonuniqueness (214) |
| Differential geometry | 29 | 15 | Yau's uniformization conjecture (338); Katok entropy rigidity (339); nearby Lagrangian counterexample (340); closed geodesics (345) |
| Mathematical physics | 25 | 17 | Spontaneous magnetisation in the 3D quantum Heisenberg ferromagnet (271); spin-one Haldane gap (268); 2D gapped area law (265); exactly three MUBs in dimension six (266); strong cosmic censorship near Kerr (264) |
| Operator algebras | 19 | 14 | **All nonabelian free group factors isomorphic** (287); Kadison similarity (288); hyperinvariant-subspace counterexample (293); Baum–Connes counterexamples (285) |
| Topology | 18 | 3 | Hilbert–Smith conjecture (304); Kervaire invariant at p = 3 (309); cosmetic surgery conjecture (306) |
| Algebra | 18 | 9 | **Kaplansky zero-divisor counterexample** (196); non-sofic groups (197); Kurosh problem counterexample (201); Serre intersection multiplicity (193) |
| Real & complex analysis | 16 | 9 | Kakeya in 3 and 4 dimensions (074); Falconer distance conjecture (073); 3D Bochner–Riesz (078); Brennan's conjecture (072) |
| PDE | 16 | 11 | Global smoothness for 3D relativistic Vlasov–Maxwell (362); De Giorgi conjecture in dim 8 (375); hot spots for simply connected planar domains (369) |
| Convex & metric geometry | 15 | 13 | Mahler conjectures (087); log-Brunn–Minkowski (091); universal optimality of the triangular lattice (090) |
| Group theory | 14 | 12 | **Thompson's group F is nonamenable** (248); Cannon's conjecture (246); Boone–Higman (250) |
| Dynamical systems & ergodic theory | 12 | 9 | Uniform limit-cycle bounds in Hilbert's 16th problem (143); Rokhlin multiple mixing (145) |
| Functional analysis | 11 | 10 | Complete Crouzeix conjecture (325); Tingley's problem (322) |
| Mathematical logic | 6 | 6 | Shelah's eventual categoricity (240); rigidity of the Turing degrees (241) |

The full list of all 372 families is in [`openai-math-appendix-families.md`](openai-math-appendix-families.md).

**Pattern.** The discrete fields (combinatorics, TCS, logic, functional analysis, convex geometry) are mostly Lean-backed. The deep structural fields are mostly *not*: only 7 of 36 families in algebraic geometry and 3 of 18 in topology have Lean pages. Many of the most famous claims sit in those weakly formalised fields, including Hodge for CM abelian varieties, BSD, Hilbert's tenth over ℚ, free group factors, and L = BPL.

## 3. Highlights: results that would be major discoveries if confirmed

Ranked by how significant the result would be if correct. "Lean" marks a family with a formalization page.

1. **Quasi-Riemann hypothesis (003, Lean):** see Section 4.
2. **Unique Games Conjecture (102, Lean):** this is the central open problem in hardness of approximation. It has a reasoning trace and Lean coverage.
3. **L = RL = BPL (103):** full derandomisation of log-space. No Lean page.
4. **Hilbert's tenth problem over ℚ (004):** proves that it is undecidable whether a polynomial has a rational root. This was open since the 1970s. No Lean page.
5. **Rational Hodge conjecture for CM abelian varieties (032):** this is a special case of a Millennium Problem, not the whole Hodge conjecture. The README says it came from a non-standard procedure.
6. **Birch–Swinnerton-Dyer formula in Selmer corank ≤ 1, with Goldfeld's conjecture (002, 006):** together these would give full BSD for a density-one set of quadratic twists. This is a partial Millennium-problem advance.
7. **Isomorphism of free group factors (287):** settles a famous question in operator algebras from the 1940s–80s. It has a reasoning trace.
8. **Thompson's group F is nonamenable (248, Lean):** a notorious decades-old question.
9. **Matrix multiplication ω ≤ 9/4 (107, Lean)** and **integer multiplication below n log n (109):** both would be large algorithmic jumps.
10. **Irrationality of Catalan's constant (005)** and **irrationality exponent of π equal to 2 (017, reasoning trace):** these are classical open problems in Diophantine approximation.
11. **Kaplansky's zero-divisor and direct-finiteness counterexamples (196–197, Lean):** these are disproofs of long-standing group-ring conjectures, and the Lean checks make them comparatively credible.
12. **Hadwiger–Nelson: the plane is not 5-colourable (158, Lean):** the chromatic number of the plane would then be 6 or 7.

## 4. The Riemann zeta function: what OpenAI claims (family 003)

### 4.1 The papers

| Manuscript | Date | Claim | Lean |
|---|---|---|---|
| *The Quasi-Riemann Hypothesis: A Zero-Free Half-Plane ℜs > 7/8* (`preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/paper.pdf`) | 30 Sep 2026 | ζ(s), every Dirichlet L-function, and every finite-order Hecke L-function over ℚ(√−3) have **no zeros with ℜs > 7/8**. The pole at s = 1 is excluded. 199 pages. | **Yes**: main theorem |
| *The Quasi-Riemann Hypothesis (alternate 11/12 proof)* (`…October-5-2026/paper2.pdf`) | 5 Oct 2026 | Same statement with the weaker 11/12. A shorter, independent route, human-edited for readability. 49 pages. | No |
| *Uniform exclusion of Landau–Siegel zeros* (`Uniform-exclusion-of-Landau-Siegel-zeros-October-1-2026/paper.pdf`) | 1 Oct 2026 | An absolute c > 0 such that every real zero β of every primitive real Dirichlet L-function of conductor q ≥ 3 satisfies **(1 − β) log q ≥ c**. 9 pages. | **Yes** |

A supporting result, **family 023**, claims an unconditional proof of Patterson's first-moment asymptotic for cubic Gauss sums. The 7/8 paper cites it as independent and says it is not used as an input.

### 4.2 What this would mean

- **It is not the Riemann Hypothesis.** RH puts every nontrivial zero on ℜs = 1/2. The paper states plainly that "the Riemann hypothesis remains open". What it claims is the *quasi-Riemann hypothesis*: there is *some* fixed σ₀ < 1 with no zeros to the right of it. Until now nobody could prove even that. Classical zero-free regions (de la Vallée Poussin, Vinogradov–Korobov) shrink towards the line ℜs = 1 as the height grows.
- **If correct, it would be the biggest advance on ζ's zeros since 1896.** Hadamard and de la Vallée Poussin proved that there are no zeros on ℜs = 1. A fixed 7/8 strip would give a **power-saving error term in the prime number theorem**, roughly π(x) = Li(x) + O(x^{7/8+ε}). The same would hold uniformly for primes in arithmetic progressions.
- **Siegel zeros would be killed.** Excluding Landau–Siegel zeros is a decades-old obstruction behind ineffective constants, for example in class-number bounds. This is a separate, 9-page paper, so it is a natural first target for expert checking.
- **Stated corollaries in the 7/8 paper:**
  - Vinogradov's least-quadratic-nonresidue conjecture, n(p) ≤ C(log p)^A.
  - A **deterministic polynomial-time algorithm for square roots mod p**.

  Both follow by plugging the strip into a known "weak-GRH" theorem of Bhargava–Ivanyos–Mittal–Saxena.

### 4.3 How the proof is said to work (from the introduction)

1. **Work over Eisenstein integers.** The argument uses the field F = ℚ(√−3) and the cubic/sextic Hecke characters over it.
2. **Use cubic theta functions.** It draws on Kubota's metaplectic theory and Patterson's cubic theta series, with the unconditional cusp expansions of Dunn–Radziwiłł.
3. **Run a two-stage argument.** Each stage compares a "reflected" representation and a "Poisson" representation of a completed cubic-theta sum.
   - Part I gets a zero-free half-plane at 11/12.
   - Part II adds prime compensation and fourth-moment estimates to push the bound to 7/8.
4. **Transfer to Dirichlet L-functions.** The result moves to all Dirichlet L-functions, and so to ζ, by factoring Hecke L-functions over F.

The 9-page Siegel-zero paper uses a different route: a transcendence-style interpolation-determinant argument over the biquadratic field ℚ(√d, √2).

**Novelty.** This is a genuinely unconventional route. It goes through cubic metaplectic forms rather than through zero-density or mollifier methods. That makes it both potentially important and harder for experts to check quickly.

### 4.4 Verification status

- **Lean statements look right.** The comparator challenge `lean/ComparatorChallenges/QuasiRiemannHypothesis.lean` states, using Mathlib's own `riemannZeta`:
  `theorem riemannZeta_ne_zero_of_seven_eighths_lt_re {s : ℂ} (hs : (7/8 : ℝ) < s.re) : riemannZeta s ≠ 0`.
  - Only the standard axioms are permitted (`propext`, `Quot.sound`, `Classical.choice`).
  - The solution module `OAI/NumberTheory/DirichletL/` is about **2,900 files and 487,000 lines** of Lean.
  - My grep of that directory found **no `sorry`, `admit`, `axiom` or `native_decide`**.
  - Because the theorem is stated against Mathlib's standard definition of ζ, the usual worry that a formal statement might not match the intended one is much smaller here than usual.
- **What I did not check:** I did not build the Lean project. That needs Lean 4.34.1, Mathlib, and 23 patched dependencies. If it does compile under the comparator, this would be the strongest evidence in the release.
- **Lean coverage is partial.** It covers the 7/8 theorem for ζ, Dirichlet and Hecke L-functions, and the Siegel-zero gap. It does **not** cover the paper's later applications (Vinogradov conjecture, square-root algorithm) or the 11/12 alternate paper.
- **Process:** this family was produced by a non-standard procedure, according to the README.
- **Reception so far:**
  - Press reports quote Alex Kontorovich (Rutgers) as saying that "if a human had done this, it would be an instant Fields Medal".
  - Mathematicians have sharply criticised the release process ("mafia-like", ignoring requests at an August meeting to follow publication norms).
  - I found no independent expert confirmation or refutation of the zeta proof yet.
- **Press confusion:** some outlets report 7/8 and others 11/12. Both are correct: 7/8 is the main theorem, and 11/12 is the alternate, weaker proof.

## 5. Bottom line

- **Volume and claims.** The release is genuine and very large. It claims solutions to dozens of famous open problems across all 17 areas.
- **Evidence varies by field.** Combinatorics, TCS and logic are mostly Lean-backed. Algebraic geometry, topology and much of number theory rest on unrefereed PDFs.
- **Riemann zeta.** The specific claim is a **zero-free half-plane ℜs > 7/8 for ζ and all Dirichlet L-functions**, plus **no Siegel zeros**. It is *not* RH. If the Lean proof compiles as advertised, this would be a historic result for prime number theory.

## 6. Follow-up (in progress): Lean build and academic commentary

### 6.1 Lean build status (interim, 7 Oct 2026)

- **Import closures.** The 7/8 proof (`OAI.NumberTheory.DirichletL.Nonvanishing`) imports 2,924 OpenAI modules (about 486,000 lines). The Siegel-zero proof (`OAI.NumberTheory.SiegelZeros.Main`) imports 306 modules (about 70,000 lines). Both rely only on Lean core, Mathlib, PrimeNumberTheoremAnd and (for 7/8) RellichKondrachov.
- **Gap check.** My grep of both closures found no `sorry`, `admit`, `axiom`, `opaque` or `native_decide`. The comparator configs allow only `propext`, `Quot.sound` and `Classical.choice`.
- **Independent third-party build.** [Zhang-Liao/quasi-riemann](https://github.com/Zhang-Liao/quasi-riemann) extracted the 7/8 proof into a standalone project. It reports a successful `lake build` with Lean 4.34.1 on 7 Oct 2026, and an axiom check showing only the three standard axioms. **I confirmed that all 2,924 extracted OAI files are byte-identical to OpenAI's originals.** That project did not run the comparator.
- **My own build.** This is not finished yet. Lean 4.34.1 is installed; the egress policy blocks `release.lean-lang.org`, so I used the GitHub release instead. Dependencies were downloading when this was saved. **Resume:** `cd lean && lake exe cache get && lake build OAI.NumberTheory.DirichletL.Nonvanishing OAI.NumberTheory.SiegelZeros.Main`, then run `#print axioms` on the four comparator theorems.

### 6.2 What academics have said so far (secondary sources only)

Most of the pages below were blocked from direct fetching by this session's network policy. These comments come from search-engine snippets of the coverage, so check the originals before quoting them.

- **Alex Kontorovich (Rutgers, leads the PNT+ Lean project):** posted on X "Quasi-RH?!", and said that if a human had done this it would be "an instant Fields Medal, no questions asked". He noted that previous zero-free regions got thinner and thinner with height, which is why a fixed boundary is striking. The OpenAI Lean proof depends on his PrimeNumberTheoremAnd library.
- **Levent Alpöge (Anthropic, formerly Harvard):** strongly praised the quasi-RH and no-Siegel-zero results ("the most significant moment in mathematical history", per Latent Space).
- **Daniel Litt (Toronto):** measured and positive. He said one result is a special case of a conjecture of his, and argued that there is no reason the answers should be kept secret.
- **Andrew Sutherland (MIT):** said claims should be treated as unverified until the model is released and results can be replicated.
- **Terence Tao (UCLA):** criticised the "insane" pace of frontier-lab releases (Scientific American). In September he led a statement co-signed by 25 Fields Medallists, "A Severe Misalignment of AI in Mathematics". I found no Tao comment on the zeta proof itself.
- **Multiple mathematicians to Wired:** said the release ignored peer review and publication norms agreed at a closed August meeting.
- **A Hacker News commenter identifying as a number theorist:** Fields-level if true, but not bigger than the prime number theorem itself.
- **Bottom line on commentary:** as of 7 Oct, **no named number theorist has publicly confirmed or found an error in the 7/8 or Siegel-zero proofs.** Reactions are about significance and process, not correctness.

## 7. Possible next steps (not done in this session)

- Build the Lean comparator for `QuasiRiemannHypothesis.json` and `SiegelZeros.json`.
- Read Parts I and II of the 7/8 paper in detail, or summarise the 9-page Siegel-zero paper fully.
- Track expert commentary from number theorists over the coming weeks.

## Sources

- [Zhang-Liao/quasi-riemann (standalone build)](https://github.com/Zhang-Liao/quasi-riemann)
- [Digg: Kontorovich reaction](https://digg.com/ai/euchcuw1)
- [Startup Fortune: mathematicians are not impressed](https://startupfortune.com/openai-drops-722-ai-math-proofs-and-mathematicians-are-not-impressed/)
- [Scientific American](https://www.scientificamerican.com/article/openai-unleashes-hundreds-more-math-results-upon-a-field-already-in-shock/)
- [Gary Marcus](https://garymarcus.substack.com/p/complementary-remarks-from-gary-marcus)
- [WebProNews: Math blitz sparks outrage](https://webpronews.com/openais-math-blitz-sparks-outrage-among-researchers)
- [Kingy.ai: results, compute and costs](https://kingy.ai/blog/openai-math-722-manuscripts-results-proofs-compute-costs/)

- Repository: [github.com/openai/math](https://github.com/openai/math): `README.md`, `CONTENTS.md`, `overview.tex`, `lean/formalization.yaml`, `lean/docs/003.md`, and the three family-003 PDFs
- [Quartz: OpenAI released 372 groups of math results on GitHub](https://qz.com/openai-math-results-github-millennium-prize-100726)
- [Interesting Engineering: OpenAI's largest math release](https://interestingengineering.com/ai-robotics/openai-largest-math-release-lean-proofs)
- [MindStudio: OpenAI's 722 Math Proofs](https://www.mindstudio.ai/blog/openai-722-math-proofs-release)
- [CellCog: What's proved, what's checked](https://cellcog.ai/blog/openai-math-results/)
- [Latent Space AINews: Quasi-Riemann-Hypothesis](https://www.latent.space/p/ainews-quasi-riemann-hypothesis-openai)
- [OfficeChai: Quasi-Riemann hypothesis explanation](https://officechai.com/ai/quasi-riemann-hypothesis-explanation/)
- [OfficeChai: Mathematicians react](https://officechai.com/ai/mathematicians-react-with-shock-and-wonder-after-openai-releases-over-300-math-proofs-at-once/)
- [BigGo Finance: sparking fury in the math community](https://finance.biggo.com/news/1d522643-5fd9-4ac5-ae86-e4a5b99edfe2)
- [36Kr: Mathematics Big Bang](https://eu.36kr.com/en/p/4015128916676736)
