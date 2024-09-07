from datetime import datetime, timedelta

from pandas import DataFrame

from account.service.base_svc import BaseSvc
from account.utils.app_logger import AppLogger


class DebitSvc(BaseSvc):
    def __init__(self, df: DataFrame, params: dict):
        super().__init__(df, params)

        self.logger = AppLogger("DEBIT")

    def process(self):
        self.logger.info("Processing all Debits")
        dr_df = self.get_cr_dr_rows(self.df, credit=False)

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

        dr_df["Reference"] = dr_df.apply(self.parse_reference, axis=1)
        dr_df[["Party", "Expense Account", "Department"]] = dr_df.apply(
            self.parse_debit_ac, axis=1
        ).to_list()

        self.format_fields(
            dr_df,
            date_fields=["Date(dd-mm-yyyy)"],
            floats=["Amount"],
            date_format="%d-%m-%Y",
        )

        bk_exp_df = dr_df[dr_df["Party"].isnull()].copy()
        bk_exp_df = bk_exp_df.reset_index(drop=True)
        if not bk_exp_df.empty:
            self.create_book_expense_template(bk_exp_df)

        dr_df = dr_df.drop(dr_df[dr_df["Party"].isnull()].index)

        self.write_to_csv(dr_df, "payments.csv")

    def parse_debit_ac(self, row):
        desc = row["Description"]
        party, exp_acc, dept = None, None, None

        if "FAHAD" in desc:
            party = "Manager Salary"
            exp_acc = "Manager"
            dept = "Accounts"
        elif "SURULIAMMAL" in desc or "RANI" in desc or "BANU" in desc:
            person = desc.split("/")[-1]
            party = f"Housekeeping Staff Salary - {person.capitalize()}"
            exp_acc = "Personnel - Housekeeping"
            dept = "House Keeping"
        elif "SURENDARPLUMBER" in desc:
            reason = desc.split("/")[-2]
            party = f"Plumbing Expenses - {reason}"
            exp_acc = "Personnel - Plumber"
            dept = "Common Area"
        elif "KDLE" in desc:
            party = desc.split("/")[-2]
            exp_acc = "Consumables - House Keeping"
            dept = "House Keeping"
        elif "TREASURER" in desc:
            desc_split = desc.split("/")[-2]
            party = f"Maintenance - {desc_split}"
            exp_acc = "Consumables - Security / Office"
            dept = "Common Area"
        elif "DGAUTOMATION" in desc:
            desc_split = desc.split("/")[-2]
            party = f"DG - {desc_split}"
            exp_acc = "Consumables - Generator"
            dept = "Common Area"

        return party, exp_acc, dept

    def set_expense_ac(self, row):
        desc = row["Description"]

        vendor, item_nm, dept, purchase_ac = None, None, None, None
        if "MDARAFATH" in desc:
            vendor = "ACare Security Services"
            item_nm = "Security Expenses"
            dept = "Security"
            purchase_ac = "Security"
        elif "CHENNAI ME" in desc or "CWSS" in desc:
            vendor = "Metro Water Corporation"
            item_nm = "Metro Water Expenses"
            dept = "Common Area"
            purchase_ac = "Metro Water"
        elif "BBPS" in desc:
            vendor = "TANGEDCO Electricity"
            item_nm = "Electricity Expenses"
            dept = "Electrical"
            purchase_ac = "TNEB"
        elif "BIGBIN" in desc:
            vendor = "Big Bin Garbage"
            item_nm = "Garbage Collection Expenses"
            dept = "Common Area"
            purchase_ac = "Corporation Garbage Cleaning"

        return vendor, item_nm, dept, purchase_ac

    def create_book_expense_template(self, bk_exp_df):
        self.logger.info("Book Expense template creation started.")

        bk_exp_df["Delivery Date(dd-mm-yyyy)"] = bk_exp_df["Date(dd-mm-yyyy)"]
        bk_exp_df["Expense Creation Date(dd-mm-yyyy)"] = bk_exp_df["Date(dd-mm-yyyy)"]
        bk_exp_df["Bill Date(dd-mm-yyyy)"] = bk_exp_df["Date(dd-mm-yyyy)"]
        bk_exp_df["Due Date(dd-mm-yyyy)"] = bk_exp_df.apply(self.set_due_date, axis=1)

        bk_exp_df["Deduction Amount"] = None
        bk_exp_df["Reason for deduction"] = None
        bk_exp_df["Bill Number"] = None
        bk_exp_df["IGST Amount"] = None
        bk_exp_df["TDS Amount"] = None

        bk_exp_df[["Amount", "SGST Amount", "CGST Amount"]] = bk_exp_df.apply(
            self.set_gst_amt, axis=1
        ).to_list()
        bk_exp_df[["Vendor", "Item name", "Departments", "Purchase Account"]] = (
            bk_exp_df.apply(self.set_expense_ac, axis=1).to_list()
        )
        bk_exp_df["Sl No"] = 1

        for idx, row in bk_exp_df.iterrows():
            bk_exp_df.at[idx, "Sl No"] = idx

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

        self.write_to_csv(bk_exp_df, "bk_expenses.csv")

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
