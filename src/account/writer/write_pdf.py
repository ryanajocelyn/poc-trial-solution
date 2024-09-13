from datetime import datetime

import pandas as pd
import win32com.client as win32
from openpyxl import load_workbook
from openpyxl.styles import Border, Side

from account.utils.utils import get_parent_dir
from account.writer.base_writer import BaseWriter


class PdfWriter(BaseWriter):
    def __init__(self, base_path):
        super().__init__(base_path)

        parent_dir = get_parent_dir(__file__)
        self.template = f"{parent_dir}\\config\\dues_template.xlsx"

    def write(self, xls_path, file_nm):
        pdf_path = f"{self.path}\\{file_nm}"

        self.excel_to_pdf_win32(xls_path, pdf_path)

        return pdf_path

    def excel_to_pdf_win32(self, excel_file, output_pdf):
        # Open Excel application
        excel = win32.Dispatch("Excel.Application")

        # Open the Excel file
        workbook = excel.Workbooks.Open(excel_file)

        # Set Excel to invisible (so it won't pop up)
        excel.Visible = False

        # Export as PDF (by default, it will save all sheets)
        workbook.ExportAsFixedFormat(0, output_pdf)

        # Close the workbook and quit Excel
        workbook.Close(False)
        excel.Quit()
