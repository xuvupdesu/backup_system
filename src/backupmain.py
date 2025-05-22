import os
import shutil
import json
from tkinter import Tk, filedialog, messagebox
from datetime import datetime
from usbdetecter import detect, check_usb, USB_BACKUP_DEST, save_config_INFO, load_config_ID

CONFIG_FILE = "config.json"
BACKUP_DEST = r"C:\檔案備份地點"
BACKUP_CYCLE_DAYS = 5


def select_multiple_folders():
    folders = []
    root = Tk()
    root.withdraw()  # 隱藏主視窗，只有文件選擇框顯示

    while True:
        folder = filedialog.askdirectory(title="選擇要備份的資料夾")
        if folder:
            folders.append(folder)
        else:
            break

        continue_select = messagebox.askyesno("新增資料夾", "是否要再選取一個資料夾？")
        if not continue_select:
            break

    root.destroy()  # 關閉 Tkinter 視窗
    return folders

def save_config(folders):  #檔案存入JSON中
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump({"folders": folders}, f, indent=4)

def load_config():  #再次存檔時確認已記錄資料夾
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("folders", [])
    return []

def create_timestamp_folder(base_path):  #備份時間戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(base_path, f"backup_{timestamp}")
    os.makedirs(path, exist_ok=True)
    return path

def backup_data(src_list, dest_base):  #備份
    dest = create_timestamp_folder(dest_base)
    for src in src_list:
        if os.path.exists(src):
            folder_name = os.path.basename(src.rstrip("/\\"))
            dest_path = os.path.join(dest, folder_name)
            shutil.copytree(src, dest_path)
            print(f"備份完成：{src} -> {dest_path}")
        else:
            print(f"跳過：找不到 {src}")

def cleanup_old_backups(dest_base, keep=5):  #清理
    backups = sorted([f for f in os.listdir(dest_base) if f.startswith("backup_")])
    if len(backups) > keep:
        for folder in backups[:-keep]:
            full_path = os.path.join(dest_base, folder)
            shutil.rmtree(full_path)
            print(f"已刪除過期備份：{full_path}")



def main():
    os.makedirs(BACKUP_DEST, exist_ok=True)

    folders = load_config()

    # 有設定過，進入選單流程
    if folders:
        print("目前設定的備份資料夾：")
        for i, f in enumerate(folders, 1):
            print(f"  {i}. {f}")

        print("\n請選擇操作：")
        print("1. 使用原有資料夾備份")
        print("2. 新增資料夾到原有設定")
        print("3. 清除全部設定並重新選擇")
        print("4. 設定外接裝置資訊(需插入USB)")

        choice = input("輸入選項 (1/2/3/4)：")

        if choice == "1":
            print("使用原設定開始備份...\n")
            backup_data(folders, BACKUP_DEST) 
            cleanup_old_backups(BACKUP_DEST, BACKUP_CYCLE_DAYS)
            pass

        elif choice == "2":
            new_folders = select_multiple_folders()
            if new_folders:
                for folder in new_folders:
                    if folder not in folders:
                        folders.append(folder)
                save_config(folders)
                print("新資料夾已加入設定，開始備份\n")
                
            else:
                print("未新增任何資料夾，維持原設定")
            
            backup_data(folders, BACKUP_DEST) 
            cleanup_old_backups(BACKUP_DEST, BACKUP_CYCLE_DAYS)

        elif choice == "3":
            print("開始重新選擇備份資料夾")

            folders = select_multiple_folders()
            if folders:
                save_config(folders)
                print("設定已重設，開始備份\n")
            else:
                print("未選擇任何資料夾，取消清除")
                return  
            
            backup_data(folders, BACKUP_DEST)
            cleanup_old_backups(BACKUP_DEST, BACKUP_CYCLE_DAYS)

        elif choice == "4":
            while True:
                print(f'請確認此槽是否為欲備份資料的外接裝置目的地----{detect()[0]['DriveLetter']}(y/n)：')
                a = input()
                if a == "y" or a == "Y":
                    save_config_INFO(detect())
                    backup_data(folders, USB_BACKUP_DEST)
                    cleanup_old_backups(USB_BACKUP_DEST, BACKUP_CYCLE_DAYS)
                    break
                else:
                    continue

    else:
        # 第一次使用
        print("初次使用，請選擇要備份的資料夾")
        folders = select_multiple_folders()
        if not folders:
            print("沒有選擇資料夾，程式結束。")
            return
        save_config(folders)
        backup_data(folders, BACKUP_DEST)


