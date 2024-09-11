import json
import re

import pandas as pd

from account.service.base_svc import BaseSvc
from account.utils.app_logger import AppLogger
from account.utils.constants import (
    FLAT_NOS,
    MAINT_PER_APT,
    BILL_PLAN_TPL_DROP_COLS,
    BILL_PLAN_TPL_COLS,
    RECEIPTS_ADVANCE_COLS,
)
from account.utils.utils import get_parent_dir


class CreditSvc(BaseSvc):
    def __init__(self, df: pd.DataFrame, params: dict):
        super().__init__(df, params)

        self.template_path = f"{params['base_path']}\\MyGate\\{params['tpl_nm']}"
        self.logger = AppLogger("CREDIT")

    def process(self):
        self.logger.info("Processing all credits.")
        cr_df = self.get_cr_dr_rows(self.df)
        cr_df["House"] = cr_df.apply(self.parse_house, axis=1)
        cr_df["Reference"] = cr_df.apply(self.parse_reference, axis=1)

        for house1, house2 in [("903", "107A"), ("607", "608")]:
            cr_df = self.handle_dual_house(cr_df, house1, house2)

        self.format_fields(
            cr_df, date_fields=["Receipt Date"], floats=["Paying Amount"]
        )

        self.write_to_csv(cr_df, "receipts_dues.csv")

        self.gen_bill_plan_template(cr_df)

    def parse_house(self, row):
        desc = row["Description"]
        if desc.startswith("UPI"):
            desc = desc.split("/")[2]

        regex = [
            {"pattern": "(.*)(/A\\d{3})(.*)", "index": 2},
            {"pattern": "(.*)(\\d{3})(.*)", "index": 2},
            {"pattern": "(.*)/[a-z]+(\\d{3})[a-z- /]+(.*)", "index": 2},
            {"pattern": "(.*)[- /a-z]+(\\d{3})[a-z- /]+(.*)", "index": 2},
            {"pattern": "(.*)[FLAT]+(\\d{3})[a-z- /]+(.*)", "index": 2},
        ]
        content = None
        for reg in regex:
            content = self.get_by_pattern(desc, reg)
            if content:
                break

        # Read the Flat and Owner name mappings
        name_mappings = self.get_flat_name_mappings()

        if not content:
            desc = row["Description"]
            for name, flat in name_mappings.items():
                if name in desc.upper():
                    content = flat
                    break

        if content == "106":
            content = "106 & 206"

        return f"Apt-{content}"

    def handle_dual_house(self, cr_df, house1, house2):
        two_house = cr_df[cr_df["House"] == f"Apt-{house1}"]
        if two_house.empty:
            self.logger.info("No Dual House Entry available. Skipping")
            return cr_df

        amt = two_house["Paying Amount"].iloc[0]
        amt = amt.replace(",", "")

        house_no = house2.replace("A", "")
        house_no = int(house_no[-1])
        two_dict = two_house.to_dict(orient="records")
        two_dict[0]["Paying Amount"] = str(MAINT_PER_APT[house_no])
        two_dict[0]["House"] = f"Apt-{house2}"

        two_pd = pd.DataFrame(two_dict)
        row_idx = int(two_house.index.values[0])

        cr_df.iloc[row_idx, 10] = str(float(amt) - MAINT_PER_APT[house_no])
        cr_df = pd.concat([cr_df, two_pd], ignore_index=True)
        cr_df = cr_df.reset_index(drop=True)

        return cr_df

    def gen_bill_plan_template(self, cr_df):
        # Create the template export by bill plan
        tpl_df = pd.read_csv(self.template_path)

        # Drop columns that exist in the statement rows
        tpl_df = tpl_df.drop(columns=BILL_PLAN_TPL_DROP_COLS)
        tpl_df = pd.merge(tpl_df, cr_df, on="House", how="left")

        self.write_bill_plan_receipts(tpl_df)

        self.write_advance_receipts(tpl_df)

    def write_advance_receipts(self, tpl_df):
        advanced_df = tpl_df[tpl_df["Paying Amount"] > tpl_df["Total Invoice Amount"]]
        advanced_df = advanced_df.reset_index(drop=True)
        advanced_df.rename(
            columns={
                "Cheque No": "Cheque number",
                "Bank Name": "Bank name",
                "Bank Branch": "Bank branch",
                "Receipt Date": "Receipt Date(dd-mm-yy)",
            },
            inplace=True,
        )
        advanced_df["Advance Receiving Amount"] = (
            advanced_df["Paying Amount"] - advanced_df["Total Invoice Amount"]
        )

        advanced_df = advanced_df[RECEIPTS_ADVANCE_COLS]
        self.write_to_csv(advanced_df, "receipts_advance.csv")
        self.logger.info("Advance Receipts generated successfully.")

    def write_bill_plan_receipts(self, tpl_df):
        bill_pln_df = tpl_df[BILL_PLAN_TPL_COLS].copy()
        bill_pln_df["Paying Amount"] = bill_pln_df.apply(
            self.set_bill_plan_paying_amt, axis=1
        )
        self.write_to_csv(bill_pln_df, "receipts_bill_plan.csv")

    def set_bill_plan_paying_amt(self, row):
        paying_amt = row["Paying Amount"]
        invoice_amt = row["Total Invoice Amount"]

        if paying_amt > invoice_amt:
            return invoice_amt

        return paying_amt

    def get_by_pattern(self, desc, reg):
        content = None
        pattern = re.compile(reg["pattern"], flags=re.IGNORECASE)
        match = pattern.match(desc)
        if match:
            content = match.group(reg["index"])
            content = content.replace("/A", "")
            if content not in FLAT_NOS:
                content = None

        return content

    def get_flat_name_mappings(self):
        parent_dir = get_parent_dir(__file__)
        name_file = f"{parent_dir}\\config\\flat_name_mappings.json"
        with open(name_file, "r", encoding="utf-8") as nf:
            name_mappings = json.loads(nf.read())
        return name_mappings
