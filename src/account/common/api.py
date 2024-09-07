import json
import os.path
from pathlib import Path

import requests

from account.utils.constants import ACCESS_TOKEN


class Api:
    def __init__(self):
        self.url = "https://api.dashboard.mygate.com/graphql/"

    def post(self, fn_name: str, params: dict):
        # Define the headers (include any required authorization tokens)
        headers = {"Authorization": ACCESS_TOKEN}

        query = self.__gql_config(fn_name, "query")

        variables = self.__gql_config(fn_name, "var")
        variables = json.loads(variables)
        try:
            self.__update_variables(variables, params)
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
        else:
            print(
                f"Query failed with status code {response.status_code}: {response.text}"
            )

        return data

    def __update_variables(self, variables, params):
        for key, value in params.items():
            if isinstance(value, dict):
                self.__update_variables(variables[key], value)
            elif isinstance(value, list):
                if key == "values":
                    variables[key] = value
                else:
                    for list_val in value:
                        var_val = None
                        for var_tpl in variables[key]:
                            if list_val["name"] == var_tpl["name"]:
                                var_val = var_tpl
                                break

                        if var_val:
                            self.__update_variables(var_val, list_val)
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
