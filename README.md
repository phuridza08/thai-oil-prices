# ⛽ ราคาน้ำมันไทย — Thai Oil Prices

หน้าเว็บแสดงราคาน้ำมันขายปลีก กรุงเทพฯ และปริมณฑล (PTT, Bangchak, Shell, Esso, Caltex) เปรียบเทียบกับเมื่อวาน + กราฟย้อนหลัง 30 วัน

อัปเดตอัตโนมัติทุกวัน **07:00 น.** ผ่าน GitHub Actions

## โครงสร้าง

```
thai-oil-prices/
├── index.html                  หน้าเว็บ (Tailwind + Chart.js ผ่าน CDN)
├── app.js                      JS render การ์ด/ตาราง/กราฟ
├── data/prices.json            ราคา 30 วันล่าสุด (auto-updated)
├── scraper/
│   ├── scrape.py               orchestrator
│   ├── requirements.txt
│   └── brands/                 scraper รายแบรนด์
│       ├── ptt.py              ← scrape pttor.com
│       ├── bangchak.py         ← JSON API
│       ├── shell.py            ← via checkraka.com
│       ├── esso.py             ← mirror Bangchak (Esso = BSRC)
│       └── caltex.py           ← mirror Bangchak (SPA scrape ไม่ได้)
└── .github/workflows/daily.yml cron 00:00 UTC = 07:00 ICT
```

## วิธี deploy ครั้งแรก

### 1. ส่งโค้ดขึ้น GitHub
ในโฟลเดอร์โปรเจกต์ เปิด PowerShell:
```powershell
git init
git branch -M main
git add .
git commit -m "init: thai oil prices"
git remote add origin https://github.com/<USERNAME>/thai-oil-prices.git
git push -u origin main
```

### 2. เปิด GitHub Pages
1. ไปที่ repo → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: **main**, Folder: **/ (root)**
4. Save → รออีก ~1 นาทีจะได้ URL `https://<USERNAME>.github.io/thai-oil-prices/`

### 3. ตรวจ permission ของ Actions
1. **Settings** → **Actions** → **General**
2. ส่วน "Workflow permissions" เลือก **Read and write permissions**
3. Save (ถ้าไม่ทำขั้นนี้ Action จะ commit prices.json ไม่ได้)

### 4. รัน workflow ครั้งแรก (manual)
1. ไปที่ tab **Actions** ใน repo
2. เลือก workflow **Daily oil price scrape** ทางซ้าย
3. กด **Run workflow** → **Run workflow**
4. รอ ~1-2 นาที จะเห็น `data/prices.json` ถูกอัปเดต และมี commit ใหม่

หลังจากนั้นจะรันอัตโนมัติทุก 07:00 ICT

## รันเทสบนเครื่องตัวเอง
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r scraper\requirements.txt
.\.venv\Scripts\python.exe scraper\scrape.py
```
แล้วเปิด `index.html` ใน browser (ผ่าน Live Server ใน VS Code หรือ `python -m http.server`)

## ข้อจำกัด & หมายเหตุ

- **Esso** ปั๊มทั่วประเทศถูก Bangchak (BSRC) ซื้อตั้งแต่ปี 2566 → ราคาเหมือน Bangchak ทุกประการ
- **Caltex** เว็บไซต์เป็น JS SPA scrape ตรงๆ ไม่ได้ → ใช้ Bangchak เป็น proxy (ราคาในกรุงเทพฯ เกือบเท่ากันเสมอ)
- **Shell** ดึงจาก checkraka.com (เว็บ Shell ก็เป็น SPA) — ราคาอาจช้ากว่าจริง 1-2 วัน
- ราคาทั้งหมดเป็นช่วง **กรุงเทพฯ และปริมณฑล** เท่านั้น
- ถ้า scraper พังเฉพาะแบรนด์ใด → ใช้ค่าเมื่อวานต่อ + log error ไม่ทำให้แบรนด์อื่นพัง

## ถ้า scraper พังในอนาคต

เว็บแหล่งข้อมูล redesign → ต้องแก้ scraper ตัวที่พัง:
1. ดู log ใน tab **Actions** → คลิก run ล่าสุด → ดูข้อความ FAIL
2. แก้ไฟล์ `scraper/brands/<brand>.py`
3. commit + push → workflow รันใหม่อัตโนมัติวันถัดไป หรือกด Run workflow มือ

## License
MIT — ใช้/แก้ได้ตามสะดวก
