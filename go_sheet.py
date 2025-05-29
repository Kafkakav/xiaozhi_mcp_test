
# pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib gspread

import sys
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger('GGSheet_MCP')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('GGSheet_MCP.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]

# go_config.json = {
#   "CredentialFile": "./path_of/goapi-credentials.json",
#   "SPREADSHEET_ID": "google_sheet_id-xxxx"
# }
GOCONF_FILE = 'go_config.json'

class GoSheetEditor:
    
    def __init__(self, file_path: str = ''):
        # 打開 Google Sheet (透過 ID)
        # 替換成你的 Google Sheet 的實際 ID
        # 你可以在 Google Sheet 的網址中找到 ID，它位於 /d/ 和 /edit 之間
        # 例如：https://docs.google.com/spreadsheets/d/1BltWkU2t8Rk-XXXXXXX-s9qX7Yw/edit#gid=0
        # ID 就是 1BltWkU2t8Rk-XXXXXXX-s9qX7Yw

        self.SPREADSHEET_NAME = ''
        self.SPREADSHEET_ID = ''
        self.client = None
        self.sheetFile = None
        self.worksheetName = "Notebook"
        self.CredentialFile = './authcreds/ggapi-credentials.json'
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            if isinstance(data, dict):
                if "CredentialFile" in data:
                    self.CredentialFile = data['CredentialFile']
                if "SPREADSHEET_ID" in data:
                    self.SPREADSHEET_ID = data['SPREADSHEET_ID']
                if "SPREADSHEET_NAME" in data:
                    self.SPREADSHEET_NAME = data['SPREADSHEET_NAME']
                self.is_init = True
        except FileNotFoundError:
            print(f"Error: File not found '{file_path}'")
        except json.JSONDecodeError:
            print(f"Error: invalid json file'{file_path}'")
        except Exception as e:
            print(f"Error: unknown error{e}")

    def gg_authorize(self, credFile:str='', scopes=SCOPES) -> bool:
        try:
            if len(credFile) == 0:
                credFile = self.CredentialFile
            creds = Credentials.from_service_account_file(credFile, scopes=scopes)
        except FileNotFoundError:
            print("fError: Credential file not found'{credFile}'")
            self.client = None
            return False
        self.client = gspread.authorize(creds)
        return True

    def gsheet_open_file(self, type:int=0, name:str='') -> bool:
        if not self.client:
            print(f"Error: client not initialized")
            return False
        try:
            if len(self.SPREADSHEET_ID) > 1:
                self.sheetFile = self.client.open_by_key(self.SPREADSHEET_ID)
                print(f"Open Google Sheet ID: '{self.SPREADSHEET_ID}'")
            elif len(self.SPREADSHEET_NAME) > 1:
                self.sheetFile = self.client.open(self.SPREADSHEET_NAME)
                print(f"Open Google Sheet Name: '{self.SPREADSHEET_NAME}'")
            else:
                self.sheetFile = None
                print(f"Error: unknown Google Sheet ID/Name '{name}'")
                return False
            return True
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"Error: Failed to open Google Sheet '{self.SPREADSHEET_NAME}'. Not found or permission denied")
            return False

    def account_book_create(self, new_entry):
       
        # worksheet = gosheet.sheetFile.sheet1
        # worksheet = gosheet.sheetFile.get_worksheet(0)
        worksheet = self.sheetFile.worksheet(self.worksheetName)
        
        # 清除工作表內容 (可選)
        # worksheet.clear()
        # print("工作表已清空。")
        print(f"creating a new entry on '{worksheet.title}'")
        nowT = get_current_datetime()
    
        # 要新增的單行資料
        # 日期, 時間, 名稱, 個數, 小計價格, 狀態, 備註
        new_row_data = [ 
            nowT['date_str'], nowT['time_str'], 
            new_entry['name'], new_entry['count'], new_entry['subtotal']
        ]
        worksheet.append_row(new_row_data)
        print(f"a new entry added: {new_row_data}")
    
        current_data_rows = len(worksheet.get_all_values())
        item_id = current_data_rows
        return f"Successfully created entry. Item ID is {item_id}, available for future reference."
        
        # Sample
        # 寫入多行多列數據 (列表的列表)
        # data_to_write = [
        #     ['Alice', 30, 'New York'],
        #     ['Bob', 24, 'London'],
        #     ['Charlie', 35, 'Paris']
        # ]
        # 從 A3 儲存格開始寫入
        # worksheet.update(data_to_write, 'A3')
        # worksheet.append_rows(new_rows_data)
        # print("已更新 A3 開始的多行數據。")
        
        # item_id = worksheet.row_count
        # 獲取當前工作表中的資料行數 (不含空白行)
        # 這是最可靠的方法，因為它會數有數據的行
        
    
    def account_book_update(self, new_entry):
        worksheet = self.sheetFile.worksheet(self.worksheetName)
    
        print(f"updating an entry on '{worksheet.title}'")
        nowT = get_current_datetime()
        item_id = new_entry['id']
        if item_id <= 1:
            return f"failee to delete. Item ID must be greater than 1."
            
        # 要新增的單行資料
        # 日期, 時間, 名稱, 個數, 小計價格, 狀態, 備註
        # 寫入多個儲存格 (單行)
        origData = worksheet.row_values(int(new_entry['id']))
        rowId = f"A{new_entry['id']}"
        new_row_data = [ 
            origData[0], origData[1], 
            new_entry['name'], new_entry['count'], new_entry['subtotal'],
            'update', f"{nowT['time_str']} {nowT['date_str']} 更新"
        ]
        worksheet.update([new_row_data], rowId)
        print(f"an entry updated {item_id}")
        return f"Successfully updated entry. Item ID: {item_id}."
        
        # Sample
        # 使用 update_cells_batch (更高效地更新多個不連續的儲存格)
        # cells_to_update = [
        #     gspread.Cell(row=1, col=5, value='Batch Update 1'),
        #     gspread.Cell(row=2, col=5, value='Batch Update 2')
        # ]
        # worksheet.update_cells(cells_to_update)
        # print("已通過批次更新儲存格。")
        
    
    def account_book_delete(self, new_entry):
        worksheet = self.sheetFile.worksheet(self.worksheetName)
    
        print(f"deleting a entry on '{worksheet.title}'")
        nowT = get_current_datetime()
        item_id = new_entry['id']
        if item_id <= 1:
            return f"failee to delete. Item ID must be greater than 1."
        
        # 要新增的單行資料
        # 日期A, 時間B, 名稱C, 個數D, 小計價格E, 狀態F, 備註G
        # 寫入多個儲存格 (單行)
        rowId = f"F{new_entry['id']}"
        # 寫入單個儲存格
        worksheet.update_acell(rowId, 'deleted')
        print(f"a entry deleted {item_id}")
          
        return f"Successfully deleted entry with Item ID: {item_id}."
    
    def account_book_read(self, new_entry):
        worksheet = self.sheetFile.worksheet(self.worksheetName)
    
        print(f"reading a entry on '{worksheet.title}'")
        item_id = new_entry['id']
        if item_id <= 1:
            return f"failee to delete. Item ID must be greater than 1."
        # all_sheet_values = worksheet.get_all_values()
        # print("\n--- All values in the sheet (list of lists) ---")
        # for row in all_sheet_values:
        #     print(row)
        rowId = int(new_entry['id'])
        read_row_data = worksheet.row_values(rowId)
        
        mcp_result = f"Successfully retrieved entry details for Item ID: {item_id}."
        mcp_result += f"\n{'日期,':<6} {'時間,':<6} {'名稱,':<6} {'個數,':<6} {'小計價格,':<8} {'狀態,':<6} {'備註':<8}\n"
        mcp_result += f"{', '.join(read_row_data)}"
        return mcp_result
        
        # Sample
        # first_column_data = worksheet.col_values(1)
        # cell_b1_value = worksheet.cell(1, 2).value
        # cell_d3_value = worksheet.acell('D3').value
    
        # # Example: Get values from range A1 to C5
        # cell_range = worksheet.range('A1:C5')
        # print(f"\n--- Values from range A1:C5 ---")
        # for cell in cell_range:
        #     print(f"Cell {cell.label} (Row: {cell.row}, Col: {cell.col}): {cell.value}")
        # 
        # # If you just want the values as a list of lists, you can process it:
        # # all_values_in_range = []
        # # for r_idx in range(1, 6): # Rows 1 to 5
        # #     row_values = []
        # #     for c_idx in range(1, 4): # Columns A to C
        # #         cell = worksheet.cell(r_idx, c_idx)
        # #         row_values.append(cell.value)
        # #     all_values_in_range.append(row_values)
        # # print("\nValues in range A1:C5 (as list of lists):")
        # # print(all_values_in_range)

def get_current_datetime() -> Dict[Any, Any]:
    # 取得當前日期與時間
    current_time = datetime.now()
    # 使用 strftime() 格式化字串
    date_str = current_time.strftime("%Y-%m-%d")
    time_str = current_time.strftime("%H:%M")
    return {
        'year': current_time.year,
        'month': current_time.month,
        'day': current_time.day,
        'hour': current_time.hour,
        'min': current_time.minute,
        'sec': current_time.second,
        'date_str': date_str,
        'time_str': time_str
    }

# 記帳本beta1
def account_book_mcp_call(method:str, item_id:int, item_name:str, item_count:int, total_price:int):
    """
    This tool is used to manage ledger entries, supporting standard Create, Read, Update, and Delete (CRUD) operations.

    Args:
        method (str): The operation to perform.
                      - If **'create'**: Use this to add a new ledger entry. For new entries, **item_id must be 0**.
                      - If **'read'**: Use this to retrieve details of an existing ledger entry. You **must provide the specific item_id** of the entry you want to read. When reading, `item_name`, `item_count`, and `total_price` are ignored.
                      - If **'update'**: Use this to modify an existing ledger entry. You **must provide the specific item_id** of the entry to be updated.
                      - If **'delete'**: Use this to remove an existing ledger entry. You **must provide the specific item_id** of the entry to be deleted. When deleting, `item_name`, `item_count`, and `total_price` are ignored.
        item_id (int): The unique identifier for the ledger item and item_id must be greater than 1.
                       - For **'create'** operations, set this to **0**. The system will assign a new ID.
                       - For **'read'**, **'update'**, or **'delete'** operations, this must be the exact ID of the existing item you wish to interact with.
        item_name (str): The name or description of the ledger item.
                         (Required for 'create' and 'update' operations, ignored for 'read' and 'delete').
        item_count (int): The quantity of the item.
                          (Required for 'create' and 'update' operations, ignored for 'read' and 'delete').
        total_price (int): The total price of the item(s).
                           (Required for 'create' and 'update' operations, ignored for 'read' and 'delete').

    Returns:
        str: A confirmation message indicating the success of the operation.
             For 'create' operations, this message will include the newly assigned item ID,
             which can be used for future 'read', 'update', or 'delete' actions.
             For 'read', 'update', or 'delete' operations, the message will confirm the action
             and might include relevant details about the item or the outcome.
    """
   
    gosheet = GoSheetEditor(file_path=GOCONF_FILE)
    gosheet.gg_authorize(scopes=SCOPES)
    gosheet.gsheet_open_file()
    if not gosheet.sheetFile:
        return f"Cannot open accouont book"

    new_entry = {
        'id': item_id,
        'name': item_name,
        'count': item_count,
        'subtotal': total_price
    }

    if method == 'create':
        return gosheet.account_book_create(new_entry)
    elif method == 'update':
        if item_id < 1:
            return "Error: Cannot update with item_id < 1. Please provide a valid item_id for update."
        return gosheet.account_book_update(new_entry)    
    elif method == 'read':
        if item_id < 1:
            return "Error: Cannot update with item_id < 1. Please provide a valid item_id for read."
        return gosheet.account_book_read(new_entry)
    elif method == 'delete':
        if item_id < 1:
            return "Error: Cannot delete with item_id < 1. Please provide a valid item_id for delete."
        return gosheet.account_book_delete(new_entry)
    else:
        return "Error: Invalid method specified. Please use 'create', 'read', 'update', or 'delete'."

if __name__ == "__main__":
    # print(f"程式名稱: {sys.argv[0]}")
    nowT = get_current_datetime()
    res = account_book_mcp_call("create", 0, f"測試新增{nowT['time_str']}", 9, 9999)
    print(f"create: {res}\n")
    res = account_book_mcp_call("update", 2, f"修改測試{nowT['time_str']}", 8, 8888)
    print(f"update: {res}\n")
    res = account_book_mcp_call("read", 2, "", 2, 888)
    print(f"read: {res}\n")
    res = account_book_mcp_call("delete", 2, "", 2, 888)
    print(f"delete: {res}\n")
    
