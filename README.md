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

แล้วสร้างบัญชี Super Admin คนแรก (ไม่มีหน้าสมัครสมาชิก จึงต้องสร้างผ่านสคริปต์นี้):
```powershell
python scripts/create_super_admin.py superadmin@example.com "Luma@2026"
```
ถ้าอีเมลนี้มีอยู่แล้ว สคริปต์จะรีเซ็ตรหัสผ่านและเปิดใช้งานบัญชีให้

### 2. Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # ครั้งแรกเท่านั้น! คำสั่งนี้เขียนทับ .env เดิม
uvicorn app.main:app --reload --port 8000
```

ค่าที่ต้องใส่ใน `backend/.env` (ดูได้จาก Supabase Dashboard → Project Settings):

| ตัวแปร | ค่า |
|---|---|
| `SUPABASE_URL` | `https://<project-ref>.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Secret key (`sb_secret_...`) หรือ legacy `service_role` key |
| `DATABASE_URL` | Connection string แบบ Shared pooler (ใช้เฉพาะ `init_db.py`) |
| `CORS_ORIGINS` | URL ของ frontend คั่นด้วย `,` |
| `JWT_SECRET` | สตริงสุ่มยาว ๆ สำหรับเซ็น token (สร้างด้วย `python -c "import secrets; print(secrets.token_urlsafe(48))"`) |
| `FRONTEND_URL` | URL ของ frontend ใช้สร้างลิงก์ในอีเมลคำเชิญ (`{FRONTEND_URL}/invite`) ต้องเพิ่มใน Redirect URLs ของ Supabase ด้วย |

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- ถ้าแก้ `.env` ต้องปิดแล้วรันใหม่ เพราะ `--reload` ดูเฉพาะไฟล์ `.py`

### 3. Frontend

```powershell
cd frontend
npm install
copy .env.example .env.local   # ครั้งแรกเท่านั้น
npm run dev
```

เปิด http://localhost:3000 (ถ้า port ชน ให้ใช้ `npm run dev -- -p 3100` และเพิ่ม origin นั้นใน `CORS_ORIGINS`)

### บัญชี Super Admin สำหรับทดสอบ

| อีเมล | รหัสผ่าน |
|---|---|
| `superadmin@example.com` | `Luma@2026` |

เข้าสู่ระบบที่ http://localhost:3000/login (หรือกดลิงก์ "สำหรับผู้ดูแล" มุมขวาบน)

**ทดสอบการเชิญ Admin:** เข้าเมนู "จัดการผู้ใช้" แล้วกรอกอีเมล Supabase จะส่งอีเมลคำเชิญไปให้ ผู้ถูกเชิญกดลิงก์ในอีเมลแล้วจะเข้าหน้าสมัคร `/invite` ซึ่งแสดงอีเมลที่ได้รับเชิญและชื่อ Super Admin ที่เชิญ จากนั้นตั้งรหัสผ่านและยืนยันรหัสผ่าน แล้วเข้าสู่ระบบด้วยบัญชีใหม่

### ตั้งค่า Supabase Auth (สำหรับอีเมลคำเชิญ)

1. **Redirect URL:** ไปที่ Supabase Dashboard → Authentication → URL Configuration แล้วเพิ่ม `http://localhost:3000/invite` ใน Redirect URLs (ถ้าไม่ได้เพิ่ม Supabase จะส่งไปที่ Site URL แทน แต่หน้าเว็บจะส่งต่อไป `/invite` ให้อัตโนมัติ)
2. **การส่งอีเมล:** ระบบอีเมลเริ่มต้นของ Supabase ส่งได้เฉพาะอีเมลของสมาชิกในทีมและจำกัดจำนวนต่อชั่วโมง จึงต้องตั้งค่า Custom SMTP ที่ Authentication → Emails → SMTP Settings โปรเจกต์นี้ใช้ **Gmail SMTP** ซึ่งเชิญอีเมลไหนก็ได้และไม่ต้องมี domain ของตัวเอง:
   - เปิด 2-Step Verification ของบัญชี Google แล้วสร้าง App Password ที่ https://myaccount.google.com/apppasswords (ได้รหัส 16 ตัวอักษร)
   - Host `smtp.gmail.com`, Port `587`, Username = อีเมล Gmail, Password = App Password (ไม่ใช่รหัสผ่าน Gmail ปกติ)
   - Sender email = อีเมล Gmail เดียวกับ Username
   - ข้อจำกัด: Gmail ส่งได้ประมาณ 500 ฉบับต่อวัน ซึ่งเพียงพอสำหรับการเชิญ Admin
3. **ข้อความในอีเมล (ไม่บังคับ):** แก้ได้ที่ Authentication → Emails → Templates → Invite user

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
| 2 | Authentication Login (Admin / Super Admin) | ✅ เสร็จ |
| 3 | Add Product (Import Excel) | ✅ เสร็จ |
| 4 | Generate QR Code | ⏳ ยังไม่เริ่ม |
| 5 | Edit Product (ข้อมูล, รูปภาพ) | ⏳ ยังไม่เริ่ม |
| 6 | Adjust QR Code (สีพื้นหลัง, ดาวน์โหลด PNG) | ⏳ ยังไม่เริ่ม |

**Feature 1 ประกอบด้วย**
- หน้า `/` แสดงสินค้าที่ `status = active` ทั้งหมด ค้นหาด้วยชื่อหรือ SKU ได้ และกรองตามหมวดหมู่ได้
- หน้า `/products/{sku}` แสดงรายละเอียด ราคา ขนาด และวิธีใช้ ซึ่งเป็น URL ที่ QR จะชี้มา
- สินค้า `inactive` หรือ SKU ที่ไม่มีอยู่จะแสดงหน้า "ไม่พบสินค้านี้" (HTTP 404)
- สินค้าที่ยังไม่มีรูป หรือรูปโหลดไม่ขึ้น จะแสดงรูป placeholder แทน
- ออกแบบให้ใช้บนมือถือก่อน (mobile-first) และรองรับ dark mode

**Feature 2 ประกอบด้วย**
- หน้า `/login` สำหรับเข้าสู่ระบบ ไม่มีหน้าสมัครสมาชิก
- หลังบ้าน `/admin`: ถ้ายังไม่ได้ login จะถูกส่งไปหน้า login แล้วกลับมาหน้าเดิมหลัง login สำเร็จ
- หน้า `/admin/users` (เฉพาะ Super Admin) ใช้เชิญ Admin ทางอีเมล ดูและยกเลิกคำเชิญที่รอยืนยัน และเปิด/ปิดการใช้งานบัญชี Admin
- หน้า `/invite` (หน้าสมัครเฉพาะสำหรับผู้ถูกเชิญ) แสดงอีเมลที่ได้รับเชิญและ Super Admin ที่เชิญ ให้ตั้งรหัสผ่านพร้อมยืนยันรหัสผ่านเอง

**Feature 3 ประกอบด้วย**
- หน้า `/admin/products/import` เลือกไฟล์ .xlsx แล้วกด "ตรวจสอบไฟล์" ระบบแสดงตัวอย่างก่อน (ยังไม่บันทึก) จากนั้นกด "ยืนยันนำเข้า"
- ตัวอย่างแสดงจำนวนแถว เพิ่มใหม่ / อัปเดต / ไม่เปลี่ยนแปลง / ข้อมูลไม่ถูกต้อง พร้อม **เลขแถวใน Excel และเหตุผล** ของแถวที่ผิด และค่าเดิม → ค่าใหม่ของแถวที่จะถูกอัปเดต
- แถวที่ผิดจะถูกข้ามโดยไม่กระทบแถวอื่น แถวที่ถูกต้องจะ upsert ตาม `sku` (ไม่แตะ `image_url` จึงไม่ลบรูปเดิม)
- API: `POST /api/admin/products/import` (multipart: `file`, `dry_run`)

ผลกับไฟล์ตัวอย่าง:

| ไฟล์ | แถวข้อมูล | นำเข้าได้ | ไม่ถูกต้อง |
|---|---|---|---|
| `luma_products.xlsx` | 30 (ข้ามแถวว่าง 1 แถว) | 21 | 9: ไม่มีชื่อ (แถว 6), ราคา "ราคาพิเศษ" (9), SKU LS-1004 ซ้ำ (12), ไม่มี SKU (15), ราคาติดลบ (17), status "yes" (20), category "Lotion" (23), ไม่มี category (30), ไม่มี category + ราคา 0 (31) |
| `luma_products_update.xlsx` | 6 | 5 (อัปเดต 3: LS-1001 ราคาและคำอธิบาย, LS-1003 ขนาดและคำอธิบาย, LS-1010 → inactive / เพิ่มใหม่ 2) | 1: ไม่มีชื่อ (แถว 7) |

**สิทธิ์ของแต่ละ Role**

| ทำอะไรได้ | Admin | Super Admin |
|---|:---:|:---:|
| เข้าหลังบ้าน | ✅ | ✅ |
| จัดการสินค้า (Feature 3–6) | ✅ | ✅ |
| เชิญ Admin ใหม่ / ยกเลิกคำเชิญ | ❌ | ✅ |
| เปิด/ปิดการใช้งานบัญชี Admin | ❌ | ✅ |

## สิ่งที่ต่างจากแผนงาน

| แผนเดิม (plan.md) | สิ่งที่ทำจริง | เหตุผล |
|---|---|---|
| `sku` เป็นชนิด `numeric` | `sku` เป็น `text` และมี CHECK ให้ตรงรูปแบบ `LS-0000` | รูปแบบ `LS-0000` มีตัวอักษรและขีด จึงเก็บเป็นตัวเลขไม่ได้ |
| แยก 2 ตาราง `luma_products` และ `luma_products_update` | ใช้ตาราง `products` ตารางเดียว ส่วนการ import ครั้งที่สองจะ upsert ตาม `sku` | QR ชี้ไปที่ `/products/{sku}` ถ้าแยกตาราง QR ที่พิมพ์ไปแล้วจะไม่เห็นข้อมูลใหม่ ซึ่งขัดกับข้อกำหนด "แก้ไขข้อมูลได้โดย QR ที่พิมพ์ไปแล้วยังใช้งานได้" |
| ไม่ได้ระบุคอลัมน์รูปภาพและเวลา | เพิ่ม `id` (uuid), `image_url`, `created_at`, `updated_at` | เตรียมไว้สำหรับ Feature 5 (อัปโหลดรูป) และใช้ติดตามการแก้ไข |
| ตาราง `admins` มีคอลัมน์ `password` | ไม่เก็บรหัสผ่านในตาราง `admins` แต่ให้ Supabase Auth (`auth.users`) เก็บแทน | Supabase Auth hash และจัดการรหัสผ่านให้ ส่วนตาราง `admins` เก็บแค่ role และสถานะ โดย `id` อ้างอิง `auth.users` |
| ระบุ "Authentication -> Users -> Add user" ของ Supabase | ใช้ Supabase Auth ส่งอีเมลคำเชิญและตรวจรหัสผ่าน แต่ทุกการเรียกยังผ่าน FastAPI ซึ่งออก JWT ของตัวเองที่มี role อยู่ข้างใน | ใช้ระบบส่งอีเมลจริงและการจัดการรหัสผ่านของ Supabase โดยยังคงลำดับการทำงาน Next.js → FastAPI → Supabase ตามแผน และตรวจ role/สถานะจากตาราง `admins` ได้ทุก request |
| ไม่ได้ระบุสถานะคำเชิญ | เพิ่มคอลัมน์ `invited_by`, `invited_at`, `activated_at` ในตาราง `admins` | ถ้า `activated_at` ว่าง แปลว่ายังไม่ได้กดลิงก์ตั้งรหัสผ่าน (คำเชิญรอยืนยัน) และยังเข้าสู่ระบบไม่ได้ |

## สมมติฐานและข้อตัดสินใจ

- **URL ของ QR ใช้ SKU** (`/products/LS-0001`) แทน id เพราะอ่านง่าย และ SKU ไม่เปลี่ยน
- **SKU ใน URL ไม่สนตัวพิมพ์เล็กใหญ่** (`/products/ls-0001` ใช้ได้) เผื่อกรณีพิมพ์ URL เอง
- **status ว่างถือเป็น active:** บังคับด้วย trigger ใน database จึงมีผลกับการเขียนข้อมูลทุกช่องทาง ไม่ใช่เฉพาะตอน import
- **หมวดหมู่สินค้าเป็นภาษาอังกฤษตาม Excel:** UI ส่วนอื่นเป็นภาษาไทย
- **Token เก็บใน httpOnly cookie ของ Next.js:** JavaScript ฝั่ง browser อ่าน token ไม่ได้ ส่วน Next.js ฝั่ง server เป็นตัวแนบ token ไปเรียก FastAPI
- **ตรวจสถานะบัญชีทุก request:** ปิดการใช้งาน Admin แล้วมีผลทันที แม้ token เดิมจะยังไม่หมดอายุ
- **คำเชิญ:** เชิญได้เฉพาะ role Admin ลิงก์ใช้ได้ครั้งเดียว และอายุของลิงก์เป็นไปตามค่าของ Supabase (Authentication → Providers → Email → Email OTP Expiration) ถ้ากด "ส่งอีกครั้ง" หรือเชิญอีเมลเดิมซ้ำ ลิงก์เก่าจะใช้ไม่ได้ ส่วน "ยกเลิกคำเชิญ" จะลบผู้ใช้ออกจาก Supabase Auth
- **Token ในลิงก์คำเชิญ:** Supabase ส่ง token มาใน URL fragment (`#access_token=...`) หน้าเว็บจะลบออกจากแถบที่อยู่ทันที และส่งให้ backend ผ่าน body ของ request (ไม่อยู่ใน URL)
- **ข้อจำกัดของ Super Admin:** ปิดการใช้งานบัญชีตัวเองไม่ได้ และปิดบัญชี Super Admin คนอื่นไม่ได้ เพื่อป้องกันไม่ให้ระบบไม่เหลือ Super Admin
- **ข้อความ login ผิด:** แสดงข้อความเดียวกันทั้งกรณีไม่มีอีเมลนี้และรหัสผ่านผิด เพื่อไม่ให้ใช้หน้า login เดาว่าอีเมลไหนมีบัญชี
- **รหัสผ่าน:** อย่างน้อย 8 ตัวอักษร
- **Import Excel ปรับข้อมูลที่ตีความได้ชัดเจนให้อัตโนมัติ และแจ้งเป็นคำเตือน:** SKU มีช่องว่าง/ตัวพิมพ์เล็ก (`" LS-1024 "`, `ls-1030`), ราคาเป็นข้อความที่มี `,` `฿` หรือ "บาท" (`"1,290"`), category และ status ไม่สนตัวพิมพ์เล็กใหญ่ ส่วนข้อมูลที่ต้องเดา (ราคา "ราคาพิเศษ", category "Lotion") จะถูกปฏิเสธ
- **SKU ซ้ำในไฟล์เดียวกัน:** ใช้แถวแรกและปฏิเสธแถวถัดไป (เช่น LS-1004 แถว 12 "Calm Cica Toner Refill" มีชื่อและราคาต่างจากแถว 5 จึงไม่ควรเดาว่าแถวไหนถูก)
- **Excel คือข้อมูลหลักตอน import:** แถวที่ถูกต้องจะเขียนทับทุกคอลัมน์ในไฟล์ (ช่องว่างใน Excel = ค่าว่าง) ยกเว้นรูปภาพ ส่วนสินค้าที่ไม่อยู่ในไฟล์จะไม่ถูกลบหรือแก้ไข
- **แถวที่ไม่มีอะไรเปลี่ยน** จะไม่ถูกเขียนลง database (`updated_at` ไม่เปลี่ยน)
- **Backend ใช้ service_role key:** ทุกตารางเปิด RLS ไว้แต่ไม่มี policy ให้ public ดังนั้นเข้าถึงข้อมูลได้ผ่าน FastAPI ทางเดียว

## การใช้ AI

_จะสรุปเมื่อจบงาน: ใช้ทำอะไร, ตัวอย่าง prompt, จุดที่ AI ผิดพลาดและวิธีแก้, ส่วนที่เขียนเอง_
