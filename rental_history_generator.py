#!/usr/bin/env python3

###
# Generates a series of rental applications for a given user
#
###

from collections import defaultdict
from enum import Enum

import argparse
import random
import json
import csv
import sys


def load_file(filename):
    with open(filename, "rt") as f:
        reader = csv.DictReader(f)
        data = list(reader)

    return data


class ApplicationStatus(Enum):
    # User has submitted their application for rental of a property
    Submitted = "S"

    # Users application has been approved
    Approved = "A"

    # Users application was unsuccessful
    Ignored = "I"

    # Users agreed application was terminated by either party
    Terminated = "T"


class RentalHistoryGenerator(object):
    def __init__(self, properties, start=0):
        self.properties = properties
        self.application_id = start

        self.user_property_applications = defaultdict(list)

    def next_application_id(self):
        self.application_id += 1
        return self.application_id

    def next_property_choice(self, user):
        user_id = user["id"]

        if len(self.user_property_applications[user_id]) >= len(self.properties):
            return None

        # Find a property the user hasn't applied for yet
        chosen_property = random.choice(self.properties)

        while chosen_property["id"] in self.user_property_applications[user_id]:
            chosen_property = random.choice(self.properties)

        # Add that property to the list the users now applied for
        self.user_property_applications[user_id].append(chosen_property["id"])

        return chosen_property

    def generate(self, user, max_history=4, success_chance=0.70):
        applications = []
        properties_applied_for = []

        # Pick the number of properties the user has lived in (their rental history)
        for i in range(0, random.choice(range(0, max_history))):
            # Default status of application history
            status = ApplicationStatus.Ignored

            # Pick the number of applications a user will submit for a given 'period' they are looking
            # Once 'successful' that last property will end their 'round of looking'
            while status != ApplicationStatus.Approved:
                if random.random() < success_chance:
                    status = ApplicationStatus.Approved

                application = {
                   "application_id": self.next_application_id(),
                   "status": status,
                   "property": self.next_property_choice(user),
                }

                applications.append(application)

        return applications


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--users", required=True)
    parser.add_argument("--properties", required=True)

    args = parser.parse_args()

    users = load_file(args.users)
    properties = load_file(args.properties)

    print(properties)
    generator = RentalHistoryGenerator(properties)

    for user in users:
        user["rental_history"] = generator.generate(user)
        print(user)

if __name__ == "__main__":
    main()
