import camelot
import pandas as pd
import pdfplumber

from account.utils.app_logger import AppLogger


class Base:
    def __init__(self):
        self.logger = AppLogger("VOAM")

        # supported modes - pdfplumber, camelot
        self.extract_mode = "pdfplumber"

    def parse_statement(self, pdf_path):
        df = self.extract_raw_tables(pdf_path)

        df["House"] = None
        df["Mode"] = "EFT"
        df["Bank Name"] = None
        df["Bank Branch"] = None
        df["Reference"] = None
        df["Receiving Account"] = "ICICI Bank 1166"

        df = df.rename(
            columns={
                "TransactionDate": "Receipt Date",
                "Cheque no /Ref No": "Cheque No",
                "Deposit(Cr)": "Paying Amount",
                "Withdrawal (Dr)": "Amount",
                "TransactionRemarks": "Description",
                "SlNo": "Sl No",
            }
        )

        file_nm = pdf_path.split("\\")[-1]
        self.logger.info(f"Tables Extracted: File = {file_nm} | Rows = {len(df)}")
        return df

    def extract_raw_tables(self, pdf_path):
        if self.extract_mode == "camelot":
            tables = camelot.read_pdf(
                pdf_path,
                pages="all",
                lattice=True,
                # flavor="stream",
                strip_text="\n",
            )
            table_df = [tbl.df for tbl in tables]

            df = pd.concat(table_df, ignore_index=True)
            df.columns = df.iloc[0].to_list()

            df = df.drop(index=[0])
        else:
            table_df = []
            with pdfplumber.open(pdf_path) as pdf:
                cols = None
                for page in pdf.pages:
                    table = page.extract_table()

                    if not cols:
                        cols = [col.replace("\n", "") for col in table[0]]
                        table = table[1:]

                    table_df.append(pd.DataFrame(table, columns=cols))

            df = pd.concat(table_df, ignore_index=True)
            df.replace("\n", "", inplace=True, regex=True)

        return df
