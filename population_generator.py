#!/usr/bin/env python3

###
# Generates a population based on a series of attributes and their universal estimates
#
###

import argparse
import json
import sys

from collections import defaultdict


def load_estimates(filename):
    with open(filename, "rt") as f:
        estimates = json.load(f)

    counters = defaultdict(dict)

    for demographic, attributes in estimates.items():
        counters[demographic]["total"] = 0

        for attribute in attributes:
            counters[demographic][attribute] = 0

    return estimates, counters


def decide_on_attribute(attributes, counters, user):
    biggest_gap = 0
    biggest_gap_name = None

    for attribute in counters:
        if attribute == "total":
            # Skip the meta attribute
            continue

        if biggest_gap_name is None:
            biggest_gap_name = attribute

        if counters["total"] == 0:
            current_percentage = 0.0
        else:
            current_percentage = counters[attribute] / counters["total"]

        if type(attributes[attribute]) is dict:
            # We depend on another attribute
            depends_on_attribute = list(attributes[attribute].keys())[0]
            users_value = user[depends_on_attribute]

            linked_percentages = attributes[attribute][depends_on_attribute]

            if users_value in linked_percentages:
                desired_percentage = linked_percentages[users_value]
            else:
                desired_percentage = linked_percentages[""]
        else:
            desired_percentage = attributes[attribute]

        gap = desired_percentage - current_percentage

        if gap >= biggest_gap:
            biggest_gap = gap
            biggest_gap_name = attribute

    return biggest_gap_name


def generate_population(estimates, counts, size):
    users = []

    # Calculate demographic generation order
    links = set()
    for demographic, attributes in estimates.items():
        for attribute in attributes.values():
            if type(attribute) is dict:
                links.add((demographic, list(attribute.keys())[0]))

    order = list(estimates.keys())

    for item, depends_on in links:
        item_index = order.index(item)
        depends_on_index = order.index(depends_on)

        if item_index < depends_on_index:
            order.insert(item_index, order.pop(order.index(depends_on)))

    # Generate users
    for i in range(size):
        user = {"id": i + 1}

        # Generate demographics for a user
        for demographic in order:
            attribute = decide_on_attribute(estimates[demographic], counts[demographic], user)

            if attribute is None:
                print(user)
                print(demographic)
                print(attribute)
            counts[demographic][attribute] += 1
            counts[demographic]["total"] += 1
            user[demographic] = attribute

        users.append(user)

    return users


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--estimates", required=True)
    parser.add_argument("--population-size", type=int, required=True)

    args = parser.parse_args()

    estimates, counters = load_estimates(args.estimates)
    population = generate_population(estimates, counters, args.population_size)

    import csv
    writer = csv.DictWriter(sys.stdout, fieldnames=population[0].keys())
    writer.writeheader()

    for user in population:
        writer.writerow(user)

if __name__ == "__main__":
    main()
