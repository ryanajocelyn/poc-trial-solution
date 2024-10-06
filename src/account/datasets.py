import glob
import json

from account.common.base import Base
from account.utils.constants import FLAT_NOS
from account.utils.utils import parse_house_no


class GenDatasets(Base):
    def __init__(self, params):
        super().__init__()

        self.params = params

        with open("config/dataset_lbl.json", mode="r") as cfg:
            self.ds_lbl = json.loads(cfg.read())

    def run(self):
        pdf_path = self.params["base_path"]

        pdf_files = []
        for file in glob.glob(f"{pdf_path}\\*.pdf"):
            pdf_files.append(file)

        statements = []
        for file_path in pdf_files:
            df = self.parse_statement(file_path)

            df = df.drop(df[df["Paying Amount"] == ""].index)
            df = df.reset_index(drop=True)

            statements.extend(df["Description"].to_list())

        datasets = self.generate_datasets(statements, self.ds_lbl)
        print(f"Datasets Count = {len(datasets)}")

        with open("stmt-iob.json", mode="w") as stmt:
            stmt.write(json.dumps(datasets))

    def generate_datasets(self, statements, ds_lbl):
        datasets = []
        for desc in statements:
            ents = self.split_entities(desc)

            labels = []
            for ent in ents:
                l_ent = ent.upper()

                label = self.annotate_lbl(l_ent, ds_lbl)
                labels.append(label if label else "O")

            print(ents)
            print(labels)
            datasets.append({"tokens": ents, "labels": labels})

        return datasets

    def split_entities(self, desc):
        ents = []

        sep = "-" if desc.startswith("NEFT") else "/"
        for ind, ent in enumerate(desc.split(sep)):
            if ind == 0:
                ents.append(ent)
            else:
                ents.extend([sep, ent])

        desc_ind = -1
        if ents[0] == "UPI":
            desc_ind = 4
        elif ents[0] in ["MMT", "BIL", "INF", "NEFT"]:
            desc_ind = 6

        rem = ents[desc_ind]
        house_no = parse_house_no(rem)
        print(house_no)

        house_ind = rem.find(str(house_no))
        if house_ind >= 0:
            ents.pop(desc_ind)

            cur = house_ind + len(house_no) if house_ind == 0 else house_ind
            ents.insert(desc_ind, rem[0:cur])

            cur2 = len(rem) if house_ind == 0 else cur + len(house_no)
            ents.insert(desc_ind + 1, rem[cur:cur2])

            if cur2 < len(rem):
                ents.insert(desc_ind + 2, rem[cur2 : len(rem)])

        return ents

    def annotate_lbl(self, l_ent, ds_lbl):
        label = None

        for cfg in ds_lbl:
            for opt in cfg["options"]:
                if cfg["search"] == "startswith":
                    if l_ent.startswith(opt):
                        label = cfg["label"]
                        break

                if cfg["search"] == "contains":
                    if opt in l_ent:
                        label = cfg["label"]
                        break

            if cfg["search"] == "numeric":
                if l_ent.isnumeric():
                    label = cfg["label"]
                    break

            if cfg["search"] == "flat_no":
                if l_ent in FLAT_NOS:
                    label = cfg["label"]
                    break

            if label:
                break

        return label

    def test(self):
        statements = [
            # "UPI/461178460664/From R Ganesh5/r.ganesh10@okax/Axis BankLtd/AXI9ded84257d1e4b01916127d1d6480b0d",
            # "UPI/karthic96@okici/307 Rajamani/KotakMahindra/461165571357/ICI9855014d35a34c978ccbfae57235b94e",
            # "UPI/saraswathi.subr/UPI/State Bank Of I/424563916759/SBI8814422c7da24a5ab6fa83c38bf2957d",
            # "MMT/IMPS/424512277218/sep24Flt204/MRS.MADHUM/Kotak Mahindra",
            # "NEFT-N245243238341509-BHANUMATHIBADHRINARAYANAN-1071 903 SEPMAINT-50100212184202-HDFC0000001",
            "BIL/INFT/DI14516782/Flat701Sep2024/GOVINDARAJAN VA",
            "BIL/INFT/D I14574246/407September202/P VIDYA SAGAR /",
            "NEFT-0811OP4140691498-SUBRAMANIYAMN-406 MONTHLYMAINTENANCE FEE-8826040000006712-DBSS0IN0811",
        ]
        with open("config/dataset_lbl.json", mode="r") as cfg:
            ds_lbl = json.loads(cfg.read())

        self.generate_datasets(statements, ds_lbl)


if __name__ == "__main__":
    # Start Row - Row to start from
    m_params = {
        "base_path": "D:\\Abiz\\Flats\\Vedanshi\\2024-25\\00. Accounts\\Datasets",
        "stmt_nm": "DetailedStatement-Sep-2024.pdf",
        "tpl_nm": "batch_dues_receipt_upload_5223004_.csv",
        "start_row": 66,
    }
    gen_data = GenDatasets(params=m_params)
    gen_data.run()

    # gen_data.test()
