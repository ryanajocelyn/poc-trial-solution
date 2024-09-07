import math
from datetime import datetime

import camelot
import pandas as pd
from dotenv import load_dotenv

from account.common.api import Api
from account.common.write_excel import XlsWriter
from account.service.creditor import CreditSvc
from account.service.debitor import DebitSvc
from account.utils.app_logger import AppLogger

load_dotenv()


class Maintenance:
    def __init__(self, params):
        self.params = params
        self.pdf_path = f"{params['base_path']}\\Statement\\{params['stmt_nm']}"
        self.logger = AppLogger("VOAM")

    def run(self):
        self.logger.info("Maintenance Extraction started")
        self.logger.info(f"Base Path: {self.params['base_path']}")

        # Extract all tables from the statement
        df = self.extract_tables()

        # Process all debits
        debit_svc = DebitSvc(df, self.params)
        debit_svc.process()

        # Process all credits
        credit_svc = CreditSvc(df, self.params)
        credit_svc.process()

        self.dues()

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

        self.logger.info(f"Tables Extracted: Rows = {len(df)}")
        return df

    def dues(self):
        dues_list = []
        headers = {}
        curr_date = int(datetime.now().timestamp())
        for page in range(1, 4):
            api_param = {
                "requestData": {
                    "pagination": {"page": page},
                    "conditions": [
                        {
                            "name": "till_date",
                            "operation": "lte",
                            "values": [curr_date],
                        }
                    ],
                }
            }

            # Define the GraphQL query
            data = Api().post("dues", params=api_param)
            data_resp = data["data"]["getDuesReportList"]["dataResponse"]
            report_header = data_resp["reportHeaders"]
            headers = {head["accessor"]: head["header"] for head in report_header}
            dues_list.extend(data_resp["data"])

        full_dues_df = pd.DataFrame(dues_list)
        full_dues_df.rename(columns=headers, inplace=True)

        dues_df = full_dues_df[full_dues_df["Total Dues"] > 0]
        dues_df = dues_df.reset_index(drop=True)

        dues_df["Maintenance Charge"] = dues_df.apply(self.combine_maint, axis=1)

        dues_df = dues_df[
            [
                "Unit",
                "Owner Name",
                "Maintenance Charge",
                "Metro Water - 2020",
                "Late Payment Fine",
                "Move in/out - Incidental Charges",
                "Total Dues",
            ]
        ]

        XlsWriter(self.params["base_path"]).write(dues_df)
        self.logger.info("Dues report generated successfully.")

    def combine_maint(self, row):
        maint = row["Maintenance Charge"]
        instore = row["Maintenance - Instore"]
        if not math.isnan(instore):
            maint = (
                row["Maintenance - Instore"] + row["CGST Output"] + row["SGST Output"]
            )

        return maint

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
    m_params = {
        "base_path": "D:\\Abiz\\Flats\\Vedanshi\\2024-25\\06. Sep",
        "stmt_nm": "DetailedStatement-1.pdf",
        "tpl_nm": "batch_dues_receipt_upload_5223004_.csv",
    }
    maint = Maintenance(params=m_params)
    maint.run()
    # maint.test()
