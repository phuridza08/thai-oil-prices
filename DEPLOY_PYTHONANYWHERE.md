# Deploy บน PythonAnywhere

ทำตาม **4 ขั้นตอน** หลังจากสมัครและ login เข้า PythonAnywhere แล้ว

> **สำคัญ:** ตั้งรหัส PythonAnywhere ให้**ต่างจาก GitHub/email อื่น** — ห้ามใช้ซ้ำ

---

## ขั้นตอนที่ 1 — Upload ไฟล์ project

1. คลิก tab **Files** (มุมขวาบน)
2. คุณจะอยู่ที่ `/home/<USERNAME>/`
3. ที่ panel ล่างขวา "Upload a file" → กด **Choose file** → เลือก **`thai-oil-prices.zip`** ที่ผมเตรียมให้
4. รอ upload (~5-10 วินาที)

## ขั้นตอนที่ 2 — Unzip + ติดตั้ง dependencies

1. กลับไปหน้า dashboard → tab **Consoles** → กด **Bash**
2. พิมพ์คำสั่งทีละบรรทัด (กด Enter หลังแต่ละบรรทัด):

```bash
cd ~
unzip thai-oil-prices.zip
cd thai-oil-prices
pip3.10 install --user -r scraper/requirements.txt
python3.10 scraper/scrape.py
```

บรรทัดสุดท้ายเป็นการ test scraper — ถ้าขึ้น `[ptt] OK (8/8 ...)` ครบ 5 แบรนด์ = ใช้ได้

## ขั้นตอนที่ 3 — สร้าง Web App

1. tab **Web** → **Add a new web app** → **Next**
2. Domain: `<USERNAME>.pythonanywhere.com` (ใช้ฟรีอันนี้) → **Next**
3. เลือก **Flask** → **Next**
4. Python version: **Python 3.10** → **Next**
5. Path: เปลี่ยนเป็น **`/home/<USERNAME>/thai-oil-prices/flask_app.py`** → **Next**
6. รอสักครู่ จะเข้าหน้า Web config

7. เลื่อนหา section **WSGI configuration file** → คลิกชื่อไฟล์ → จะเปิด editor
8. **ลบทุกอย่าง** แล้ววางโค้ดนี้ (แก้ `<USERNAME>` เป็นชื่อจริง):

```python
import sys
path = '/home/<USERNAME>/thai-oil-prices'
if path not in sys.path:
    sys.path.insert(0, path)
from flask_app import app as application
```

9. กด **Save** (มุมขวาบนของ editor)
10. กลับไป Web tab → กดปุ่ม **Reload** สีเขียวด้านบน
11. คลิกลิงก์ `https://<USERNAME>.pythonanywhere.com` → จะเห็นเว็บราคาน้ำมัน 🎉

## ขั้นตอนที่ 4 — ตั้ง cron 07:00 ICT ทุกวัน

1. tab **Tasks** (ถ้าหาไม่เจอ คลิก dashboard → ในเมนูซ้าย)
2. ที่ "Schedule a new task":
   - Daily at: **00:00** (UTC = 07:00 ICT)
   - Command: `python3.10 /home/<USERNAME>/thai-oil-prices/scraper/scrape.py`
3. กด **Create**

เสร็จ — ทุกวัน 07:00 จะ scrape ราคาใหม่ แล้วเว็บอัปเดตอัตโนมัติ

---

## ตรวจสอบ

- เว็บ: `https://<USERNAME>.pythonanywhere.com`
- ดู task log: Tasks tab → กดชื่อ task → ดู output
- ถ้า scraper พัง: Web tab → "Error log" + "Server log"

## หมายเหตุข้อจำกัด PythonAnywhere free tier

- เว็บจะ **inactive** หลัง 3 เดือนถ้าไม่ login → log in ทุก 2 เดือนเพื่อรักษา
- CPU 100 วินาที/วัน — โปรเจกต์นี้ใช้ ~5 วินาที/วัน เหลือเฟือ
- ไม่รองรับ custom domain — ใช้ `*.pythonanywhere.com` ได้
