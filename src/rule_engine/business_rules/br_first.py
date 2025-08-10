import pprint
from typing import Optional

import pandas as pd
from business_rules.actions import BaseActions, rule_action
from business_rules.engine import run_all
from business_rules.fields import FIELD_TEXT
from business_rules.variables import BaseVariables, numeric_rule_variable
from pydantic import BaseModel


# Input object
class Person(BaseModel):
    name: str
    age: int
    status: Optional[str] | None = None  # To be set by rule


# Variables that can be used in rules
class PersonVariables(BaseVariables):
    def __init__(self, person):
        self.person = person

    @numeric_rule_variable
    def age(self):
        return self.person.age


# Actions to take when rules fire
class PersonActions(BaseActions):
    def __init__(self, person):
        self.person = person

    @rule_action(params={"status": FIELD_TEXT})
    def set_status(self, status):
        self.person.status = status


# Define rules
rules = [
    {
        "conditions": {"all": [{"name": "age", "operator": "less_than", "value": 18}]},
        "actions": [{"name": "set_status", "params": {"status": "underage"}}],
    },
    {
        "conditions": {
            "all": [
                {"name": "age", "operator": "greater_than_or_equal_to", "value": 18}
            ]
        },
        "actions": [{"name": "set_status", "params": {"status": "adult"}}],
    },
]


def assert_fact(row):
    per = Person(**row)
    run_all(
        rule_list=rules,
        defined_variables=PersonVariables(per),
        defined_actions=PersonActions(per),
        stop_on_first_trigger=False,
    )
    pprint.pprint(vars(per))


df = pd.DataFrame(
    [
        {"name": "Alice", "age": 16},
        {"name": "Bob", "age": 25},
        {"name": "Charlie", "age": 18},
    ]
)

print("\nRules on Dataframe:")
df.apply(assert_fact, axis=1)
