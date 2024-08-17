import camelot

from dotenv import load_dotenv

load_dotenv()


class Maintenance:
    def run(self):
        pdf_path = "D:\\Abiz\\Flats\\Vedanshi\\2024-25\\03. Jun\\Statement\\DetailedStatement-3.pdf"
        tables = camelot.read_pdf(pdf_path, pages="all", lattice=True)
        print(tables)

        for tbl in tables:
            print(tbl.df)


if __name__ == "__main__":
    Maintenance().run()
