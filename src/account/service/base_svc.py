import re
from abc import ABC, abstractmethod

import pandas as pd

from account.utils.app_logger import AppLogger


class BaseSvc(ABC):
    def __init__(self, df: pd.DataFrame, params: dict):
        self.df = df
        self.params = params
        self.logger = AppLogger("BaseSvc")

    def get_cr_dr_rows(self, df, credit=True):
        col_list = [
            "Sl No",
            "House",
            "Mode",
            "Cheque No",
            "Bank Name",
            "Bank Branch",
            "Receipt Date",
            "Reference",
            "Description",
            "Receiving Account",
        ]
        col_nm = "Amount"
        if credit:
            col_nm = "Paying Amount"

        col_list.append(col_nm)
        df = df[col_list]

        cr_df = df.drop(df[df[col_nm] == ""].index)
        cr_df = cr_df.drop(cr_df[cr_df["Description"].str.contains("VIVISH")].index)
        cr_df = cr_df.reset_index(drop=True)

        self.logger.info(f"Manual Payments Rows: {len(cr_df)} | Credit: {credit}")
        return cr_df

    def parse_reference(self, row):
        desc = row["Description"]

        ref = None
        if desc.startswith("NEFT"):
            if "-" in desc:
                ref = desc.split("-")[1]
            else:
                ref = desc.split("/")[0]
        elif desc.startswith("UPI"):
            desc_split = desc.split("/")

            ref = desc_split[4]
            if not ref.isnumeric():
                ref = desc_split[1]
        elif desc.startswith("BIL"):
            ref = desc.split("/")[2]
        else:
            desc_split = desc.split("/")
            for splt in desc_split:
                if re.match("\\d+", splt):
                    ref = splt
                    break
                elif re.match("DF[\\d]+", splt):
                    ref = splt
                    break

        return ref

    def format_fields(self, cr_df, date_fields, floats, date_format="%d-%m-%y"):

        for field in date_fields:
            cr_df[field] = pd.to_datetime(cr_df[field])
            cr_df[field] = cr_df[field].dt.strftime(date_format)

        for field in floats:
            cr_df[field] = cr_df[field].str.replace(",", "")
            cr_df[field] = cr_df[field].astype(float)

    def write_to_csv(self, cr_df, file_nm):
        file_path = f"{self.params['base_path']}\\MyGate\\{file_nm}"
        cr_df.to_csv(file_path, index=False)
        self.logger.info(f"Template file exported: {file_nm}")

    @abstractmethod
    def process(self):
        """
        Method to process the service
        :return:
        """
