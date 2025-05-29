# 小智 XaioZhi AI MCP 測試

### This project forked from XaioZhi MCP Sample Project
To get more information [here](https://github.com/78/mcp-calculator/tree/main) 

### Features 
MCP tools:
- MCP tool to get the timetable of Taiwan high spped rail (查詢高鐡時刻表)
- MCP tool to manage ledger entries (利用google sheet 簡單記帳)

### Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up the url of MCP_ENDPOINT:
To get the url, please go to the website: https://xiaozhi.me. Find the "MCP接入點"
```bash
export MCP_ENDPOINT=<your_mcp_endpoint>
```

3. Run the calculator example:
```bash
python mcp_pipe.py mcp_script.py
```

### go_config.json for go_sheet.py
``` json
{
   "CredentialFile": "./path_of/goapi-credentials.json",
   "SPREADSHEET_ID": "google_sheet_id-xxxx"
}
```

### TBD

``` text
### 臺灣證券交易所 OpenAPI
https://openapi.twse.com.tw
https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL

# 智慧城鄉 OpenAPI
https://www.openapi.org.tw/

# 聯合信用卡處理中心-開放資料平臺 Open API
https://bas.nccc.com.tw/nccc-nop/swagger-ui.html
```
