# Luma Skin Care
เป้าหมาย : ระบบจัดการสินค้า Skin Care โดยการนำข้อมูล EXCEL และจะสร้าง QR แต่ละชิ้น เมื่อสแกน QR นั้นจะเห็นหน้าเว็บของสินค้าตัวนี้น (มีแค่เฉพาะ ADMIN และ SUPER ADMIN=>จะเป็นคนคอยกำหนด Role ของ User ไหนที่ต้องการเป็น Admin)

## Pharse 1
ผู้ใช้เมื่อเปิดเว็บไซต์แล้วสามารถ
- จะเห็นรายการทั้งหมดของสินค้าแต่ละชิ้น
- เพิ่มสินค้าจากการ Import จาก Excel 
- สินค้าแต่ละชิ้นจะมี QR เป็นของตัวเอง
- แก้ไขรูปภาพในแต่ละสินค้า อัปโหลดรูปภาพ สร้าง QR code ของตัวสินค้า ปรับแต่ง QR(เปลี่ยนสีพื้นหลัง และ Downlaod เป็นไฟล์ png ได้)
- เก็บ Log ทุกครั้งหากมีคตนเปิดหน้าสินค้าจาก QR และแสดงสินค้าโดยเรียงลำดับจากมากสุดไปต่ำสุด
- เมื่อเข้าระบบ USER จะถูกกำหนดเป็น ADMIN โดยจะต้องถูกส่งผ่าน SUPER ADMIN ก่อน

Feature ที่จะมีในเว็บไซต์ :
1. Feature 1 : Landing Page (Show pulic every product)
2. Feature 2 : Authentication Login (Role : Admin และ Super Admin)
3. Feature 3 : Add Product (Import Excel)
4. Feature 4 : Generate QR Code (Add Every Product)
5. Feature 5 : Edit Product (Edit QR,Description,Upload picture produc)
6. Feature 6 : Adjust QR Code (Can change background color & can Download png)

เรียงลำดับความสำคัญตอนเริ่มงาน :
- 1.หน้าสินค้าสาธารณะ: สแกน QR แล้วเห็นหน้าเว็บข้อมูลสินค้า ใช้งานบนมือถือได้ดี
- 2.Login ของ Admin: เข้าหลังบ้านได้เฉพาะผู้มีบัญชี ไม่มีหน้าสมัครสมาชิก
- 3.แยกสิทธิ์ผู้ใช้: มี 2 role คือ Super Admin และ Admin ต่างกันตามที่ผู้สอบออกแบบ แต่ Super Admin เท่านั้นที่เพิ่มผู้ใช้ได้
- 4.เชิญ Admin ทางอีเมล: Super Admin เพิ่ม Admin ใหม่ ระบบส่งอีเมลให้ผู้ถูกเชิญยืนยันและตั้งรหัสผ่านเอง (ใช้ Mailtrap หรือบันทึกอีเมลลง log แทนการส่งจริงได้)
- 5.Import Excel: นำเข้าสินค้าจากไฟล์ Excel ที่ให้ไว้ พร้อมแจ้งแถวที่ข้อมูลไม่ถูกต้อง
- 6.แก้ไขข้อมูลสินค้า: แก้ไขข้อมูลได้โดย QR ที่พิมพ์ไปแล้วยังใช้งานได้และแสดงข้อมูลใหม่
- 7.อัปโหลดรูปสินค้า: เพิ่มรูปให้สินค้าในหน้าแก้ไขสินค้า
- 8.สร้าง QR: สร้าง QR ให้สินค้าแต่ละชิ้นหลังนำเข้า
- 9.ปรับแต่ง QR: เปลี่ยนสีพื้นหลังและขนาด แล้วดาวน์โหลดเป็นไฟล์รูปได้
- 10.บันทึกการสแกน: เก็บ log ทุกครั้งที่มีคนเปิดหน้าสินค้าจาก QR และแสดงสินค้าที่ถูกดูมากที่สุด

เอกสารสินค้าจะทำการ Import ข้อมูลสินค้าทั้งหมด :
- Excel 2 ไฟล์ ไฟล์แรกใช้นำเข้าสินค้าครั้งแรก ไฟล์ที่สองใช้ทดสอบการนำเข้าซ้ำหลังจากสร้าง QR ไปแล้ว ไฟล์เหล่านี้จำลองข้อมูลจริงจากลูกค้า จึงมีบางแถวที่ข้อมูลไม่ถูกต้อง ให้เปิดดูข้อมูลก่อนเขียนแผนไฟล์
ใช้เมื่อ
- luma_products.xlsx
นำเข้าสินค้าครั้งแรก (ประมาณ 30 แถว)
- luma_products_update.xlsx
นำเข้าครั้งที่สอง หลังจากสร้าง QR แล้ว

เครื่องมือ Tools :
- Frontend : Next.js (React) + Javascript + CSS
- Backend : FastAPI (Python)
- Database : Supabase (PostgreSQL)
- ลำดับการทำงาน : หน้าเว็บ Next.js -> เรียก FastAPI -> อ่านเขียนจาก Supabase

## Phrase 2
Flow Working
เวลที่เหลือ 3.30 ชั่วโมง :
1. 14.30 - 15.30 น. ชั่วโมงแรกจะทำ 
- Feature 1 : Landing Page (Show pulic every product)
- Feature 2 : Authentication Login (Role : Admin และ Super Admin)

2. 15.30 - 16.30 น. จะทำ
- Feature 3 : Add Product (Import Excel)
- Feature 4 : Generate QR Code (Add Every Product)

3. 16.30 - 17.00 น. จะทำ
- Feature 5 : Edit Product (Edit QR,Description,Upload picture produc)
- Feature 6 : Adjust QR Code (Can change background color & can Download png)

4. 17.00 - 17.30 น. จะทำ README สรุปงานตามหัวข้อกำหนด

ถ้าหากเวลาไม่พอ จะตัด Feature 6 ออกก่อนเป็น optional 
### ข้อมูลที่ต้องเก็บ
ตาราง luma_products และ luma_products_update (Supabase) Column Form
- sku numberic (รหัสสินค้า ไม่ซ้ำกัน รูปแบบ LS-0000)
- name text (ชื่อสินค้า)
- category text (Cleanser, Toner, Serum, Moisturizer, Sunscreen หรือ Mask)
- price numberic (ราคาเป็นบาท มากกว่า 0)
- size text (เช่น 30 ml, 50 g)
- description text (รายละเอียดสินค้า)
- how_to_use text (วิธีใช้)
- status text (active หรือ inactive ถ้าว่างถือเป็น active สินค้า inactive ไม่แสดงบนหน้าสาธารณะ)

ตาราง Admins และ Super Admin
- id uuid pk
- email text unique
- password text
- role text
- is_active boolean
Authentication -> Users -> Add user
หากพลาดในส่วนไหนไปสามารถทำการแก้ไขหรือทำเพิ่มได้

Contraints PNG :
- จำนวนรูป (1 รูปหลักต่อสินค้า (หลายรูปทำได้ถ้ามีเวลา))
- ประเภทไฟล์ (JPG, PNG หรือ WEBP)
- ขนาดไฟล์ (ไม่เกิน 2 MB)
- สัดส่วนที่แนะนำ (สี่เหลี่ยมจัตุรัส อย่างน้อย 800 × 800 px)
- ไฟล์ผิดเงื่อนไข (ระบบต้องปฏิเสธและบอกเหตุผลให้ผู้ใช้เข้าใจ) 
- สินค้าที่ยังไม่มีรูป (หน้าสาธารณะต้องแสดงผลได้ปกติ เช่น ใช้รูปแทน (placeholder))

อื่นๆ 
- PLAN.md ต้องมี
Flow การทำงานของระบบ ตั้งแต่ Admin นำเข้า Excel จนลูกค้าสแกน QR (เขียนหรือวาดก็ได้)
ข้อมูลที่ต้องเก็บ แบ่งเป็นตารางอะไรบ้าง แต่ละตารางมีข้อมูลอะไร
ลำดับงานที่จะทำ และเวลาโดยประมาณของแต่ละงาน
ถ้าเวลาไม่พอ จะตัดฟีเจอร์ไหนออกก่อน เพราะอะไร
สมมติฐานหรือข้อตัดสินใจที่ต้องทำเอง เพราะโจทย์ไม่ได้ระบุไว้
(ถ้าหากขาดตกหรือเขียนไม่ครบสามารถไปอัพเดทที่ README แทนที่จะแก้ไข Plan.md เพิ่ม โดนบอกว่าต่างจากแผนงานเดิมยังไง แล้วเหตุผลที่ต้องเปลี่ยน)
- README.md ต้องมี
วิธีติดตั้งและรันระบบ พร้อมบัญชี Super Admin สำหรับทดสอบ
Tech stack ที่เลือก และเหตุผลที่เลือก
ฟีเจอร์ที่ทำเสร็จ และที่ไม่เสร็จ
สิ่งที่ต่างจากแผนงาน และเหตุผลที่เปลี่ยน
การใช้ AI: ใช้ทำอะไรบ้าง, ตัวอย่าง prompt อย่างน้อย 3 ตัวอย่าง, AI ผิดพลาดตรงไหนและแก้อย่างไร, ส่วนไหนเขียนเองทั้งหมด
