from __future__ import annotations

import itertools
import random
from typing import Dict, List

from ..models import Article


class RecommendationStrategy:
    """Base interface for recommendation selection strategies.

    Each strategy receives candidate articles and rule constraints
    and returns a list of selected articles that satisfy the limits.
    """

    def select(self, candidates: List[Article], rule: Dict[str, int]) -> List[Article]:
        raise NotImplementedError


class GreedyStrategy(RecommendationStrategy):
    """Deterministic selection based on shortest reading time first.

    Candidates are ordered by reading time and selected until the
    maximum count or time budget is reached. This strategy is fast
    and predictable but tends to favor shorter articles.
    """

    def select(self, candidates: List[Article], rule: Dict[str, int]) -> List[Article]:

        ordered_candidates = sorted(
            candidates,
            key=lambda article: article.reading_time_min,
        )

        selected_articles: List[Article] = []
        total_minutes = 0

        for article in ordered_candidates:

            if len(selected_articles) >= rule["max_count"]:
                break

            if total_minutes + article.reading_time_min > rule["max_total_minutes"]:
                break

            selected_articles.append(article)
            total_minutes += article.reading_time_min

        return selected_articles


class RandomFitStrategy(RecommendationStrategy):
    """Randomized greedy selection.

    Candidates are shuffled and then greedily selected while respecting
    the limits. This adds diversity while remaining computationally cheap.
    """

    def select(self, candidates: List[Article], rule: Dict[str, int]) -> List[Article]:

        shuffled_candidates = candidates[:]
        random.shuffle(shuffled_candidates)

        selected_articles: List[Article] = []
        total_minutes = 0

        for article in shuffled_candidates:

            if len(selected_articles) >= rule["max_count"]:
                break

            if total_minutes + article.reading_time_min > rule["max_total_minutes"]:
                continue

            selected_articles.append(article)
            total_minutes += article.reading_time_min

        return selected_articles


class BoundedKnapsackStrategy(RecommendationStrategy):
    """Combination search on a bounded candidate subset.

    A random sample of candidates (default ≤10) is taken and all
    valid combinations within the constraints are evaluated.
    One valid combination is selected randomly.

    Useful when the candidate pool is small and exploration of
    combinations is desired without heavy computation.
    """

    def __init__(self, sample_size: int = 10):
        self.sample_size = sample_size

    def select(self, candidates: List[Article], rule: Dict[str, int]) -> List[Article]:

        if len(candidates) > self.sample_size:
            candidates = random.sample(candidates, self.sample_size)

        valid_combinations: List[List[Article]] = []

        for r in range(1, rule["max_count"] + 1):

            for combination in itertools.combinations(candidates, r):

                total_minutes = sum(
                    article.reading_time_min for article in combination
                )

                if total_minutes <= rule["max_total_minutes"]:
                    valid_combinations.append(list(combination))

        if not valid_combinations:
            return []

        return random.choice(valid_combinations)


class StochasticSamplingStrategy(RecommendationStrategy):
    """Randomized subset sampling strategy.

    Multiple randomized trials are performed. Each trial shuffles the
    candidates and greedily fills the selection under the constraints.
    One valid result from the sampled trials is chosen randomly.

    This approach scales well for larger candidate pools while still
    producing diverse combinations.
    """

    def __init__(self, trials: int = 80):
        self.trials = trials

    def select(self, candidates: List[Article], rule: Dict[str, int]) -> List[Article]:

        valid_combinations: List[List[Article]] = []

        for _ in range(self.trials):

            shuffled_candidates = candidates[:]
            random.shuffle(shuffled_candidates)

            selected_articles: List[Article] = []
            total_minutes = 0

            for article in shuffled_candidates:

                if len(selected_articles) >= rule["max_count"]:
                    break

                if total_minutes + article.reading_time_min > rule["max_total_minutes"]:
                    continue

                selected_articles.append(article)
                total_minutes += article.reading_time_min

            if selected_articles:
                valid_combinations.append(selected_articles)

        if not valid_combinations:
            return []

        return random.choice(valid_combinations)


STRATEGIES = {
    "greedy": GreedyStrategy(),
    "random_fit": RandomFitStrategy(),
    "bounded_knapsack": BoundedKnapsackStrategy(),
    "stochastic_sampling": StochasticSamplingStrategy(),
}