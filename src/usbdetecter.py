#install wmi
import wmi
import json
import os

CONFIG_FILE2 = 'config2.json'
def detect():
    c = wmi.WMI()
    usbb = []
    for disk in c.Win32_DiskDrive():
        if disk.InterfaceType == 'USB':
            for partition in disk.associators("Win32_DiskDriveToDiskPartition"):
                for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                    drive_letter = logical_disk.DeviceID  
                    usbb.append({
                        "DriveLetter": drive_letter,
                        "DeviceID": disk.DeviceID})                    
    return usbb

def save_config_INFO(usbb):  #檔案存入JSON中
    with open(CONFIG_FILE2, 'w', encoding='utf-8') as f:
        json.dump({"usbb": usbb}, f, indent=4)

def load_config_ID():  #再次存檔時確認已記錄資料夾
    if os.path.exists(CONFIG_FILE2):
        with open(CONFIG_FILE2, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("DeviceID", [])
    return []

def check_usb():
    usbb = load_config_ID()
    if usbb == detect[0]["DeviceID"]:
        return '1'
    else:
        return '0'

DL = detect()[0]['DriveLetter']
USB_BACKUP_DEST = DL + "\檔案備份地點"