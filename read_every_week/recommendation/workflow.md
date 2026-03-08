# Recommendation Engine

This document explains how the article recommendation system works, including the pipeline flow and the selection strategies used to choose articles.

The system is designed to recommend a small number of articles that fit within a daily reading time budget while encouraging consistent reading habits.

---

# Recommendation Pipeline

The recommendation system follows a structured pipeline.

```
All Articles
     ↓
Candidate Filtering
     ↓
Candidate Pool Preparation
     ↓
Strategy Selection
     ↓
Final Recommendation
```

Each stage has a clear responsibility.

---

## 1. Candidate Filtering

The first step removes articles that should not be considered for recommendation.

Articles are excluded if:

* The article has no reading time estimate.
* The article has already been read.
* The article was recommended recently and is still within the cooldown window.

The cooldown window prevents the same article from being recommended repeatedly in a short period.

Example:

```
cooldown_days = 14
```

If an article was recommended within the last 14 days, it will be skipped.

---

## 2. Candidate Pool Preparation

Eligible articles are split into two groups:

```
Regular Articles
Worth-Revisit Articles
```

### Regular Articles

Articles that have not been marked as worth revisiting.

These form the main pool used for the primary recommendation.

### Worth-Revisit Articles

Articles that are considered valuable to revisit later.

These are handled separately and do not count toward the primary recommendation limits.

Example rule:

```
max_worth_revisit = 2
```

This means up to two revisit articles may be suggested alongside the main recommendations.

---

## 3. Strategy Selection

Once the candidate pool is prepared, a selection strategy chooses which articles should be recommended.

All strategies respect the following constraints:

```
max_count
max_total_minutes
```

Example:

```
max_count = 3
max_total_minutes = 35
```

The strategies differ in how they explore possible combinations.

---

# Selection Strategies

The system currently includes four strategies.

---

## Greedy Strategy

Description:

Articles are sorted by reading time, and the shortest articles are selected first until the limits are reached.

Example process:

```
Sort by reading_time
Pick smallest article
Add until limits reached
```

Advantages:

* Very fast
* Deterministic
* Predictable recommendations

Disadvantages:

* Tends to favor short articles
* May ignore better combinations of medium-length articles

Typical use:

```
Weekday recommendations
Low cognitive load days
```

---

## Random Fit Strategy

Description:

Candidates are shuffled randomly and then selected greedily.

Example process:

```
Shuffle candidates
Select articles until limits reached
```

Advantages:

* Adds variety
* Very cheap computationally

Disadvantages:

* Still somewhat biased toward shorter articles
* Does not explore combinations deeply

Typical use:

```
When diversity is desired with minimal cost
```

---

## Bounded Knapsack Strategy

Description:

This strategy explores combinations of articles within a limited candidate subset.

Steps:

1. Randomly sample up to 10 candidates.
2. Generate combinations of those candidates.
3. Keep combinations that satisfy the constraints.
4. Select one valid combination randomly.

Example:

```
Sample ≤10 articles
Generate combinations
Pick a valid set
```

Advantages:

* Explores multiple article combinations
* Produces more balanced recommendations

Disadvantages:

* Computational cost increases with candidate size
* Requires sampling to remain efficient

Typical use:

```
Small candidate pools
Exploratory recommendations
```

---

## Stochastic Sampling Strategy

Description:

This strategy runs multiple randomized trials to generate candidate combinations.

Steps:

```
Repeat N times:
    Shuffle candidates
    Fill selection under constraints
Choose one result randomly
```

Example:

```
trials = 80
```

Advantages:

* Scales well to large candidate pools
* Produces diverse combinations
* Computationally efficient

Disadvantages:

* Not guaranteed to find the optimal combination

Typical use:

```
Large candidate pools
Primary production strategy
```

---

# Strategy Comparison

| Strategy            | Speed     | Diversity | Combination Exploration |
| ------------------- | --------- | --------- | ----------------------- |
| Greedy              | Very Fast | Low       | None                    |
| Random Fit          | Fast      | Medium    | Low                     |
| Bounded Knapsack    | Medium    | High      | High                    |
| Stochastic Sampling | Fast      | High      | Medium                  |

---

# Default Strategy

The system typically uses:

```
stochastic_sampling
```

This provides a good balance between performance and recommendation diversity.

Greedy may be used when deterministic behavior is preferred.

---

# Design Principles

The recommendation system is built around a few guiding principles.

### Keep computation predictable

Algorithms are bounded to avoid combinatorial explosion.

### Encourage reading consistency

Recommendations prioritize articles that fit within the available reading time.

### Maintain diversity

Randomized strategies prevent the same articles from appearing repeatedly.

### Keep the system extensible

New strategies can be added without modifying the recommendation engine.

---

# Future Improvements

Possible future enhancements include:

* Time budget utilization scoring
* Difficulty progression based on reading streak
* Weighted article priorities
* Adaptive strategy selection

These improvements can be added without major architectural changes because the strategy system is modular.

