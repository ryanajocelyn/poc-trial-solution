import logging
import re
from datetime import date, datetime, timedelta

import camelot
import pandas as pd
import requests
from dotenv import load_dotenv

from account.common.api import Api
from account.utils.constants import FLAT_NOS, MAINT_PER_APT

load_dotenv()

logger = logging.getLogger("VOAM")
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


class Maintenance:
    def __init__(self, params):
        self.params = params
        self.pdf_path = f"{params['base_path']}\\Statement\\{params['stmt_nm']}"
        self.template_path = f"{params['base_path']}\\MyGate\\{params['tpl_nm']}"

    def run(self):
        logger.info("Maintenance Extraction started")
        logger.info(f"Base Path: {self.params['base_path']}")

        # Extract all tables from the statement
        df = self.extract_tables()

        # Process all debits
        self.process_debits(df)

        # Process all credits
        cr_df = self.process_credits(df)

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

    def process_credits(self, df):
        logger.info("Processing all credits.")
        cr_df = self.get_cr_dr_rows(df)
        cr_df["House"] = cr_df.apply(self.parse_house, axis=1)
        cr_df["Reference"] = cr_df.apply(self.parse_reference, axis=1)
        cr_df = self.handle_dual_house(cr_df, "903", "107A")
        cr_df = self.handle_dual_house(cr_df, "607", "608")
        self.format_fields(
            cr_df, date_fields=["Receipt Date"], floats=["Paying Amount"]
        )
        self.write_to_csv(cr_df, "dues_receipt.csv")
        return cr_df

    def write_to_csv(self, cr_df, file_nm):
        file_path = f"{self.params['base_path']}\\MyGate\\{file_nm}"
        cr_df.to_csv(file_path, index=False)
        logger.info(f"Template file exported: {file_nm}")

    def format_fields(self, cr_df, date_fields, floats, date_format="%d-%m-%y"):

        for field in date_fields:
            cr_df[field] = pd.to_datetime(cr_df[field])
            cr_df[field] = cr_df[field].dt.strftime(date_format)

        for field in floats:
            cr_df[field] = cr_df[field].str.replace(",", "")
            cr_df[field] = cr_df[field].astype(float)

    def process_debits(self, df):
        logger.info("Processing all Debits")
        dr_df = self.get_cr_dr_rows(df, credit=False)

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

    def create_book_expense_template(self, bk_exp_df):
        logger.info("Book Expense template creation started.")

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

        format = "%d-%m-%Y"
        due_date = datetime.strptime(due_date, format)
        due_date = due_date + timedelta(days=10)

        return due_date.strftime(format)

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

        logger.info(f"Manual Payments Rows: {len(cr_df)} | Credit: {credit}")
        return cr_df

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

    def extract_tables(self):
        tables = camelot.read_pdf(self.pdf_path, pages="all", lattice=True)

        table_df = [tbl.df for tbl in tables]
        df = pd.concat(table_df, ignore_index=True)

        cols = df.iloc[0].str.replace("\n", " ")
        df.columns = cols.to_list()

        df["House"] = None
        df["Mode"] = "EFT"
        df["Bank Name"] = None
        df["Bank Branch"] = None
        df["Reference"] = None
        df["Receiving Account"] = "ICICI Bank 1166"

        df = df.rename(
            columns={
                "Transaction Date": "Receipt Date",
                "Cheque no / Ref No": "Cheque No",
                "Deposit (Cr)": "Paying Amount",
                "Withdra wal (Dr)": "Amount",
                "Transaction Remarks": "Description",
            }
        )

        df = df.drop(index=[0])
        df["Description"] = df["Description"].str.replace("\n", "")

        logger.info(f"Tables Extracted: Rows = {len(df)}")
        return df

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

    def dues(self):
        api_param = {"requestData": {"pagination": {"page": 2}}}

        # Define the GraphQL query
        data = Api().post("dues", params=api_param)
        print(data)

    def test(self):
        txts = [
            "UPI/saraswathi.subr/UPI/State Bank OfI/424563916759/SBI8814422c7da24a5ab6fa83c38bf2957d",
            "UPI/divyasnmgn@okax/808Maintenance/AxisBankLtd/424836055511/AXIecab305f70294f91953e2b5344daa849",
            "UPI/karthic96@okici/307 Rajamani/KotakMahindra/461165571357/ICI9855014d35a34c978ccbfae57235b94e",
            "UPI/karthic96@okici/306 Rajamani/KotakMahindra/458087494394/ICI7399629d31394599937daad08b78c596",
            "UPI/421424514240/ From 504 Mainte/r.ganesh10@ okax/Axis Bank Ltd/AXI6a51e19459cf4fd9baa3eb1ba562633e",
            "NEFT-0811OP4139207675-SUBRAMANIYAMN-406 MONTHLY MAINTENANCE FEE-8826040000006712-DBSS0IN0811",
            "MMT/IMPS/421408320228/108 AugMainten/Lakshmanan/Federal Bank",
            "MMT/IMPS/421409707154/AUG24FLAT204/MADHUMITHA/Kotak Mahindra",
            "BIL/INFT/DH17399857/Flat701Aug2024/GOVINDARAJAN VA",
            "UPI/422195444374/Maintenance905/8072234138@ibl/Bank ofIndia/IBL251917a2a9554bc1b997bd5dd78a06ce",
        ]
        for txt in txts:
            row = {"Description": txt}
            house = self.parse_house(row)
            print(f"{house} === {txt}")


if __name__ == "__main__":
    params = {
        "base_path": "D:\\Abiz\\Flats\\Vedanshi\\2024-25\\06. Sep",
        "stmt_nm": "DetailedStatement-1.pdf",
        "tpl_nm": "batch_dues_receipt_upload_5223004_.csv",
    }
    maint = Maintenance(params=params)
    maint.run()
    # maint.dues()
    # maint.test()
