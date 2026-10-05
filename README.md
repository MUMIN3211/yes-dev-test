# Luma Skin Care

ระบบจัดการสินค้า Skin Care: นำเข้าสินค้าจาก Excel สร้าง QR ให้สินค้าแต่ละชิ้น และเมื่อลูกค้าสแกน QR จะเห็นหน้าข้อมูลสินค้านั้น

> แผนงานเริ่มต้นอยู่ที่ [plan.md](plan.md) ส่วนที่ต่างจากแผนบันทึกไว้ในหัวข้อ [สิ่งที่ต่างจากแผนงาน](#สิ่งที่ต่างจากแผนงาน)

## โครงสร้างโปรเจกต์

```
backend/    FastAPI (Python)   router → service → repository → Supabase
frontend/   Next.js (React) + JavaScript + CSS Modules
supabase/   schema.sql (โครงสร้างตาราง), seed.sql (ข้อมูลตัวอย่าง)
```

ลำดับการทำงาน: หน้าเว็บ Next.js → เรียก FastAPI → อ่าน/เขียน Supabase
(frontend ไม่ได้ต่อกับ Supabase โดยตรง และไม่ได้ถือ key ใด ๆ)

## วิธีติดตั้งและรันระบบ

ต้องมี Node.js 18.18 ขึ้นไป, Python 3.11 ขึ้นไป และ Supabase project

### 1. Database (Supabase)

ไปที่ Supabase Dashboard → SQL Editor แล้วรัน
1. [supabase/schema.sql](supabase/schema.sql) เพื่อสร้างตาราง (รันซ้ำได้)
2. [supabase/seed.sql](supabase/seed.sql) เพื่อใส่ข้อมูลตัวอย่าง (ไม่บังคับ)

หรือรันผ่านสคริปต์ ซึ่งต้องตั้งค่า `DATABASE_URL` ใน `backend/.env` ก่อน:
```powershell
cd backend
python scripts/init_db.py --seed
```

### 2. Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

ค่าที่ต้องใส่ใน `backend/.env` (ดูได้จาก Supabase Dashboard → Project Settings):

| ตัวแปร | ค่า |
|---|---|
| `SUPABASE_URL` | `https://<project-ref>.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Secret key (`sb_secret_...`) หรือ legacy `service_role` key |
| `DATABASE_URL` | Connection string แบบ Shared pooler (ใช้เฉพาะ `init_db.py`) |
| `CORS_ORIGINS` | URL ของ frontend คั่นด้วย `,` |

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- ถ้าแก้ `.env` ต้องปิดแล้วรันใหม่ เพราะ `--reload` ดูเฉพาะไฟล์ `.py`

### 3. Frontend

```powershell
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

เปิด http://localhost:3000 (ถ้า port ชน ให้ใช้ `npm run dev -- -p 3100` และเพิ่ม origin นั้นใน `CORS_ORIGINS`)

### บัญชี Super Admin สำหรับทดสอบ

_จะเพิ่มเมื่อทำ Feature 2 (Authentication) เสร็จ_

## Tech stack และเหตุผลที่เลือก

| ส่วน | เลือกใช้ | เหตุผล |
|---|---|---|
| Frontend | Next.js 15 (App Router) + JavaScript + CSS Modules | render หน้าสินค้าฝั่ง server ทำให้เปิดจากการสแกน QR บนมือถือได้เร็ว และ CSS Modules แยก style ตาม component โดยไม่ต้องใช้ library เพิ่ม |
| Backend | FastAPI | validate ข้อมูลด้วย Pydantic ได้ในตัว ซึ่งจำเป็นสำหรับการตรวจแถวที่ผิดใน Excel และมี Swagger docs ให้อัตโนมัติ |
| Database | Supabase (PostgreSQL) | ใช้ CHECK constraint บังคับรูปแบบข้อมูลที่ระดับ database ได้ และมี Auth กับ Storage สำหรับ Feature ถัดไป |

## สถานะฟีเจอร์

| # | Feature | สถานะ |
|---|---|---|
| 1 | Landing Page: แสดงสินค้าสาธารณะ + หน้าสินค้าจาก QR | ✅ เสร็จ |
| 2 | Authentication Login (Admin / Super Admin) | ⏳ ยังไม่เริ่ม |
| 3 | Add Product (Import Excel) | ⏳ ยังไม่เริ่ม |
| 4 | Generate QR Code | ⏳ ยังไม่เริ่ม |
| 5 | Edit Product (ข้อมูล, รูปภาพ) | ⏳ ยังไม่เริ่ม |
| 6 | Adjust QR Code (สีพื้นหลัง, ดาวน์โหลด PNG) | ⏳ ยังไม่เริ่ม |

**Feature 1 ประกอบด้วย**
- หน้า `/` แสดงสินค้าที่ `status = active` ทั้งหมด ค้นหาด้วยชื่อหรือ SKU ได้ และกรองตามหมวดหมู่ได้
- หน้า `/products/{sku}` แสดงรายละเอียด ราคา ขนาด และวิธีใช้ ซึ่งเป็น URL ที่ QR จะชี้มา
- สินค้า `inactive` หรือ SKU ที่ไม่มีอยู่จะแสดงหน้า "ไม่พบสินค้านี้" (HTTP 404)
- สินค้าที่ยังไม่มีรูป หรือรูปโหลดไม่ขึ้น จะแสดงรูป placeholder แทน
- ออกแบบให้ใช้บนมือถือก่อน (mobile-first) และรองรับ dark mode

## สิ่งที่ต่างจากแผนงาน

| แผนเดิม (plan.md) | สิ่งที่ทำจริง | เหตุผล |
|---|---|---|
| `sku` เป็นชนิด `numeric` | `sku` เป็น `text` และมี CHECK ให้ตรงรูปแบบ `LS-0000` | รูปแบบ `LS-0000` มีตัวอักษรและขีด จึงเก็บเป็นตัวเลขไม่ได้ |
| แยก 2 ตาราง `luma_products` และ `luma_products_update` | ใช้ตาราง `products` ตารางเดียว ส่วนการ import ครั้งที่สองจะ upsert ตาม `sku` | QR ชี้ไปที่ `/products/{sku}` ถ้าแยกตาราง QR ที่พิมพ์ไปแล้วจะไม่เห็นข้อมูลใหม่ ซึ่งขัดกับข้อกำหนด "แก้ไขข้อมูลได้โดย QR ที่พิมพ์ไปแล้วยังใช้งานได้" |
| ไม่ได้ระบุคอลัมน์รูปภาพและเวลา | เพิ่ม `id` (uuid), `image_url`, `created_at`, `updated_at` | เตรียมไว้สำหรับ Feature 5 (อัปโหลดรูป) และใช้ติดตามการแก้ไข |

## สมมติฐานและข้อตัดสินใจ

- **URL ของ QR ใช้ SKU** (`/products/LS-0001`) แทน id เพราะอ่านง่าย และ SKU ไม่เปลี่ยน
- **SKU ใน URL ไม่สนตัวพิมพ์เล็กใหญ่** (`/products/ls-0001` ใช้ได้) เผื่อกรณีพิมพ์ URL เอง
- **status ว่างถือเป็น active:** บังคับด้วย trigger ใน database จึงมีผลกับการเขียนข้อมูลทุกช่องทาง ไม่ใช่เฉพาะตอน import
- **หมวดหมู่สินค้าเป็นภาษาอังกฤษตาม Excel:** UI ส่วนอื่นเป็นภาษาไทย
- **Backend ใช้ service_role key:** ตาราง `products` เปิด RLS ไว้แต่ไม่มี policy ให้ public ดังนั้นเข้าถึงข้อมูลได้ผ่าน FastAPI ทางเดียว

## การใช้ AI

_จะสรุปเมื่อจบงาน: ใช้ทำอะไร, ตัวอย่าง prompt, จุดที่ AI ผิดพลาดและวิธีแก้, ส่วนที่เขียนเอง_
