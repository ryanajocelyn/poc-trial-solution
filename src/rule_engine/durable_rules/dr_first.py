from durable.lang import ruleset, when_all, m, assert_fact, get_facts

# Dictionary to collect the final results
updated_facts = {}

# Define the ruleset
with ruleset("person"):

    # Rule 1: Derive new fact with status
    @when_all(m.age < 18)
    def derive_underage(c):
        merged = dict(c.m)
        merged["status"] = "underage"
        c.retract_fact(c.m)
        c.assert_fact(merged)

    @when_all(m.age >= 18)
    def derive_adult(c):
        merged = dict(c.m)
        merged["status"] = "adult"
        c.retract_fact(c.m)
        c.assert_fact(merged)

    # Rule 2: Capture inserted fact with status
    # @when_all((m.status == "underage") | (m.status == "adult"))
    # def collect_result(c):
    #     print(f"collect: {c.m.name}")
    #     updated_facts[c.m.name] = dict(c.m)


# Input facts
person1 = {"name": "Alice", "age": 16}
person2 = {"name": "Bob", "age": 25}

# Apply rules
assert_fact("person", person1)
assert_fact("person", person2)

facts = get_facts("person")
print(facts)
