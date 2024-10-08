import os

FLAT_NOS = ["104", "105", "106", "107", "108"]
FLAT_NOS.extend(["204", "205", "207", "208"])
FLAT_NOS.extend(["304", "305", "306", "307", "308"])
FLAT_NOS.extend(["401", "402", "403", "404", "405", "406", "407", "408"])
FLAT_NOS.extend(["501", "502", "503", "504", "505", "506", "507", "508"])
FLAT_NOS.extend(["601", "602", "603", "604", "605", "606", "607", "608"])
FLAT_NOS.extend(["701", "702", "703", "704", "705", "706", "707", "708"])
FLAT_NOS.extend(["801", "802", "803", "804", "805", "806", "807", "808"])
FLAT_NOS.extend(["901", "902", "903", "904", "905", "906", "907", "908"])


MAINT_PER_APT = {
    1: 4230,
    2: 5320,
    3: 3950,
    4: 4290,
    5: 3410,
    6: 3690,
    7: 4000,
    8: 2660,
}

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

BILL_PLAN_TPL_DROP_COLS = [
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

BILL_PLAN_TPL_COLS = [
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

RECEIPTS_ADVANCE_COLS = [
    "Sl No",
    "House",
    "Advance Type",
    "Mode",
    "Cheque number",
    "Bank name",
    "Bank branch",
    "Receipt Date(dd-mm-yy)",
    "Advance Receiving Amount",
    "Reference",
    "Description",
    "Receiving Account",
]
