import math
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from transformers import pipeline

from account.common.api import Api
from account.common.base import Base
from account.service.creditor import CreditSvc
from account.service.debitor import DebitSvc
from account.utils.app_logger import AppLogger
from account.writer.write_excel import XlsWriter
from account.writer.write_pdf import PdfWriter

load_dotenv()


class Maintenance(Base):
    def __init__(self, params):
        super().__init__()

        self.params = params
        self.pdf_path = f"{params['base_path']}\\Statement\\{params['stmt_nm']}"
        self.logger = AppLogger("VOAM")

    def run(self):
        self.logger.info("Maintenance Extraction started")
        self.logger.info(f"Base Path: {self.params['base_path']}")

        # Extract all tables from the statement
        df = self.extract_statement()

        # Process all debits
        debit_svc = DebitSvc(df, self.params)
        debit_svc.process()

        # Process all credits
        credit_svc = CreditSvc(df, self.params)
        credit_svc.process()

        self.dues()

    def extract_statement(self):
        df = self.parse_statement(self.pdf_path)

        if self.params.get("ner", False):
            remarks = df["Description"].to_list()
            flats = self.identify_entities(remarks)
            df["House"] = flats

        recon_df = df.copy()
        recon_df["Amount"] = recon_df["Amount"].str.replace(",", "")
        recon_df["Paying Amount"] = recon_df["Paying Amount"].str.replace(",", "")
        recon_df["TransactionPostedDate"] = pd.to_datetime(
            recon_df["TransactionPostedDate"], format="%d/%m/%Y%H:%M:%S %p"
        ).dt.strftime("%d/%m/%Y")

        recon_df.rename(
            columns={
                "TransactionPostedDate": "Transaction Date",
                "Amount": "Withdrawal",
                "Paying Amount": "Deposit",
            },
            inplace=True,
        )

        credit_svc = CreditSvc(pd.DataFrame(), self.params)
        credit_svc.write_to_csv(recon_df, "reconcilation.csv", header=False, index="06")

        start_row = self.params.get("start_row", 0)
        if start_row > 0:
            df["Sl No"] = df["Sl No"].astype(int)
            df = df[df["Sl No"] >= start_row]
            df = df.reset_index(drop=True)

        self.logger.info(f"Tables Extracted after Filter: Rows = {len(df)}")
        return df

    def identify_entities(self, remarks):
        model_output_checkpoint = "D:\\Abiz\\Technical\\code\\python\\poc-trial-solution\\src\\ai\\ner\\transformers\\nfl_pbp_token_classifier"
        classifier = pipeline(
            "ner", model=model_output_checkpoint, aggregation_strategy="simple"
        )
        responses = classifier(remarks)
        flats = []
        ents = []
        for ind, row in enumerate(responses):
            ents_row = []
            flat = None
            for ent in row:
                if ent["entity_group"] == "FLAT":
                    flat = f"Apt-{ent['word']}"

                ents_row.append({ent["entity_group"]: ent["word"]})

            print(flat, remarks[ind], ents_row)
            flats.append(flat)
            ents.append(ents_row)
        print(ents)
        return flats

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
            if not data_resp:
                raise ValueError("API Key not set")

            report_header = data_resp["reportHeaders"]
            tmp_headers = {head["accessor"]: head["header"] for head in report_header}
            headers.update(tmp_headers)
            dues_list.extend(data_resp["data"])

        full_dues_df = pd.DataFrame(dues_list)
        full_dues_df.rename(columns=headers, inplace=True)

        dues_df = full_dues_df[full_dues_df["Total Dues"] > 0]
        dues_df = dues_df.reset_index(drop=True)

        dues_df["Maintenance Charge"] = dues_df.apply(self.combine_maint, axis=1)

        dues_cols = [
            "Unit",
            "Owner Name",
            "Maintenance Charge",
            "Metro Water - 2020",
            "Late Payment Fine",
            "Move in/out - Incidental Charges",
            "Total Dues",
        ]

        dues_df = dues_df[dues_cols]

        dues_path = self.params["base_path"]
        dues_path = f"{dues_path}\\Dues"
        xls_path = XlsWriter(dues_path).write(dues_df, "dues.xlsx")

        cur_date = datetime.now().strftime("%b_%d")
        PdfWriter(dues_path).write(xls_path, f"dues_{cur_date}.pdf")

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
        credit_svc = CreditSvc(pd.DataFrame(), self.params)
        for txt in txts:
            row = {"Description": txt}
            house = credit_svc.parse_house(row)
            print(f"{house} === {txt}")


if __name__ == "__main__":
    # Start Row - Row to start from
    m_params = {
        "base_path": "D:\\Abiz\\Flats\\Vedanshi\\2025-26\\02. May",
        "stmt_nm": "DetailedStatement-1.pdf",
        "tpl_nm": "batch_dues_receipt_upload_6288477_.csv",
        "start_row": 0,
        "ner": False,
    }
    maint = Maintenance(params=m_params)
    maint.run()
    # maint.test()

    remarks = [
        "INF/INFT/037461885331/A8032736ad15fb5ba3a94a8eae0844906c/VIVISHTECHNOLO"
    ]
    # maint.identify_entities(remarks)
