import asyncio
import aiohttp
import requests
import argparse
import sys
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger('TaiwanHSR_MCP')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('TaiwanHSR_MCP.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class AsyncTHSRClient:
    """台灣高鐵非同步 HTTP 客戶端"""
    
    def __init__(self):
        self.base_url = "https://www.thsrc.com.tw/TimeTable/Search"
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.thsrc.com.tw',
            'X-Requested-With': 'XMLHttpRequest'
        }
    # Donot use the aysnc funcation in FastMCP stdio
    async def search_timetable(
        self,
        start_station: str = 'NanGang',
        end_station: str = 'ZuoYing',
        outward_date: str = '2025/05/26',
        outward_time: str = '18:30',
        return_date: str = '2025/05/26',
        return_time: str = '18:00',
        search_type: str = 'S',
        lang: str = 'TW',
        discount_type: str = ''
    ) -> Dict[Any, Any]:
        """
        非同步查詢高鐵時刻表
        
        Args:
            start_station: 起始站代碼
            end_station: 終點站代碼
            outward_date: 去程日期 (YYYY/MM/DD)
            outward_time: 去程時間 (HH:MM)
            return_date: 回程日期 (YYYY/MM/DD)
            return_time: 回程時間 (HH:MM)
            search_type: 搜尋類型 ('S' 為標準搜尋)
            lang: 語言 ('TW' 為繁體中文)
            discount_type: 折扣類型
            
        Returns:
            Dict: 時刻表查詢結果的 JSON 數據
        """
        
        # 準備 POST 表單數據
        form_data = {
            'SearchType': search_type,
            'Lang': lang,
            'StartStation': start_station,
            'EndStation': end_station,
            'OutWardSearchDate': outward_date,
            'OutWardSearchTime': outward_time,
            'ReturnSearchDate': return_date,
            'ReturnSearchTime': return_time,
            'DiscountType': discount_type
        }
        
        #print(f"發送請求到: {self.base_url}")
        #print(f"表單數據: {form_data}")
        
        try:
            # 創建 aiohttp 會話
            timeout = aiohttp.ClientTimeout(total=20)  # 20秒超時
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.base_url,
                    data=form_data,
                    headers=self.headers
                ) as response:
                    
                    # print(f"HTTP 狀態碼: {response.status}")
                    # print(f"響應標頭: {dict(response.headers)}")
                    
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        
                        if 'application/json' in content_type:
                            # 如果是 JSON 響應
                            json_data = await response.json()
                            print("成功獲取 JSON 數據")
                            return json_data
                        else:
                            # 如果不是 JSON，獲取文本內容
                            text_data = await response.text()
                            print(f"獲取文本響應，長度: {len(text_data)}")
                            
                            # 嘗試解析 JSON（有時服務器返回 JSON 但 content-type 不正確）
                            try:
                                json_data = json.loads(text_data)
                                print("成功從文本解析 JSON 數據")
                                return json_data
                            except json.JSONDecodeError:
                                print("無法解析為 JSON，返回原始文本")
                                return {
                                    "error": "非 JSON 響應",
                                    "content_type": content_type,
                                    "raw_text": text_data[:500]  # 只返回前1000字符
                                }
                    else:
                        error_text = await response.text()
                        return {
                            "error": f"HTTP 錯誤 {response.status}",
                            "status": response.status,
                            "response": error_text[:500]
                        }
                        
        except asyncio.TimeoutError:
            return {"error": "請求超時", "timeout": 30}
        except aiohttp.ClientError as e:
            return {"error": f"客戶端錯誤: {str(e)}"}
        except Exception as e:
            return {"error": f"未知錯誤: {str(e)}"}

    def search_timetable_sync(
        self,
        start_station: str = 'NanGang',
        end_station: str = 'ZuoYing',
        outward_date: str = '2025/05/26',
        outward_time: str = '18:30',
        return_date: str = '2025/05/26',
        return_time: str = '18:00',
        search_type: str = 'S',
        lang: str = 'TW',
        discount_type: str = ''
    ) -> Dict[Any, Any]:
        """
        同步查詢高鐵時刻表
        
        Args:
            start_station: 起始站代碼
            end_station: 終點站代碼
            outward_date: 去程日期 (YYYY/MM/DD)
            outward_time: 去程時間 (HH:MM)
            return_date: 回程日期 (YYYY/MM/DD)
            return_time: 回程時間 (HH:MM)
            search_type: 搜尋類型 ('S' 為標準搜尋)
            lang: 語言 ('TW' 為繁體中文)
            discount_type: 折扣類型
            
        Returns:
            Dict: 時刻表查詢結果的 JSON 數據
        """
        
        # 準備 POST 表單數據
        form_data = {
            'SearchType': search_type,
            'Lang': lang,
            'StartStation': start_station,
            'EndStation': end_station,
            'OutWardSearchDate': outward_date,
            'OutWardSearchTime': outward_time,
            'ReturnSearchDate': return_date,
            'ReturnSearchTime': return_time,
            'DiscountType': discount_type
        }
        
        try:
            # 使用 requests 發送同步 POST 請求
            response = requests.post(
                self.base_url,
                data=form_data,
                headers=self.headers,
                timeout=20  # 20秒超時
            )
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                
                if 'application/json' in content_type:
                    # 如果是 JSON 響應
                    json_data = response.json()
                    print("成功獲取 JSON 數據")
                    return json_data
                else:
                    # 如果不是 JSON，獲取文本內容
                    text_data = response.text
                    print(f"獲取文本響應，長度: {len(text_data)}")
                    
                    # 嘗試解析 JSON（有時服務器返回 JSON 但 content-type 不正確）
                    try:
                        json_data = json.loads(text_data)
                        print("成功從文本解析 JSON 數據")
                        return json_data
                    except json.JSONDecodeError:
                        print("無法解析為 JSON，返回原始文本")
                        return {
                            "error": "非 JSON 響應",
                            "content_type": content_type,
                            "raw_text": text_data[:500]  # 只返回前500字符
                        }
            else:
                error_text = response.text
                return {
                    "error": f"HTTP 錯誤 {response.status_code}",
                    "status": response.status_code,
                    "response": error_text[:500]
                }
                
        except requests.Timeout:
            return {"error": "請求超時", "timeout": 20}
        except requests.RequestException as e:
            return {"error": f"請求錯誤: {str(e)}"}
        except Exception as e:
            return {"error": f"未知錯誤: {str(e)}"}
        
        async def get_station_info(self) -> Dict[str, str]:
            """
            獲取高鐵站點資訊
            
            Returns:
                Dict: 站點代碼對應表
            """
            return stationinfo_list()
       

def stationinfo_list()-> Dict[str, str]:
    return {
        "NanGang": "南港",
        "TaiPei": "台北", 
        "BanQiao": "板橋",
        "TaoYuan": "桃園",
        "XinZhu": "新竹",
        "MiaoLi": "苗栗",
        "TaiZhong": "台中",
        "ZhangHua": "彰化",
        "YunLin": "雲林",
        "JiaYi": "嘉義",
        "TaiNan": "台南",
        "ZuoYing": "左營",
        "ZuoYing": "高雄"
    }

def stationinfo_code(station_name: str) -> str:
    stations = stationinfo_list()
    for code, name in stations.items():
        #print(f"search {station_name} {name}")
        if  station_name == code or station_name == name:
            return code
    return ''

def get_current_datetime() -> Dict[Any, Any]:
    # 取得當前日期與時間
    current_time = datetime.now()
    
    if current_time.minute >= 30:
        new_hour = current_time.hour + 1
        current_time = datetime(
            year=current_time.year,
            month=current_time.month,
            day=current_time.day,
            hour=new_hour,
            minute=0,
            second=0
        )
    else:
        current_time = datetime(
            year=current_time.year,
            month=current_time.month,
            day=current_time.day,
            hour=current_time.hour,
            minute=30,
            second=0
        )
        
    # 使用 strftime() 格式化字串
    date_str = current_time.strftime("%Y/%m/%d")
    time_str = current_time.strftime("%H:%M")
    # date_str = f"{current_time.year}/{current_time.month:02d}/{current_time.day:02d}"
    # time_str = f"{current_time.hour:02d}:{current_time.minute:02d}"

    # 組織成指定的字典格式
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

def format_timetable_result(result: Dict[Any, Any], max: int=5, aftertime: str='N/A'):
    """
    格式化時刻表查詢結果並美化輸出
    
    Args:
        result: 高鐵 API 回應的 JSON 數據
    """
    mcp_result = "查詢失敗\n"
    try:
        if not result.get('success', False):
            print("查詢失敗")
            return mcp_result
        
        data = result.get('data', {})
        departure_table = data.get('DepartureTable', {})
        price_table = data.get('PriceTable', {})
        
        # 輸出標題資訊
        title = departure_table.get('Title', {})
        start_station = title.get('StartStationName', '未知')
        end_station = title.get('EndStationName', '未知')
        search_time = title.get('TitleSplit1', '未知時間')
        
        print(f"\n{'='*60}")
        print(f"🚄 台灣高鐵時刻表查詢結果")
        print(f"{'='*60}")
        print(f"路線: {start_station} → {end_station}")
        print(f"查詢時間: {search_time}")
        print(f"{'='*60}")
        mcp_result = f"台灣高鐵時刻表查詢結果\n"
        mcp_result += f"路線: 從 {start_station} 到 {end_station}\n"
        
        # 輸出列車時刻表
        train_items = departure_table.get('TrainItem', [])
        if train_items:
            print(f"\n🕐 列車時刻表 (全天共 {len(train_items)} 班次)")
            print(f"{'-'*80}")
            #print(f"{'車次':^6} {'發車時間':^8} {'到達時間':^8} {'行車時間':^8} {'標準座':^8} {'商務座':^8} {'自由座':^8}")
            #print(f"{'-'*80}")
            print(f"{'車次':^6} {'發車時間':^6} {'到達時間':^6} {'行車時間':^8}")
            print(f"{'-'*80}")
            mcp_result += f"\n{'車次':^6} {'發車時間':^6} {'到達時間':^6} {'行車時間':^8}\n"
            mcp_result += f"{'-'*60}\n"
            
            #獲取票價資訊
            coach_prices = price_table.get('Coach', [])
            business_prices = price_table.get('Business', [])
            unreserved_prices = price_table.get('Unreserved', [])
            
            listNum = 0
            for i, train in enumerate(train_items):
                train_number = train.get('TrainNumber', 'N/A')
                departure_time = train.get('DepartureTime', 'N/A')
                destination_time = train.get('DestinationTime', 'N/A')
                duration = train.get('Duration', 'N/A')
            
                if departure_time == 'N/A':
                    continue
                if aftertime != 'N/A':
                    if aftertime >= departure_time:
                        continue
            
                # 獲取對應的票價（如果有的話
                # coach_price = coach_prices[0] if listNum < 1 else '-'
                # business_price = business_prices[0] if listNum < 1 else '-'
                # unreserved_price = unreserved_prices[0] if listNum < 1 else '-'
                
                #print(f"{train_number:^8} {departure_time:^10} {destination_time:^10} {duration:^10} {coach_price:^8} {business_price:^8} {unreserved_price:^8}")
                print(f"{train_number:^8} {departure_time:^10} {destination_time:^10} {duration:^10}")
                mcp_result += f"{train_number:^8} {departure_time:^10} {destination_time:^10} {duration:^10}\n"
                
                listNum = listNum + 1
                if max > 0 and listNum >= max:
                    break
            print(f"{'-'*80}")
            mcp_result += f"{'-'*60}\n"
        else:
            print("❌ 沒有找到合適的班次")
            mcp_result += '沒有找到合適的班次'
        
        # 輸出票價說明
        if price_table:
            print(f"💰\n票價說明 {'普通票':^6} {'優待票':^6} {'自由座':^6}")
            print(f"{'-'*60}")
            mcp_result += f"\n票價說明 {'普通票':^6} {'優待票':^6} {'自由座':^6}\n"
            mcp_result += f"{'-'*60}\n"
            
            coach_prices = price_table.get('Coach', [])
            business_prices = price_table.get('Business', [])
            unreserved_prices = price_table.get('Unreserved', [])
            
            if coach_prices:
                print(f"標準座:   {', '.join(coach_prices)}")
                mcp_result += f"標準座:   {', '.join(coach_prices)}\n"
            if business_prices:
                print(f"商務座:   {', '.join(business_prices)}")
                mcp_result += f"商務座:   {', '.join(business_prices)}\n"
            if unreserved_prices:
                print(f"自由座:   {', '.join(unreserved_prices)}")
                mcp_result += f"自由座:   {', '.join(unreserved_prices)}\n"
        
        print(f"\n{'='*60}")
        mcp_result == f"\n{'='*60}\n"
        return mcp_result
        
    except Exception as e:
        print(f"格式化輸出時發生錯誤: {e}")
        mcp_result += "格式化輸出時發生錯誤\n"
        print("原始 JSON 資料:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return mcp_result

def tawinhsr_mcp_call(start_station: str, end_station: str, query_date: str, query_time: str):
    """主程式 - 示範如何使用非同步客戶端"""
    
    logger.info(f"params: {start_station} {end_station} {query_date} {query_time}")
    
    print("=== 台灣高鐵時刻表查詢 ===")
    print()
    
    # 創建客戶端實例
    client = AsyncTHSRClient()
    
    # 查詢時刻表（使用您提供的參數）
    start_code = stationinfo_code(start_station)
    end_code = stationinfo_code(end_station)
    if len(start_code) == 0 or len(end_code) == 0:
        print(f"查無從{start_station}到{end_station}的時刻表")
        return f"查無從{start_station}到{end_station}的時刻表"
    now_dt = get_current_datetime()
    print("正在查詢時刻表...")
    
    result = client.search_timetable_sync(
        start_station = start_code,
        end_station   = end_code,
        outward_date  = query_date,
        outward_time  = query_time,
        return_date=now_dt['date_str'],
        return_time=now_dt['time_str']
    )
    
    print("\n=== 查詢結果 ===")
    if 'error' in result:
        print(f"發生錯誤: {result['error']}")
        if 'raw_text' in result:
            print(f"原始響應: {result['raw_text'][:200]}...")
        return "網路查詢發生錯誤\n"
    else:
        print("查詢成功！")
        #print(json.dumps(result, ensure_ascii=False, indent=2))
        return format_timetable_result(result=result, max=5, aftertime=query_time)
    
    #print("\n=== 站點資訊 ===")
    #stations = await client.get_station_info()
    #for code, name in stations.items():
    #    print(f"{code}: {name}")

async def main():
    """主程式 - 示範如何使用非同步客戶端"""
    
    print("=== 台灣高鐵時刻表查詢 ===")
    print()
    
    # 創建客戶端實例
    client = AsyncTHSRClient()
    
    # 查詢時刻表（使用您提供的參數）
    now_dt = get_current_datetime()
    print(f"正在查詢時刻表...{now_dt['date_str']} {now_dt['time_str']}")
    
    result = await client.search_timetable(
        start_station='NanGang',
        end_station='ZuoYing',
        outward_date='2025/05/28',
        outward_time='05:30',
        return_date=now_dt['date_str'],
        return_time=now_dt['time_str']
    )
    
    print("\n=== 查詢結果 ===")
    if 'error' in result:
        print(f"發生錯誤: {result['error']}")
        if 'raw_text' in result:
            print(f"原始響應: {result['raw_text'][:200]}...")
    else:
        print("查詢成功！")
        #print(json.dumps(result, ensure_ascii=False, indent=2))
        format_timetable_result(result)
    
    print("\n=== 站點資訊 ===")
    stations = await client.get_station_info()
    for code, name in stations.items():
        print(f"{code}: {name}")

# 併發查詢多個路線的範例
async def batch_search_example():
    """批量查詢範例"""
    
    print("\n=== 批量查詢範例 ===")
    
    client = AsyncTHSRClient()
    
    # 定義多個查詢任務
    search_tasks = [
        client.search_timetable('TaiPei', 'TaiZhong', '2025/05/26', '08:00'),
        client.search_timetable('TaiZhong', 'TaiNan', '2025/05/26', '10:00'),
        client.search_timetable('JiaYi', 'ZuoYing', '2025/05/26', '12:00')
    ]
    
    # 併發執行所有查詢
    print("正在併發執行多個查詢...")
    start_time = datetime.now()
    
    results = await asyncio.gather(*search_tasks, return_exceptions=True)
    
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    
    print(f"批量查詢完成，耗時: {elapsed:.2f} 秒")
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"查詢 {i+1} 失敗: {result}")
        else:
            print(f"查詢 {i+1} 成功")
            format_timetable_result(result)

if __name__ == "__main__":
    # print(f"程式名稱: {sys.argv[0]}")
    now_dt = get_current_datetime()
    parser = argparse.ArgumentParser(description='高鐡時刻表查詢')
    parser.add_argument('--start', '-s', type=str, required=True, default='台北', 
                       help='起始站名')
    parser.add_argument('--dest', '-d', type=str, required=True, default='新竹', 
                       help='目的站名')
    parser.add_argument('--date', '-D', type=str, default=now_dt['date_str'], 
                        help='日期')
    parser.add_argument('--time', '-T', type=str, default=now_dt['time_str'], 
                        help='時間')
    args = parser.parse_args()

    if len(sys.argv) > 4:
        result = tawinhsr_mcp_call(
            args.start, 
            args.dest, 
            args.date, 
            args.time)
        logger.info(f"result: {result}")
    else:
        print(f"開始執行非同步查詢...{sys.argv}")
        asyncio.run(main())
    
    # 運行批量查詢範例
    #asyncio.run(batch_search_example())


                         
""" 
### POST https://www.thsrc.com.tw/TimeTable/Search
Host: www.thsrc.com.tw
Content-Type: application/x-www-form-urlencoded
Origin: https://www.thsrc.com.tw
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64)

StationList = [
  { ch:'台北', en:'TaiPei' },
  { ch:'南港', en:'NanGang' },
  { ch:'板橋', en:'BanQiao' },
  { ch:'桃園', en:'TaoYuan' },
  { ch:'新竹', en:'XinZhu' },
  { ch:'苗栗', en:'MiaoLi' },
  { ch:'台中', en:'TaiZhong' },
  { ch:'彰化', en:'ZhangHua' },
  { ch:'雲林', en:'YunLin' },
  { ch:'嘉義', en:'JiaYi' },
  { ch:'台南', en:'TaiNan' },
  { ch:'左營', en:'ZuoYing' }
]

### form-data:
SearchType='S'
Lang='TW'
StartStation='NanGang'
EndStation='ZuoYing'
OutWardSearchDate='2025/05/26'
OutWardSearchTime='18:30'
ReturnSearchDate='2025/05/26'
ReturnSearchTime='18:00'
DiscountType=''

### response result: 
taiwan_hsr.json
"""

