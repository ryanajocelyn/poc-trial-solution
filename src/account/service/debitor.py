from datetime import datetime, timedelta
from functools import partial

import pandas as pd
from pandas import DataFrame

from account.service.base_svc import BaseSvc
from account.utils.app_logger import AppLogger
from account.utils.utils import get_vendor_expenses, get_general_expenses


class DebitSvc(BaseSvc):
    def __init__(self, df: DataFrame, params: dict):
        super().__init__(df, params)

        self.logger = AppLogger("DEBIT")

    def process(self):
        self.logger.info("Processing all Debits")
        dr_df = self.get_cr_dr_rows(self.df, credit=False)
        if dr_df.empty:
            self.logger.info("No Debits found. Skipping.")
            return

        dr_df["Reference"] = dr_df.apply(self.parse_reference, axis=1)
        dr_df = self.process_cash_bank(dr_df)

        dr_df = dr_df.rename(
            columns={
                "Receipt Date": "Date(dd-mm-yyyy)",
                "Receiving Account": "Paying Account",
                "Cheque No": "Cheque no.",
            }
        )

        dr_df["Party"] = None
        dr_df["Expense Account"] = None
        dr_df["Department"] = None
        dr_df["Cheque date(dd-mm-yyyy)"] = None

        dr_df = dr_df[
            [
                "Date(dd-mm-yyyy)",
                "Party",
                "Expense Account",
                "Paying Account",
                "Cheque no.",
                "Cheque date(dd-mm-yyyy)",
                "Department",
                "Reference",
                "Description",
                "Amount",
            ]
        ]

        gen_expense = get_general_expenses()
        gen_debit_fn = partial(self.parse_debit_ac, gen_expense=gen_expense)
        dr_df[["Party", "Expense Account", "Department"]] = dr_df.apply(
            gen_debit_fn, axis=1
        ).to_list()

        self.format_fields(
            dr_df,
            date_fields=["Date(dd-mm-yyyy)"],
            floats=["Amount"],
            date_format="%d-%m-%Y",
        )

        dr_df = self.create_book_expense_template(dr_df)

        dr_df = dr_df.drop(dr_df[dr_df["Party"].isnull()].index)
        dr_df = dr_df[
            [
                "Date(dd-mm-yyyy)",
                "Party",
                "Expense Account",
                "Paying Account",
                "Cheque no.",
                "Cheque date(dd-mm-yyyy)",
                "Department",
                "Reference",
                "Description",
                "Amount",
            ]
        ]

        self.write_to_csv(dr_df, "general_payments.csv", index="04")

    def process_cash_bank(self, dr_df):
        cb_df = dr_df[dr_df["Description"].str.contains("TREASURER")]
        cb_df["To Account"] = "Cash"
        cb_df["Cheque Date"] = None
        cb_df = cb_df[
            [
                "Sl No",
                "Receipt Date",
                "Receiving Account",
                "To Account",
                "Reference",
                "Cheque No",
                "Cheque Date",
                "Amount",
                "Description",
            ]
        ]
        cb_df.rename(
            columns={
                "Sl No": "row",
                "Receipt Date": "Date",
                "Receiving Account": "From Account",
                "Cheque No": "Cheque Number",
            },
            inplace=True,
        )
        self.format_fields(
            cb_df,
            date_fields=["Date"],
            floats=["Amount"],
            date_format="%d-%m-%Y",
        )

        self.write_to_csv(cb_df, "cash_bank_transfer.csv", index="07")

        dr_df = dr_df[~dr_df["Description"].str.contains("TREASURER")]
        return dr_df

    def parse_debit_ac(self, row, gen_expense):
        desc = row["Description"]
        party, exp_acc, dept = None, None, None

        general_exp = None
        for exp in gen_expense:
            exp_items = exp["vendor_type"]
            for item in exp_items:
                if item in desc:
                    general_exp = exp
                    break

            if general_exp:
                break

        if general_exp:
            exp_desc = desc.split("/")[general_exp["counter"]]

            party = f'{general_exp["vendor"]} - {exp_desc.capitalize()}'
            dept = general_exp["dept"]
            exp_acc = general_exp["purchase_ac"]

        return party, exp_acc, dept

    def set_expense_ac(self, vendor_exps, row):
        desc = row["Description"]

        vendor_exp = None
        for exp in vendor_exps:
            exp_items = exp["vendor_type"]
            for item in exp_items:
                if item in desc:
                    vendor_exp = exp
                    break

            if vendor_exp:
                break

        party = desc.split("/")[-2]
        amount, sgst, cgst = row["Amount"], 0, 0
        vendor, item_nm, dept, purchase_ac = None, None, None, None
        if vendor_exp:
            vendor = vendor_exp["vendor"]
            item_nm = vendor_exp["item_nm"]
            dept = vendor_exp["dept"]
            purchase_ac = vendor_exp["purchase_ac"]

            if vendor_exp.get("gst", True):
                amount, sgst, cgst = self.set_gst_amt(row)

        return party, vendor, item_nm, dept, purchase_ac, amount, sgst, cgst

    def create_book_expense_template(self, dr_df):
        self.logger.info("Book Expense template creation started.")

        dr_df["Delivery Date(dd-mm-yyyy)"] = dr_df["Date(dd-mm-yyyy)"]
        dr_df["Expense Creation Date(dd-mm-yyyy)"] = dr_df["Date(dd-mm-yyyy)"]
        dr_df["Bill Date(dd-mm-yyyy)"] = dr_df["Date(dd-mm-yyyy)"]
        dr_df["Due Date(dd-mm-yyyy)"] = dr_df.apply(self.set_due_date, axis=1)

        dr_df["Deduction Amount"] = None
        dr_df["Reason for deduction"] = None
        dr_df["Bill Number"] = None
        dr_df["IGST Amount"] = None
        dr_df["TDS Amount"] = None
        dr_df["Total Amount"] = dr_df["Amount"]

        vendor_exp = get_vendor_expenses()
        expenses_fn = partial(self.set_expense_ac, vendor_exp)

        cols = [
            "Party",
            "Vendor",
            "Item name",
            "Departments",
            "Purchase Account",
            "Amount",
            "SGST Amount",
            "CGST Amount",
        ]
        dr_df[cols] = dr_df.apply(expenses_fn, axis=1).to_list()
        dr_df["Sl No"] = 1

        for idx, row in dr_df.iterrows():
            dr_df.at[idx, "Sl No"] = idx

        bk_exp_df = dr_df[~dr_df["Vendor"].isnull()].copy()
        bk_exp_df = bk_exp_df.reset_index(drop=True)
        bk_exp_df = bk_exp_df[
            [
                "Sl No",
                "Delivery Date(dd-mm-yyyy)",
                "Expense Creation Date(dd-mm-yyyy)",
                "Due Date(dd-mm-yyyy)",
                "Vendor",
                "Purchase Account",
                "Deduction Amount",
                "Reason for deduction",
                "Bill Number",
                "Bill Date(dd-mm-yyyy)",
                "Departments",
                "Description",
                "Amount",
                "SGST Amount",
                "CGST Amount",
                "IGST Amount",
                "TDS Amount",
                "Item name",
            ]
        ]

        final_exps = {}
        exp_list = bk_exp_df.to_dict(orient="records")
        for exp in exp_list:
            con_exp = final_exps.get(exp["Vendor"])
            if not con_exp:
                con_exp = exp
                final_exps[exp["Vendor"]] = con_exp
            else:
                con_exp["Amount"] = con_exp["Amount"] + exp["Amount"]
                con_exp["SGST Amount"] = con_exp["SGST Amount"] + exp["SGST Amount"]
                con_exp["CGST Amount"] = con_exp["CGST Amount"] + exp["CGST Amount"]

                if exp["IGST Amount"]:
                    con_exp["IGST Amount"] = con_exp["IGST Amount"] + exp["IGST Amount"]

                if exp["TDS Amount"]:
                    con_exp["TDS Amount"] = con_exp["TDS Amount"] + exp["TDS Amount"]

        bk_exp_df = pd.DataFrame(list(final_exps.values()))
        bk_exp_df.reset_index(inplace=True, drop=True)
        self.write_to_csv(bk_exp_df, "vendor_expense.csv", index="05")

        dr_df = dr_df[dr_df["Vendor"].isnull()].copy()
        dr_df["Amount"] = dr_df["Total Amount"]
        return dr_df

    def set_gst_amt(self, row):
        amt = row["Amount"]

        base_amt = (amt * 100) / 118
        gst = amt - base_amt
        sgst = gst / 2
        cgst = gst - sgst

        desc = row["Description"]
        if "BBPS" in desc or "MDARAFATH" in desc:
            return amt, 0, 0

        return base_amt, sgst, cgst

    def set_due_date(self, row):
        due_date = row["Date(dd-mm-yyyy)"]

        fmt = "%d-%m-%Y"
        due_date = datetime.strptime(due_date, fmt)
        due_date = due_date + timedelta(days=10)

        return due_date.strftime(fmt)
