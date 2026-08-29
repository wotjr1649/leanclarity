"""Summary statistics. Stdlib only."""


def mean(values):
    values = list(values)
    if not values:
        raise ValueError("mean of an empty sequence")
    return sum(values) / len(values)
