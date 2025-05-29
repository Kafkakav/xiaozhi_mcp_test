# 小智 XiaoZhi AI How To

### 1. download the project xiaozhi-esp32
``` bash
git clone https://github.com/78/xiaozhi-esp32.git

```

### 2. setup ESP32 build envrionment (docker here)
``` bash
IMAGE_VNAME="espressif/idf:release-v5.4"
CONTAINER_NAME=esp32_idf
PROJECT_DIR=xiaozhi-esp32 # git clone folder

docker run -it --name ${CONTAINER_NAME} --rm \
  -v $PROJECT_DIR:/project -w /project -u $UID \
  -e HOME=/tmp ${IMAGE_VNAME} /bin/bash

```

### 3. setup build configuration (esp32_idf container)
``` bash
cd /procject
source /opt/esp/idf/export.sh

# set build target esp32s3 n16r8 (or esp32c3 depends on your hardware)
idf.py set-target esp32s3 

# menuconfig to customize features
idf.py menuconfig

```
Enter the menuconfig settings after run idf.py menuconfig
``` text
# change settings you want, such as Default Language, Board Type, OLED Type ...
# save and exit menuconfig after you did (pressing the ESC key repeatedly)

Xiaozhi Assistant  --->
(https://api.tenclass.net/xiaozhi/ota/) Default OTA URL
    Default Language (Chinese Traditional)  --->
    Board Type (面包板新版接线（WiFi）)  --->
    OLED Type (SSD1306, 分辨率128*32)  --->
[ ] Enable WeChat Message Style
[*] Enable Wake Word Detection
[*] Enable Audio Noise Reduction
[ ]     Enable Server-Side AEC
    IoT Protocol (MCP协议 2024-11-05)  --->

```

### 4. Build the project
```
idf.py build

# folder of build result:
# project/build
# project/build/esp-id

# clean previous build
idf.py clean

# clean all previous build and release and reset menucnofig (do this carefully)
idf.py fullclean

```

### 5. Release image
``` text
python scripts/release.py

# folder of image:
# project/releases/v1.6.6_bread-compact-wifi.zip

```

### 6. Update firmware
1. unzip v1.6.6_bread-compact-wifi.zip then you'll get the file merged-binary.bin
2. use esptool firmware tool or esp-launchpad webiste
3. plug esp32 UART(the right one) in the PC usb port
4. using esp-launchpad webiste (using browser chrome or edge) 
[esp-launchpad](https://espressif.github.io/esp-launchpad/)
5. In esp-launchpad webiste -> DIY
  a. Connect to COM port of ESP32 
  b. Flash Address: 0x0
  c. select image file: merged-binary.bin
  d. Program and wait for it to finish
6. reboot/reset esp32 


## How To

### 支援正體中文字型(支援部分日文) 
``` text
# source xiaozhi-esp32\managed_components\78__xiaozhi-fonts
專案是用lvgl點陣字型庫, 需要透過[lv_font_conv](https://github.com/lvgl/lv_font_conv)轉換ttf字型
轉換的過程只包含GB2312.TXT字集, 如果要支援正體中文必須手動修改轉換範圍
**注意**字集太多會造成ESP32記憶體的負擔, 可能無燒錄或功能異常
原來GB2312字集: font_puhui_14_1.c size 1.8 8MB (object code: 3xxKB)
修改後GBK字集: font_puhui_14_1.c size 5.28 MB (object code: 821KB)

```
修改 font.py, 支援GBK uncode 字集 0x4E00 - 0x9FFF
``` python
def load_symbols(type):
    symbols = ["•", "·", "÷", "×", "©", "¥", "®"]
    for line in open("GB2312.TXT"):
        if line.startswith("#") or line.strip() == "":
            continue
        parts = line.split()
        unicode = int(parts[1], 16)
        # GBK range 0x4E00-0x9FFF
        if type == "GBK":
            if unicode < 0x4E00 or unicode > 0x9FFF:
                symbols.append(chr(unicode))
        else:
            symbols.append(chr(unicode))
    return symbols

# 修改轉換指令, 新增範圍 -r 0x4E00-0x9FFF
lv_font_conv {flags} --font {font} --format lvgl --lv-include lvgl.h --bpp {args.bpp} -o {output} --size {args.font_size} -r 0x20-0x7F -r 0x4E00-0x9FFF --symbols {symbols_str}

```
