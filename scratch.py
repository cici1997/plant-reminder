import sqlite3
import datetime
import cv2
import os
from tkinter import Tk, filedialog

DB_NAME = 'plants.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            water_interval INTEGER,
            last_watered DATE,
            next_watering DATE,
            photo_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

def take_photo(filename='plant_photo.jpg'):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        return None
    print("按空格拍照，ESC退出")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头画面")
            break
        cv2.imshow('拍照窗口', frame)
        key = cv2.waitKey(1)
        if key == 27:  # ESC
            print("已退出拍照")
            break
        elif key == 32:  # 空格
            cv2.imwrite(filename, frame)
            print(f"照片已保存为 {filename}")
            cap.release()
            cv2.destroyAllWindows()
            return filename
    cap.release()
    cv2.destroyAllWindows()
    return None

def choose_photo():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="选择植物照片",
        filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp")]
    )
    root.destroy()
    if file_path:
        print(f"已选择图片：{file_path}")
        return file_path
    else:
        print("未选择图片")
        return None

def add_plant():
    name = input("请输入植物名称：")
    interval = int(input("请输入浇水间隔（天）："))
    print("请选择照片方式：1-拍照  2-选择本地图片  3-不添加")
    photo_choice = input("请输入选项：")
    photo_path = None
    if photo_choice == '1':
        photo_path = take_photo(f"{name}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
    elif photo_choice == '2':
        photo_path = choose_photo()
    today = datetime.date.today()
    next_watering = today + datetime.timedelta(days=interval)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO plants (name, water_interval, last_watered, next_watering, photo_path)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, interval, today, next_watering, photo_path))
    conn.commit()
    conn.close()
    print(f"已添加植物：{name}")

def list_plants():
    today = datetime.date.today()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id, name, water_interval, last_watered, next_watering, photo_path FROM plants')
    rows = c.fetchall()
    if not rows:
        print("暂无植物，请先添加。")
    else:
        print("\n植物列表：")
        for row in rows:
            id, name, interval, last_watered, next_watering, photo_path = row
            overdue = ""
            next_date = datetime.datetime.strptime(next_watering, "%Y-%m-%d").date()
            if next_date < today:
                overdue = "【已逾期！】"
            elif next_date == today:
                overdue = "【今天要浇水！】"
            elif next_date == today + datetime.timedelta(days=1):
                overdue = "【明天要浇水】"
            print(f"{id}. {name} | 下次浇水日: {next_watering} {overdue} | 照片: {photo_path or '无'}")
    conn.close()

def water_plant():
    list_plants()
    pid = input("请输入要打卡浇水的植物编号：")
    today = datetime.date.today()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT water_interval FROM plants WHERE id=?', (pid,))
    result = c.fetchone()
    if not result:
        print("未找到该植物。")
    else:
        interval = result[0]
        next_watering = today + datetime.timedelta(days=interval)
        c.execute('''
            UPDATE plants
            SET last_watered=?, next_watering=?
            WHERE id=?
        ''', (today, next_watering, pid))
        conn.commit()
        print("浇水打卡成功！")
    conn.close()

def main():
    init_db()
    while True:
        print("\n==== 我的植物浇水提醒 ====")
        print("1. 添加植物")
        print("2. 浇水打卡")
        print("3. 查看植物列表")
        print("0. 退出")
        choice = input("请选择操作：")
        if choice == '1':
            add_plant()
        elif choice == '2':
            water_plant()
        elif choice == '3':
            list_plants()
        elif choice == '0':
            print("再见！")
            break
        else:
            print("无效选择，请重试。")

if __name__ == '__main__':
    main()