# Voyager 1 Reel — Script & Scene Production Plan

- **Project ID**: `mamase-voyager1-reel-v1`
- **Topic**: Voyager 1 — มนุษย์ยังคุยกับยานที่ไกลขนาดนั้นได้อย่างไร?
- **Category**: Spacecraft / Interstellar
- **Voice**: `google-gemini` (Fenrir, speed=1.0)
- **Resolution**: 1080×1920 (9:16 Vertical)
- **Visual Style Master**: `assets/branding/mamase/reference/eris-master-reels-visual-reference.jpg`

---

## Shot List & Scene Architecture

| Scene ID | Topic / Core Visual Focus | Narration & Key Facts | Visual Composition & Characters | Motion Plan |
|---|---|---|---|---|
| **Scene 01** (`scene-01-hook.png`) | **Hero Key Art Cover** (Locked Master) | ยานวอยเอเจอร์ 1 กำลังลอยอยู่ในความมืดมิด ห่างจากเราไปกว่า 24,000 ล้านกิโลเมตร... แต่มนุษย์บนโลก ยังคงคุยกับมันได้อยู่? | **ใช้ภาพ Master ที่ผู้ใช้ส่งมาโดยตรง** (1080×1920): Voyager 1 เสาอากาศหันหาโลก + ชายหนุ่มและสุนัขบนขอบหิน + Typographic Hook | Wan subtle push-in |
| **Scene 02** (`scene-02-interstellar-distance.png`) | **Interstellar Trajectory & Distance** | ยานถูกปล่อยตั้งแต่ปี 1977 ตอนนี้ข้ามพ้นขอบระบบสุริยะ เข้าสู่ห้วงอวกาศระหว่างดวงดาว ไกลโลกที่สุดในประวัติศาสตร์ | ภาพมุมกว้างมองย้อนกลับไปเห็นดวงอาทิตย์เป็นเพียงจุดแสงสีเหลืองอ่อนไกลลิบ ท่ามกลางอวกาศระหว่างดวงดาว (Interstellar Medium) | FFmpeg slow zoom out |
| **Scene 03** (`scene-03-light-speed-delay.png`) | **Light-Speed Delay (45+ Hours)** | คลื่นวิทยุความเร็วแสงต้องใช้เวลาขาเดียวนาน 23 ชั่วโมง ส่งไป-กลับใช้เวลานานเกือบ 2 วันเต็ม | ลำแสงวิทยุ (radio wave pulse) วิ่งผ่านความเวิ้งว้างข้ามระยะทาง 24,000 ล้านกิโลเมตร เชื่อมต่อยานและโลก | FFmpeg documentary pan |
| **Scene 04** (`scene-04-refrigerator-bulb-power.png`) | **22-Watt Transmitter** | เครื่องส่งสัญญาณกำลังส่งเพียง 22 วัตต์ เทียบเท่าหลอดไฟตู้เย็นดวงเล็กๆ | โฟกัสระยะใกล้ไปที่โมดูลส่งสัญญาณและจาน High-Gain Antenna เส้นผ่านศูนย์กลาง 3.7 เมตร โครงสร้างโลหะสะท้อนแสงดาว | FFmpeg cinematic push in |
| **Scene 05** (`scene-05-attowatt-signal-earth.png`) | **Attowatt Signal Arrival** | เมื่อสัญญาณมาถึงโลก พลังงานแผ่วเบาเหลือไม่ถึง 1 ใน 1,000 ล้านล้านล้านวัตต์ (10⁻²⁰ W) เบากว่าถ่านนาฬิกา | คลื่นวิทยุแผ่วเบาตัดกับสัญญาณรบกวนของเอกภพ (Cosmic Background Noise) ก่อนตกลงสู่ชั้นบรรยากาศโลก | FFmpeg slow zoom in |
| **Scene 06** (`scene-06-dsn-giant-dishes.png`) | **Deep Space Network (DSN 70m Dishes)** | เครือข่าย Deep Space Network จานรับสัญญาณยักษ์ 70 เมตร 3 แห่งทั่วโลก (Goldstone, Madrid, Canberra) | จานรับสัญญาณยักษ์ 70 เมตรของ DSN ยามค่ำคืนใต้ทางช้างเผือก หันหน้าขึ้นสู่ท้องฟ้ากำลังล็อกสัญญาณอย่างแม่นยำ | FFmpeg pull out |
| **Scene 07** (`scene-07-golden-record-humanity.png`) | **The Golden Record** | แผ่นจานเสียงทองคำ บันทึกเสียงทักทาย บทเพลง และภาพถ่ายของมนุษยชาติ เพื่อสื่อสารกับสิ่งมีชีวิตทรงปัญญา | ภาพโคลสอัพแผ่นจานเสียงทองคำ (Golden Record Cover) บนตัวยาน ลวดลายสัญลักษณ์ไฮโดรเจนและพัลซาร์สะท้อนแสง | FFmpeg push in |
| **Scene 08** (`scene-08-silent-voyage-milkyway.png`) | **Endless Journey in the Milky Way** | แม้พลังงานนิวเคลียร์ RTG จะหมดลงในอนาคต แต่วอยเอเจอร์ 1 จะลอยผ่านดวงดาวในทางช้างเผือกชั่วนิรันดร์ | ยานวอยเอเจอร์ 1 ลอยเงียบสงบผ่านกลุ่มดาวในทางช้างเผือก มุ่งหน้าสู่ดาวฤกษ์ Gliese 445 อย่างยิ่งใหญ่ไร้ขอบเขต | FFmpeg slow zoom out |
| **Scene 09** (`scene-09-mamase-outro.png`) | **Locked Mamase Outro** | Outro ประจำช่อง Mamase ของแท้ (กดไลก์ กดแชร์ กดติดตาม แล้วมาค้นพบโลก ค้นพบใจ) | ชายหนุ่มและสุนัขคู่หูนั่งชมวิวเมืองและทางช้างเผือก (Byte-for-byte locked asset) | FFmpeg slow zoom in |
