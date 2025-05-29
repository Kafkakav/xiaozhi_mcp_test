# server.py
import asyncio
from mcp.server.fastmcp import FastMCP
import sys
import logging
#from ast import literal_eval
from taiwan_hsr import tawinhsr_mcp_call
from go_sheet import account_book_mcp_call

logger = logging.getLogger('MyFirstMCP')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('MyFirstMCP.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

import math
import random

# Create an MCP server
mcp = FastMCP(name="UtilityTools", 
        instructions="""
            This server provides utilities, like calculator and the timetable of taiwan high speed rail.
            """
        )

def safe_math_eval(expr: str):
    allowed_names = {
        k: v for k, v in math.__dict__.items() 
        if not k.startswith("_")  # Exclude private methods
    }
    allowed_names.update({"abs": abs, "min": min, "max": max})
    
    return eval(expr, {"__builtins__": None}, allowed_names)
    
# an calculator
@mcp.tool()
def calculator(python_expression: str) -> dict:
    """For mathamatical calculation, always use this tool to calculate the result of a python expression. `math` and `random` are available."""
    try:
        # 使用更安全的評估方式
        result = safe_math_eval(python_expression) 
        #result = eval(python_expression)
        logger.info(f"Calculating formula: {python_expression}, result: {result}")
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Calculation error: {e}")
        return {"success": False, "error": str(e)}

# taiwan hgig speed railway timetable 
@mcp.tool()
async def taiwan_high_speed_rail_timetable(start_station: str, destination_station: str, query_date: str, query_time: str) -> dict:
    """
    For timetable of taiwan high speed rail, always use this tool to search the timetable of a train.
    please provide these paramters below:

    Args:
        start_station (str): The starting station for the train journey. 
            **Allowed values: "TaiPei", "NanGang", "BanQiao", "TaoYuan", "XinZhu", "MiaoLi", "TaiZhong", "ZhangHua", "YunLin", "JiaYi", "TaiNan", "ZuoYing".**
            For example, "TaiPei" means 台北
        destination_station (str): The destination station for the train journey.
            **Allowed values: "TaiPei", "NanGang", "BanQiao", "TaoYuan", "XinZhu", "MiaoLi", "TaiZhong", "ZhangHua", "YunLin", "JiaYi", "TaiNan", "ZuoYing".**
            For example, "TaiZhong" means 台中
        query_date (str): The date for the train query in 'YYYY/MM/DD' format. For example, "2025/05/27".
        query_time (str): The desired departure time for the train query in 'HH:MM' format (24-hour clock). For example, "14:30".

    Returns:
        dict: A dictionary containing the train timetable information.
   
    """
    result = tawinhsr_mcp_call(
        start_station,
        destination_station,
        query_date,
        query_time
    )
    
    logger.info(f"twhsr timetable: result: {result}")
    return {"success": True, "result": result}

# an account book (帳本)
@mcp.tool()
def account_book(method:str, item_id:int, item_name:str, item_count:int, total_price:int):
    """
    This tool is used to manage ledger(帳本) entries, supporting standard Create, Read, Update, and Delete (CRUD) operations.

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

    result = account_book_mcp_call(
        method, item_id, item_name, item_count, total_price)
    
    logger.info(f"twhsr timetable: result: {result}")
    return {"success": True, "result": result}

# Start the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
