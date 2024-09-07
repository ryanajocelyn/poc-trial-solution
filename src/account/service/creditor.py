import re

import pandas as pd

from account.service.base_svc import BaseSvc
from account.utils.app_logger import AppLogger
from account.utils.constants import FLAT_NOS, MAINT_PER_APT


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
        cr_df = self.handle_dual_house(cr_df, "903", "107A")
        cr_df = self.handle_dual_house(cr_df, "607", "608")
        self.format_fields(
            cr_df, date_fields=["Receipt Date"], floats=["Paying Amount"]
        )
        self.write_to_csv(cr_df, "dues_receipt.csv")

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

        name_mappings = {
            "KIDIYURVIN": 207,
            "SARASWATHI.SUBR": 208,
            "KALPANAMAJUMDER": 703,
            "GEETA IYER HARI": 706,
            "GEETA HARIHARAN": 706,
            "AANANDALAXMI M": 404,
            "NEDUMARANTHANGAMANI": 904,
            "VENKATARAGHAVAN": 308,
            "R GANESH": 504,
            "PRASANNAL": 507,
            "VIDYA SAGAR": 407,
            "KYOYEON": 408,
            "N MESIAH": 505,
            "A V M FUELS": 607,
            "RAJAMANI": 307,
            "RASIK": 905,
            "INSTORE": "Instore",
        }

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
        tpl_df = tpl_df.drop(
            columns=[
                "Paying Amount",
                "Receipt Date",
                "Mode",
                "Cheque No",
                "Bank Name",
                "Bank Branch",
                "Receiving Account",
                "Reference",
                "Description",
            ]
        )
        merged_df = pd.merge(tpl_df, cr_df, on="House", how="left")
        merged_df = merged_df[
            [
                "Batch",
                "Date",
                "Due Date",
                "House",
                "Charge Id",
                "Item Description",
                "Charge Account",
                "Balance",
                "Paying Amount",
                "Total Invoice Amount",
                "Receipt Date",
                "Excess Amount",
                "Mode",
                "Cheque No",
                "Bank Name",
                "Bank Branch",
                "Receiving Account",
                "Reference",
                "Description",
            ]
        ]
        self.write_to_csv(merged_df, "bill_plan_receipts.csv")

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
