import json
import os.path
from pathlib import Path

import requests


class Api:
    def __init__(self):
        self.url = "https://api.dashboard.mygate.com/graphql/"

    def post(self, fn_name: str, params: dict):
        # Define the headers (include any required authorization tokens)
        headers = {
            "Authorization": "w5r5YaQN8hXvi7PGuZUChPC9PlmGGXfXgWOVoWzeyBZ1n5Po1KNbINdeQEjHZLQT"
        }

        query = self.__gql_config(fn_name, "query")
        print(query)

        variables = self.__gql_config(fn_name, "var")
        variables = json.loads(variables)
        try:
            self.__update_variables(variables, params)
            print(variables)
        except Exception as e:
            print(e)

        # Send the request
        response = requests.post(
            self.url, json={"query": query, "variables": variables}, headers=headers
        )

        data = None
        # Check for errors
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            print(data)
        else:
            print(
                f"Query failed with status code {response.status_code}: {response.text}"
            )

        return data

    def __update_variables(self, variables, params):
        for key, value in params.items():
            if isinstance(value, dict):
                self.__update_variables(variables[key], value)
            else:
                variables[key] = value

    def __gql_config(self, fn_name, fn_type):
        current_dir = Path(__file__).resolve().parent
        parent_dir = current_dir.parent

        if fn_type == "query":
            file_nm = f"qry_{fn_name}.graphql"
        else:
            file_nm = f"var_{fn_name}.json"

        file_path = os.path.join(parent_dir, "config", file_nm)
        with open(file_path, "r", encoding="utf-8") as f_qry:
            query = f_qry.read()

        return query
