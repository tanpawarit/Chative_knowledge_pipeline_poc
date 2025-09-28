The image displays a book titled "Cryptography: How to Make a FUD Cryptocurrency and How to Re-FUD It" by Found. The cover features a dark background with a prominent, intricate blue geometric design in the center. The text on the cover is in white and blue, providing a stark contrast against the dark backdrop.

<!-- image -->
<!-- image description: The image displays a book titled "Cryptography: How to Make a FUD Cryptocurrency and How to Re-FUD It" by Found. The cover features a dark background with a prominent, intricate blue geometric design in the center. The text on the cover is in white and blue, providing a stark contrast against the dark backdrop. -->

## สารบัญ

```
แนะน าหนังสือ...2 บทที่ 1 รู ้ จักกับโปรแกรม Crypter...3 FUD vs UD…3-5 Scantime Crypter vs Runtime Crypter…5 Online Scanner…6 ฟังชั่นต่างๆในโปรแกรม Crypter…7-8 บทที่ 2  ปัจจัยที่ส าคัญที่สุดที่คุณจ าเป ็ นต ้ องรู ้ เกี่ยวกับการสร ้ าง Crypter…9 Anti-Viruses vs Crypter concept…9 ปัจจัยที่ 1...9 ปัจจัยที่ 2...10 สรุปบทที่ 2...10 บทที่ 3 โปรแกรม Crypter…10 Anti-Virus มองหาอะไรในไฟล์ไวรัส?...10-11 ระบบการท างานของ Crypter และไฟล์ Stub…12 สรุปการท างานของ Crypter…13 บทที่ 4 เขียนโปรแกรม Crypter โดย VB.NET…13 สร้ างโปรแกรม Crypter (Scantime)…14 สร้ างไฟล์ Stub…22 บทที่ 5 เทคนิคและแนวทางในการท าให ้  Crypter ของคุณ FUD…27 เปลี่ยนไอคอน...28-30 เปลี่ยนข ้ อมูล Assembly…30-33 เปลี่ยนชื่อตัวแปรต่างๆในโค ้ ต (Variable Names)...33-35 ใส่โค ้ ตขยะ (Junk Codes)…35-37 แก้ ไขดัดแปลง String และเปลี่ยนแปลงรูปแบบการท างานของโค ้ ต...37-40 เพิ่มขนาดไฟล์ (File Pumper)…40 Runtime Crypter (Built-in Stub และฟังชั่นต่างๆ)…41 บทสรุปหนังสือ Cryptography…42-43
```

## แนะน าหนังสือ

สวัสดีครับสมาชิกแฮกดีทุกท่าน เจอกันอีกแล ้ ว.. เล่มสองคราวนี้ผมจะมาสอน วิธีการสร ้ าง Crypter และเทคนิคแนวทางและวิธีที่จะท าให ้  Crypter ของคุณ FUD (Fully Undetectable). มือใหม่ไม่ต ้ องกลัวครับบทความมีรูปภาพประกอบ อธิบายขั้นตอนต่อขั้นตอนเข ้ าใจง่าย.

ก่อนเริ่มผมขอบอกสิ่งหนึ่งที่ส าคัญมากๆก่อน ในบทความนี้ไม่มีอะไรที่ง่าย โดยเฉพาะการสร้าง Crypter..  ไม่มีที่ไหนในโลกที่สอนให ้ คุณสร ้ าง Crypter ที่มี เพียงแค่ปุ ่ มเดียวให ้ กดและจะ FUD ไปตลอดชีวิต คุณโดนหลอกครับ ใช่ครับ..มัน อาจไม่ง่าย แต่คุณจ าเป็ นจะต ้ องมีความพยายามและทดลอง มีเวลาให ้ กับมันและ ลงมือท าในสิ่งที่คุณเรียนรู ้ จากหนังสือเล่มนี้.

ยิ่งคุณมีความรู ้ ด ้ านการเขียนโปรแกรมคุณจะยิ่งได ้ ประโยชน์จากหนังสือเล่มนี้เกิน กว่าที่คุณคิดแน่นอนครับ  ส่วนสมาชิกที่ไม่มีพื้นฐานเกี่ยวกับการเขียนโปรแกรม หรือมีบ ้ างเล็กน ้ อย ไม่ใช่ปัญหาครับ ผมจะลงลึกแบบละเอียดทุกบรรทัดทุก บทความคุณจะเข้ าใจและลงมือท าตามได ้ ทุกขั้นตอน.

แล้ วที่ส าหรับที่สุดระหว่างการเรียนรู ้  หากสมาชิกมีปัญหาต ้ องการความช่วยเหลือ รบกวนตั้งกระทู ้ โพสถามได ้ ที่:

http://Hackdee.biz/community/index.php?categories/cryptography.70/ แล้ วผมจะมาตอบภายใน 24 ชั่วโมง.

ส าคัญ: สมาชิกที่ซื้อหนังสือเล่มนี้จ าเป ็ นต ้ องแจ ้ งชื่อไอดีในบอร์ดของคุณให ้ ผมรู ้ ด้ วยนะครับ ส าหรับสมาชิกที่ยังไม่ได ้ แจ ้ งให ้ อัพเกรดคุณจะไม่สามารถเข ้ าถึงบอร์ด 'Cryptography' ที่สงวนสิทธิ์ไว ้ ให ้ กับสมาชิกที่ซื้อหนังสือเท่านั้น.

## บทที่ 1 - รู ้ จักกับ Crypter

Crypter คือโปรแกรมที่ใช ้ ในการ Encrypt ไฟล์ต่างๆเช่น ไวรัส, โทรจัน, คีย์ล็อก เกอร์ ฯลฯ จุดประสงค์หลักๆคือการ FUD เพื่อท าให ้  Anti-Virus ต่างๆสแกนไม่พบ นั่นเอง.

## FUD vs UD

FUD ย่อมาจาก Fully Undetected หรือ Fully Undetectable ซึ่ งแปลว่าซ่อนตัว จากการสแกนพบอย่างเต็มรูปแบบ. เต็มรูปแบบในที่นี้หมายถึงไม่มีแอนตี้ไวรัสตัว ไหนที่สแกนพบเลยว่าไฟล์ของคุณคือไวรัส.

UD ย่อมาจาก Undetected แปลว่าไฟล์ของคุณหลบแอนตี้ไวรัสได ้  แต่หลบได ้ ไม่ทั้งหมด อาจจะมี 1 หรือ 2 แอนตี้ไวรัสที่สแกนเจอ.

ดังนั้นเวลาให ้ บริการ Crypte ไฟล์ กรุณาให ้ ข ้ อมูลที่ถูกต ้ องกับลูกค ้ าหรือสมาชิก ด้ วยนะครับว่า Crypter ของคุณ FUD หรือ UD เฉยๆ.

ผมมีรูปความแตกต่างระหว่าง FUD กับ UD มาให ้ ดูเพื่อให ้ เข ้ าใจได ้ ง่ายมากขึ้น.

FUD

The image displays a screenshot of a file scan result from various antivirus programs. The interface includes a status bar at the top indicating "Scan Complete - 0/35," suggesting no issues were found. Each antivirus program listed, such as AVG Free, ArcaVir, Avast, and others, has a corresponding "OK" result, indicating that none of the programs detected any problems with the scanned file.

<!-- image -->
<!-- image description: The image displays a screenshot of a file scan result from various antivirus programs. The interface includes a status bar at the top indicating "Scan Complete - 0/35," suggesting no issues were found. Each antivirus program listed, such as AVG Free, ArcaVir, Avast, and others, has a corresponding "OK" result, indicating that none of the programs detected any problems with the scanned file. -->

## UD

The image displays a list of various antivirus and security software programs, each accompanied by a status indicator (either a green checkmark or a red cross) and a brief description or error message. The green checkmarks denote that the software is clean and functioning properly, while the red crosses indicate issues or infections detected by the software, with specific error messages provided for those instances. 

The layout is organized into two columns, with each row dedicated to a different security program. The background of the image is orange, providing a clear contrast to the text and status indicators. The list includes well-known programs such as AVG Free, Ad-Aware, ArcaVir, BitDefender, and Kaspersky Antivirus, among others.

<!-- image -->
<!-- image description: The image displays a list of various antivirus and security software programs, each accompanied by a status indicator (either a green checkmark or a red cross) and a brief description or error message. The green checkmarks denote that the software is clean and functioning properly, while the red crosses indicate issues or infections detected by the software, with specific error messages provided for those instances. 

The layout is organized into two columns, with each row dedicated to a different security program. The background of the image is orange, providing a clear contrast to the text and status indicators. The list includes well-known programs such as AVG Free, Ad-Aware, ArcaVir, BitDefender, and Kaspersky Antivirus, among others. -->

## Scantime Crypter vs Runtime Crypter

Crypter จะมีสองประเภทคือ Scan-Time Crypter และ Run-Time Crypter. สอง ประเภทนี้จะดูคล ้ ายๆกัน แต่ความแตกต่างของมันคือ:

## Run-Time Crypter

ใช ้  Encrypte ไฟล์ไวรัสของคุณ และเวลามันรัน มันจะ Decrypte เข ้ าไปใน Memory ซึ่งจะท าให ้ แอนตี้ไวรัสสแกนไม่เจอตอนก่อนหน้ าที่เหยื่อกดรันไฟล์ไวรัส และหลังจากที่เหยื่อรันไฟล์ไวรัสแล ้ ว.

## Scan-Time Crypter

ใช ้  Encrypte ไฟล์ไวรัสของคุณ และมันจะ ' ไม่ ' ถูกสแกนเจอแค่ตอนก่อนหน้าที่ จะรันไฟล์ไวรัส ไม่ใช่ตอนรันหรือหลังจากที่รันไฟล์ไปแล ้ ว.

## สรุปคือ

'Run'time Crypter = แอนตี้ไวรัสสแกนไม่เจอทั้งตอนก่อนกดรันไฟล์ และหลัง รันไฟล์.

'Scan'time Crypter = แอนตี้ไวรัสสแกนไม่เจอแค่ตอนก่อนกดรันไฟล์เท่านั้น. ผมแนะน าให้ สร ้ าง Crypter ที่มีทั้ง Runtime และ Scantime อยู่ในตัว. ผมจะมา สอนวิธีการสร ้ าง Crypter ทั้งแบบ Scantime และ Runtime ในหนังสือเล่มนี้แบบ ละเอียดในบทความต่อๆไป.

## Online Scanner

เราจะรู ้ ได ้ อย่างไรว่าแอนตี้ไวรัสตัวไหนบ ้ างที่สแกนพบว่า Crypter ของเราเป ็ น ไวรัส? เราจะใช ้ เว็บสแกนไวรัสออนไลน์ต่างๆตามอินเตอร์เน็ต.

แต่… มีเว็บไซต์ให ้ บริการสแกนไฟล์ไวรัสหลายเว็บที่ส่งผลสแกนไวรัสให ้ กับ บริษัทแอนตี้ไวรัส และนั้นคือเหตุผลหลักที่ท าให ้  Crypter ของคุณมีระยะเวลาการ FUD สั้นลง ! เพราะว่าถ ้ าคุณหรือใครก็ตามที่น าไฟล์ที่ Crypted ไฟล์ไวรัสโดยใช ้ Crypter ของคุณไปสแกนบนเว็บไซต์เหล่านี้ที่ส่งผลสแกนให ้ บริษัทแอนตี้ไวรัส ต่างๆ นั้นจะท า Crypter ของคุณมีระยะเวลาการ FUD ในสั้นลง.

ผมจะลงลึกข ้ อมูลเพิ่มเติมเกี่ยวกับเรื่องนี้ในหัวข ้ อต่อๆไปนะครับ. เว็บไซต์ที่ผม แนะน าให ้ น าไฟล์ไวรัสที่ Crypted แล ้ วไปสแกนได ้ คือ..

http://nodistribute.com/ (ฟรี 4 ครั้งต่อวัน) http://refud.me/scan.php (ฟรี) http://scan4you.net/ (เสียตัง)

## EOF

EOF ย่อมาจาก End Of File คือฟังค์ชั่นตัวนึงที่อยู่ใน Crypter. ไฟล์โทรจันบาง ไฟล์เช่น Cybergate, Bifrost หรือ Medusa จ าเป็นต ้ องท าการ EOF ตอนก าลัง Crypt เพื่อไม่ให ้ ไฟล์นั้นๆเกิดการ Corruption (Error).

รูปตัวอย่างของโปรแกรม Crypter ที่มีฟังค์ชั่น EOF:

The image shows a software interface named "TYV CRYPTER by m3m0_11," which appears to be a tool for encrypting files. The interface includes a password input field, a "Generate" button, and several checkboxes for different options such as "Anti Anubis," "Anti VM," and "Anti Debugger." There is also a section for selecting encryption methods and an option to include EOF Data. The interface features buttons for "Icon Changer," "Crypt!," and "About."

<!-- image -->
<!-- image description: The image shows a software interface named "TYV CRYPTER by m3m0_11," which appears to be a tool for encrypting files. The interface includes a password input field, a "Generate" button, and several checkboxes for different options such as "Anti Anubis," "Anti VM," and "Anti Debugger." There is also a section for selecting encryption methods and an option to include EOF Data. The interface features buttons for "Icon Changer," "Crypt!," and "About." -->

## File Binder

หลายคนน่าจะรู้ จาก File Binder กันดีแล ้ วถ ้ าได ้ อ่าน Hacking E-Book 1 st Edition มา. File Binder ใช ้ ส าหรับรวมไฟล์สองไฟล์เข ้ าด ้ วยกันนั่นเอง และมันก็ ควรถูกน าเข ้ าไปเป ็ นหนึ่งในฟังค์ชั่นของ Crypter ด ้ วย. มันสามารถรวมไฟล์ .exe เข ้ ากับนามสกุลอื่นๆได ้ เช่น .mp4, .jpg, .gif ฯลฯ พอกดรันไฟล์นั้นๆ ไฟล์ทั้งสอง ที่ถูกน ามารวมก็จะท างานด ้ วยกันทั้งคู่. แต่ Output ของไฟล์ที่รวมออกมาแล ้ วมัน ก็จะกล ้ ายเป ็ น .exe เหมือนเดิม ให ้ คุณลองอ่านวิธี 'เปลี่ยนนามสกุลไฟล์' ใน Hacking E-Book 1 st  Edition ดู มันอาจช่วยคุณได ้ .

## Anti's

หลายคนอาจเคยเห็นฟังค์ชั่น 'Anti's' ที่อยู่ใน Crypter และสงสัยว่ามันใช ้ ท า อะไร. Anti's ในที่นี้หมายถึงการ Bypass หรือ ป้องกันไฟล์ไวรัสของเราจากการ กระท าการใดการหนึ่ง เช่น Anti-Vm, Anti-Sandboxies, Anti-debugger ฯลฯ ยกตัวอย่างเช่น Anti-Sandboxies หมายถึงการป้องกันไม่ให ้ ไฟล์ไวรัสของเราถูก เปิดโดยโปรแกรม Sandboxies.

## File Pumper

File Pumper แปลว่า 'เพิ่มขนาดไฟล์' ใช ้ เพื่อเพิ่ม bytes ลงไปในไฟล์ของเรา เพื่อให ้ ขนาดมันใหญ่ขึ้น. มันอาจไม่ช่วยอะไรมาก แต่มันอาจช่วยให ้ ลดจ านวนการ ถูกสแกนพบจากบริษัทแอนตี้ไวรัส 1 - 2 บริษัท ซึ่งมันก็คุ ้ มค่า.

## Assembly Changer &amp; Icon Changer

ที่โปรแกรม Crypter ขาดไม่ได ้ เลยคือสองตัวนี้ มันมีผลอย่างมากที่จะท าให ้ โปรแกรม Crypter ของคุณนั้น FUD ในท ้ ายของหนังสือเล่มนี้ผมจะสอนเขียน โปรแกรม Crypter โดยมีฟังชั่นพวกนี้อยู่ด ้ วย. แต่อย่าข ้ ามไปอ่านเลยนะครับ! ใจ เย็นๆ ผมแนะน าให ้ อ่านให ้ ละเอียดอ่านให ้ เข ้ าใจทุกๆหน ้ าในหนังสือเล่มนี้.

Tip: ค ้ นหาใน Google หมวดรูปภาพ ค ้ นหาค าว่า Crypter, Crypter GUI เพื่อดู รูปร่างหน ้ าตาโปรแกรม Crypter ในหลากหลายรูปแบบ.

## บทที่ 2 - ปัจจัยที่ส าคัญที่สุดที่คุณจ าเป ็ นต ้ องรู ้ เกี่ยวกับ การสร้ าง Crypter

บทนี้เป็ นบทที่ส าคัญมากๆ อ่านให ้ หมดและอ่านให ้ ละเอียดนะครับ. บทที่ ๒ นี้จะ เปิดโลกกว ้ างให ้ กับคุณ คุณจะได ้ รู ้ ว่า มีปัจจัยอะไรบ ้ างที่ท าให ้  Crypter ของคุณมี ระยะเวลาการ FUD ที่สั้นลง.

## Anti-Viruses vs Crypter concept

คุณเคยสงสัยไหมว่าไฟล์ไวรัส, โทรจัน ของเราถูกสแกนพบว่าเป็นไฟล์ไวรัสโดย บริษัทแอนตี้ไวรัสต่างๆได ้ อย่างไร?....

การท างานของแอนตี้ไวรัสนั่นซับซ ้ อนมากกว่าที่คุณจินตนาการไว ้ แน่นอน. ปัจจัย ส าคัญที่จะท าให ้ เรา Bypass แอนตี้ไวรัสได ้ คือ รู ้ จักวิธีที่แอนตี้ไวรัสตรวจสอบไฟล์ ต่างๆ และพวกเขารู ้ ได ้ อย่างไรว่าไฟล์นั่นๆ คือไฟล์ไวรัส หรือโทรจัน.

## ปัจจัยที่ 1

จากเว็บไซต์สแกนไฟล์ไวรัสออนไลน์ อาจเพราะพวกเราเหล่าแฮกเกอร์เองอัพ โหลดไฟล์ไวรัสที่ Crypted แล ้ ว เพื่อตรวจสอบว่ามีแอนตี้ไวรัสตัวไหนสแกนเจอ บ้ าง หรืออาจเพราะเหยื่อของเราหรือผู ้ ใช ้ งานคอมฯทั่วไป เกิดไม่ไว ้ ใจไฟล์ที่พวก เขาดาวน์โหลดมา จึงน าไปสแกนบนเว็บไซต์เหล่านี้.

หลังจากที่อัพโหลดไฟล์เพื่อสแกนไวรัสลงบนเว็บไซต์เหล่านี้ พวกเขาก็จะส่งผล สแกนให้กับบริษัทแอนตี้ไวรัสทันที. ส าหรับแฮกเกอร์ หรือคนที่ใช ้ บริการ Crypter ผมแนะน าให้ สแกนบนเว็บไซต์ที่มีตัวเลือก 'No Distribute' (แปลว่าไม่ส่งผล สแกน) หรือถ ้ าหาไม่เจอผมแนะน าสองเว็บนี้.

http://nodistribute.com/ (ฟรี 4 ครั้งต่อวัน)

http://refud.me/scan.php (ฟรี)

http://scan4you.net/ (เสียตัง)

## ปัจจัยที่ 2

จากโปรแกรมแอนตี้ไวรัสที่ติดตั้งอยู่ในคอมฯของคุณ.. จริงเหรอ? ครับจริง. และนี้ คือสิ่งที่ทุกคนที่ใช ้ งาน หรือก าลังสร ้ าง Crypter จ าเป ็ นต ้ องรู ้ . โปรแกรมแอนตี้ ไวรัสจะส่งไฟล์ที่ถูกสแกนพบว่าเป็นไวรัส ไปสู่ฐานข ้ อมูลของบริษัทพวกเขาโดย อัตโนมัติ.

ดังนั้นวิธีแก ้ ปัญหาคืออย่าติดตั้งโปรแกรมแอนตี้ไวรัสถ ้ าคุณคิดจะใช ้ งานหรือ ก าลัง สร้ างโปรแกรม Crypter. แอนตี้ไวรัสบางตัวมีตัวเลือกให ้ เราเลือกตอนติดตั้ง โปรแกรมว่า ให ้ เรายินยอมถ ้ าทางแอนตี้ไวรัสจะส่งล็อก และผลสแกนทั้งหมดไป ยังฐานข ้ อมูล. แต่ผมแนะน าว่าอย่าไว ้ ใจแอนตี้ไวรัส.

## สรุปบทที่ 2

บทที่ ๒ นี้ถือเป ็ นบทที่ส าคัญมากส าหรับคนที่คิดจะสร ้ าง FUD Crypter. เหตุผล หลักๆเลยที่ท าให ้  Crypter ของเราหรือของฟรีตามอินเตอร์เน็ตมีระยะเวลา FUD ที่สั้ นลงเพราะว่าคนส่วนใหญ่ไม่รู ้ จัก Anti-Viruses vs Crypter concept ตามที่ สอนมาในบทที่ 2 ข ้ างต ้ นนี้.

## บทที่ 3 - โปรแกรม Crypter

บทนี้เราจะลงลึก ผมจะแนะแนวเกี่ยวกับโปรแกรม Crypter ว่ามันท างานอย่างไร และถูกสร้ างขึ้นมาแบบไหน เพื่อเป็ นการปูพื้นให ้ คุณส าหรับการสร ้ าง FUD Crypter เป็นของตัวเอง.

## Anti-Virus มองหาอะไรในไฟล์ไวรัส?

ก่อนอื่นเรามาท าความเข ้ าใจพื้นฐานการท างานของแอนตี้ไวรัสกันก่อน.. ไฟล์ exe จะมีบรรทัดต่างๆที่เราเรียกมันว่า Offset, Hex, ASCII. คุณไม่ จ าเป ็ นต ้ องเข ้ าใจทั้งหมดที่ผมก าลังจะอธิบายต่อไปนี้ แค่เข ้ าใจพื้นฐานการท างาน ของมันก็พอ.

## รูปตัวอย่างในโปรแกรม Hex Workshop

The image shows a screenshot of the Hex Workshop software, which is used for hexadecimal editing and data analysis. The main window displays a hex dump of a file named "picture," showing both hexadecimal values and their corresponding ASCII representations. Additional panes at the bottom provide data inspection and structure viewer tools, with one pane listing various data types and their offsets, and another showing options for data comparison and analysis.

<!-- image -->
<!-- image description: The image shows a screenshot of the Hex Workshop software, which is used for hexadecimal editing and data analysis. The main window displays a hex dump of a file named "picture," showing both hexadecimal values and their corresponding ASCII representations. Additional panes at the bottom provide data inspection and structure viewer tools, with one pane listing various data types and their offsets, and another showing options for data comparison and analysis. -->

แอนตี้ไวรัสมีฐานข ้ อมูลส าหรับบันทึกโค ้ ตพวกนี้ของไฟล์ที่ถูกสแกนพบว่าเป ็ นไฟล์ ไวรัส. และพวกเขาจะใช ้ ข ้ อมูลในฐานข ้ อมูลเหล่านี้เพื่อตรวจสอบไฟล์ของคุณว่า มีโค ้ ตบรรทัดไหนตรงกับในฐานข ้ อมูลที่เคยตรวจพบว่าเป็นไวรัสหรือเปล่า ถ ้ า ตรงกันไฟล์ของคุณก็จะถูกสแกนพบและบันทึกว่าเป็นไวรัส.

## ระบบการท างานของ Crypter

The image depicts a sequence of four document icons connected by arrows, illustrating a process. The sequence starts with a document marked with an exclamation point, followed by a document with a question mark, then a document with a smiling face, and finally a document with a question mark and a plus sign.

<!-- image -->
<!-- image description: The image depicts a sequence of four document icons connected by arrows, illustrating a process. The sequence starts with a document marked with an exclamation point, followed by a document with a question mark, then a document with a smiling face, and finally a document with a question mark and a plus sign. -->

## ระบบการท างานของไฟล์ Stub

<!-- image -->

## สรุปการท างานของ Crypter

โปรแกรม Crypter จะน าไฟล์ไวรัสของคุณมา Encrypt จากนั้นมันจะน าไฟล์ไวรัส ของเราไปรวมเข ้ ากับไฟล์ Stub แล ้ ว Compile ออกมาเป็นไฟล์ Stub(Trojan) คือไฟล์ที่เราจะส่งให ้ เหยื่อเพื่อให ้ เหยื่อกด. ถ ้ าวันใดวันหนึ่งไฟล์ Stub ตัวนี้เกิดไม่ FUD ขึ้นมา (ถูกสแกนพบว่าเป็นไฟล์ไวรัส) ไฟล์ไวรัสทุกไฟล์ที่คุณเคยใช ้ กับไฟล์ Stub ตัวนี้ก็จะถูกสแกนพบว่าเป็นไวรัสไปด ้ วยทั้งหมด เข ้ าใจง่ายๆว่า ถ ้ าเพื่อนคุณ ญาติคุณ พี่น ้ องคุณมาขอให ้ คุณ FUD ให ้ เขา. ถ ้ าเวลาผ่านไปไฟล์ Stub ของคุณ ไม่ FUD. ไฟล์ทุกไฟล์ที่คุณเคย FUD ให ้ ก็จะไม่ FUD ไปด ้ วยทั้งหมด

## บทที่ 4 - เขียนโปรแกรม Crypter โดย VB.NET

คุณจ าเป็ นต ้ องมีความรู ้ ได ้ การเขียนโปรแกรมเล็กน ้ อยถึงปานกลาง. เหตุผลที่ผม ใช ้  VB.NET ในหนังสือเล่มนี้เพราะว่าเป ็ นภาษาที่เข ้ าใจง่าย เหมาะส าหรับมือใหม่ ที่ไม่มีความรู ้ ด ้ านการเขียนโปรแกรมมาก่อน. ก่อนอื่นให ้ โหลด VB.NET ที่นี้: https://www.visualstudio.com/products/visual-studio-community-vs ถ้ าคุณมีความรู ้ ด ้ านการเขียนโปรแกรมโดยภาษาอื่น เช่น C#, C++ ฯลฯ ในกรณี ที่คุณต ้ องการจะใช ้ ภาษาที่คุณถนัดในการเขียนโปรแกรม. คนที่ไม่มีประสบการณ์ ด้ านการเขียนโปรแกรมโดย VB.NET ให ้ เริ่มศึกษาพื้นฐาน VB.NET ที่นี้ครับ: http://www.visual-basic-tutorials.com/

เราจะเริ่มจากการสร ้ างโปรแกรม Crypter (Scan-Time) และไฟล์ Stub แบบ พื้นฐานกัน.

## สร้ าง Crypter {Scan-Time}

เปิดโปรแกรม Microsoft Visual Studio 2013 ขึ้นมาแล ้ วสร ้ างโปรเจคใหม่ขึ้นมา File &gt; New &gt; Project… &gt; Windows Forms Application

The image shows a dialog box for creating a new project in a development environment. The user is prompted to select a project template, with options ranging from different versions of the .NET Framework to Visual Basic and C# templates. The dialog also includes fields for naming the project, specifying the location, and choosing whether to create a new solution or use an existing one.

<!-- image -->
<!-- image description: The image shows a dialog box for creating a new project in a development environment. The user is prompted to select a project template, with options ranging from different versions of the .NET Framework to Visual Basic and C# templates. The dialog also includes fields for naming the project, specifying the location, and choosing whether to create a new solution or use an existing one. -->

- ปล. .NET 2.0, 3.0, 4.0, 4.5 แตกต่างกันอย่างไร? กรุณาอ่านก่อนครับตรงนี้ ค่อนข ้ างส าคัญ ถ ้ าเป้าหมายของคุณคือเหยื่อที่ใช ้  Windows 7 หรือต ่ากว่า ให ้ ใช ้ 2.0 ได ้ ไม่มีปัญหาครับ แต่ถ ้ าเป้าหมายของคุณคือผู ้ ใช ้  Windows 8.0/8.1/10 ให ้ ใช ้  .NET 4.0/4.5/4.5.1 เท่านั้นนะครับ เพราะถ ้ าใช ้  .NET 2.0 เหยื่อจะรันไฟล์ Crypte ของคุณไม่ได ้ และจะเจอ Error แบบนี้:

The image displays a Windows error dialog box titled "Windows Features." The message within the dialog indicates that the requested changes could not be completed because the system couldn't connect to the internet to download necessary files. It suggests ensuring an internet connection and clicking "Retry" to attempt the process again. The error code provided is "0x800F0906," and there is a link labeled "Tell me how to solve this problem." The dialog includes "Retry" and "Close" buttons at the bottom.

<!-- image -->
<!-- image description: The image displays a Windows error dialog box titled "Windows Features." The message within the dialog indicates that the requested changes could not be completed because the system couldn't connect to the internet to download necessary files. It suggests ensuring an internet connection and clicking "Retry" to attempt the process again. The error code provided is "0x800F0906," and there is a link labeled "Tell me how to solve this problem." The dialog includes "Retry" and "Close" buttons at the bottom. -->

## จากนั้นกด OK แล ้ วคุณจะเด ้ งมาหน ้ าจอแบบนี้:

The image shows a screenshot of Microsoft Visual Studio, an integrated development environment. It displays a window titled "Form1" with a blank form ready for design, and the tab at the top indicates it is in "Design" mode. The interface includes various menus and toolbars for different functionalities such as file operations, editing, debugging, and project management.

<!-- image -->
<!-- image description: The image shows a screenshot of Microsoft Visual Studio, an integrated development environment. It displays a window titled "Form1" with a blank form ready for design, and the tab at the top indicates it is in "Design" mode. The interface includes various menus and toolbars for different functionalities such as file operations, editing, debugging, and project management. -->

ให้ คุณไปที่ Toolbox ที่อยู่ตรง Sidebar ด ้ านซ ้ ายมือแล ้ วไปที่ &gt; Common Controls จากนั้นเราจะใส่ 2 Button และ 1 TextBox.

The image shows a screenshot of Microsoft Visual Studio with the Toolbox panel open. The Toolbox panel is categorized under "Common Controls" and lists various UI elements such as Pointer, Button, CheckBox, ComboBox, DateTimePicker, Label, ListBox, and others. The interface also displays the main menu and toolbar at the top, indicating options like File, Edit, View, Project, Build, Debug, Team, and Tools.

<!-- image -->
<!-- image description: The image shows a screenshot of Microsoft Visual Studio with the Toolbox panel open. The Toolbox panel is categorized under "Common Controls" and lists various UI elements such as Pointer, Button, CheckBox, ComboBox, DateTimePicker, Label, ListBox, and others. The interface also displays the main menu and toolbar at the top, indicating options like File, Edit, View, Project, Build, Debug, Team, and Tools. -->

ปรับขนาด Form ปรับแต่งปุ ่ มทั้งสามและกล่องข ้ อความทั้งสองของคุณ ปุ ่ มที่ 1 ให้ ตั้งชื่อว่า 'เลือกไฟล์…'เราจะใช ้ มันเป ็ นปุ ่ มที่ใช ้ เลือกไฟล์ที่จะท าการ Crypte. ปุ ่ มที่สองให ้ ตั้งว่า Crypte ส่วน TextBox1 คือกล่องข ้ อความที่จะแสดง Path และ ชื่ อไฟล์ที่คุณเลือก.

The image shows a screenshot of Microsoft Visual Studio with a project named "Hackdee.net" open. The interface displays a form designer on the left side, where a form named "Form1.vb" is being edited, containing a TextBox labeled "Crypt". On the right, the Solution Explorer is visible, listing the project and its components. The bottom part of the window shows the Output window, which currently indicates that the project is ready.

<!-- image -->
<!-- image description: The image shows a screenshot of Microsoft Visual Studio with a project named "Hackdee.net" open. The interface displays a form designer on the left side, where a form named "Form1.vb" is being edited, containing a TextBox labeled "Crypt". On the right, the Solution Explorer is visible, listing the project and its components. The bottom part of the window shows the Output window, which currently indicates that the project is ready. -->

จากนั้นไปที่ Form1.vb แล ้ วใส่ Imports System.Text ไว ้ ด ้ านบนสุดของ Source code และประกาศใช ้  Const ไว ้ ใน Public Class Form1 โดยใส่โค ้ ตนี้ลง ไป:

<!-- image -->

## โค้ ตคุณจะต ้ องออกมาเป็ นแบบนี้:

The image shows a screenshot of Microsoft Visual Studio, an integrated development environment (IDE). The interface displays a code editor with a file named "Form1.vb" open, containing a snippet of Visual Basic code. The Solution Explorer on the right side lists the project structure, including files and folders, with "Form1.vb" highlighted.

<!-- image -->
<!-- image description: The image shows a screenshot of Microsoft Visual Studio, an integrated development environment (IDE). The interface displays a code editor with a file named "Form1.vb" open, containing a snippet of Visual Basic code. The Solution Explorer on the right side lists the project structure, including files and folders, with "Form1.vb" highlighted. -->

## จากนั้นกลับมาที่หน้า Form1.vb [Design] ดับเบิ้ลคลิกที่ปุ ่ มที่ 1 (เลือกไฟล์…)

The image shows a screenshot of a software development environment, specifically Microsoft Visual Studio, with a window titled "Hackdee.net." The window contains a form with various input fields and labels, including one labeled "Crypt" and another labeled "Crypt2." The form appears to be in the design mode, as indicated by the blue bar at the top labeled "Design."

<!-- image -->
<!-- image description: The image shows a screenshot of a software development environment, specifically Microsoft Visual Studio, with a window titled "Hackdee.net." The window contains a form with various input fields and labels, including one labeled "Crypt" and another labeled "Crypt2." The form appears to be in the design mode, as indicated by the blue bar at the top labeled "Design." -->

## แล้ วใส่โค ้ ตนี้เข ้ าไป:

The image displays a series of code snippets in a programming language, with text in both Thai and English. The code appears to involve file operations, such as opening and saving files, with specific filters for executable files (.exe). The layout includes comments in Thai explaining the functionality of each code section, and the text is color-coded for readability.

<!-- image -->
<!-- image description: The image displays a series of code snippets in a programming language, with text in both Thai and English. The code appears to involve file operations, such as opening and saving files, with specific filters for executable files (.exe). The layout includes comments in Thai explaining the functionality of each code section, and the text is color-coded for readability. -->

<!-- image -->

## โค้ ตคุณจะต ้ องออกมาหน้าตาแบบนี้:

The image shows a screenshot of Microsoft Visual Studio with a code editor open. The code appears to be a Visual Basic script for a form with a button, containing a subroutine for handling the button's click event. The code includes functionality to open a file dialog, save a file, and display the file name in a text box.

<!-- image -->
<!-- image description: The image shows a screenshot of Microsoft Visual Studio with a code editor open. The code appears to be a Visual Basic script for a form with a button, containing a subroutine for handling the button's click event. The code includes functionality to open a file dialog, save a file, and display the file name in a text box. -->

The image displays a screenshot of a Visual Studio interface with a form named "Form1.vb [Design]" open, showing a dialog box labeled "Hackdee.net." Below the screenshot, there is a block of Visual Basic code in Thai, which includes comments and instructions for saving and executing a file. The code involves file operations, such as opening, reading, and executing files, and includes a message box displaying the word "Crypt."

<!-- image -->
<!-- image description: The image displays a screenshot of a Visual Studio interface with a form named "Form1.vb [Design]" open, showing a dialog box labeled "Hackdee.net." Below the screenshot, there is a block of Visual Basic code in Thai, which includes comments and instructions for saving and executing a file. The code involves file operations, such as opening, reading, and executing files, and includes a message box displaying the word "Crypt." -->

## โค้ ตคุณจะได ้ แบบนี้:

The image displays a code editor window from a platform called "Hackdee.net." The main focus is on a Visual Basic (VB) script that includes a subroutine for handling a button click event. The code involves file operations, such as saving and loading files, and includes comments and logic for managing file paths and dialogs. The interface features a dark theme with syntax highlighting for better readability.

<!-- image -->
<!-- image description: The image displays a code editor window from a platform called "Hackdee.net." The main focus is on a Visual Basic (VB) script that includes a subroutine for handling a button click event. The code involves file operations, such as saving and loading files, and includes comments and logic for managing file paths and dialogs. The interface features a dark theme with syntax highlighting for better readability. -->

จากนั้นเราจะใส่โค ้ ต RC4 Algorithm Encryption เข ้ าไป. Algorithm Encryption/Decryption ของ VB.NET มีหลายรูปแบบเช่น XOR, Rijndael, Polymorphic RC4, Polymorphic Stairs เป็นต ้ น แต่ในบทความนี้ผมจะใช ้  RC4. การที่เราใช ้  Encryption เพื่อท าให ้ การ Encrypte ไฟล์ของคุณมีความซับซ ้ อน มากขึ้นและเพิ่มโอกาสให ้ แอนตี้ไวรัสสแกนไฟล์ไวรัสของคุณไม่เจอมากยิ่งขึ้น.

คุณลองไปที่เว็บไซต์นี้ http://www.fyneworks.com/encryption/rc4encryption/index.asp ลองใส่ค าว่า 'Hello Hackdee' แล ้ วกด Encrypt คุณจะ ได้ ตัวอักษรแบบสุ่มมาแบบนี้:

The image depicts an RC4 Encryption Tool interface that shows a process of encrypting original data. The original data, "Hello Hackdee," is transformed into a hexadecimal string "D4 0B 00 13 60 00 6B A9 81 0D D8 D6 04" using a secret key, as indicated by the encryption button and the resulting encrypted data displayed on the right.

<!-- image -->
<!-- image description: The image depicts an RC4 Encryption Tool interface that shows a process of encrypting original data. The original data, "Hello Hackdee," is transformed into a hexadecimal string "D4 0B 00 13 60 00 6B A9 81 0D D8 D6 04" using a secret key, as indicated by the encryption button and the resulting encrypted data displayed on the right. -->

ยิ่งท าให ้ โปรแกรม Crypter ของคุณมีความซับซ ้ อนเท่าไหร่ยิ่งท าให ้ แอนตี้ไวรัส ต่างๆสับสนยิ่งมีโอกาสท าให ้ ไฟล์ไวรัสของคุณถูกสแกนเจอได ้ น ้ อยที่สุด  .

คุณสามารถลองดาวน์โหลด Source Algorithm ตัวอื่นๆมาศึกษา และใช ้ งานได ้ :

http://www.se7ensins.com/forums/threads/source-vb-net-cryptographyalgorithms-for-a-fud-crypter.458064/

แต่ในบทความนี้ให ้ ใช ้  Rc4 นะครับ. ให ้ ใส่ Rc4 Function ตัวนี้ลงไป:

'ใช ้  RC4 Algorithm Encryption

Public Shared Function rc4(ByVal message As String, ByVal password As String) As String

Dim i As Integer = 0

Dim j As Integer = 0

Dim cipher As New StringBuilder

Dim returnCipher As String = String.Empty

Dim sbox As Integer() = New Integer(256) {}

Dim key As Integer() = New Integer(256) {}

Dim intLength As Integer = password.Length

Dim a As Integer = 0

While a &lt;= 255

Dim ctmp As Char = (password.Substring((a Mod intLength), 1).ToCharArray()(0))

key(a) = Microsoft.VisualBasic.Strings.Asc(ctmp)

sbox(a) = a

System.Math.Max(System.Threading.Interlocked.Increment(a), a - 1)

End While

Dim x As Integer = 0

Dim b As Integer = 0

While b &lt;= 255

x = (x + sbox(b) + key(b)) Mod 256

Dim tempSwap As Integer = sbox(b)

sbox(b) = sbox(x)

sbox(x) = tempSwap

System.Math.Max(System.Threading.Interlocked.Increment(b), b - 1)

End While a = 1

While a &lt;= message.Length

Dim itmp As Integer = 0

i = (i + 1) Mod 256

j = (j + sbox(i)) Mod 256

itmp = sbox(i)

sbox(i) = sbox(j)

sbox(j) = itmp

Dim k As Integer = sbox((sbox(i) + sbox(j)) Mod 256)

Dim ctmp As Char = message.Substring(a - 1, 1).ToCharArray()(0)

itmp = Asc(ctmp)

Dim cipherby As Integer = itmp Xor k cipher.Append(Chr(cipherby))

System.Math.Max(System.Threading.Interlocked.Increment(a), a - 1)

End While returnCipher = cipher.ToString

cipher.Length = 0

Return returnCipher

End Function

## โค้ ตคุณจะได ้ แบบนี้:

The image displays a code editor window from a platform called "Hackdee.net," showing a file named "Form1.vb." The code within the editor is written in Visual Basic and appears to be an encryption algorithm, with functions and variables related to cryptographic operations. The interface includes a toolbar at the top, a code panel in the center, and a sidebar on the right labeled "Declarations."

<!-- image -->
<!-- image description: The image displays a code editor window from a platform called "Hackdee.net," showing a file named "Form1.vb." The code within the editor is written in Visual Basic and appears to be an encryption algorithm, with functions and variables related to cryptographic operations. The interface includes a toolbar at the top, a code panel in the center, and a sidebar on the right labeled "Declarations." -->

## จากนั้นสร ้ าง Crypter ของคุณโดยไปที่ Build แล ้ วสร ้ างไฟล์ Crypter ของคุณได ้ เลย:

The image displays a menu from Microsoft Visual Studio, specifically for a project named "Hackdee.net." The menu is under the "Build" tab and includes options such as "Build Solution," "Rebuild Solution," "Clean Solution," "Run Code Analysis on Solution," "Build Hackdee.net," "Rebuild Hackdee.net," "Clean Hackdee.net," "Publish Hackdee.net," "Run Code Analysis on Hackdee.net," and "Configuration Manager." The interface is dark-themed with a clean layout.

<!-- image -->
<!-- image description: The image displays a menu from Microsoft Visual Studio, specifically for a project named "Hackdee.net." The menu is under the "Build" tab and includes options such as "Build Solution," "Rebuild Solution," "Clean Solution," "Run Code Analysis on Solution," "Build Hackdee.net," "Rebuild Hackdee.net," "Clean Hackdee.net," "Publish Hackdee.net," "Run Code Analysis on Hackdee.net," and "Configuration Manager." The interface is dark-themed with a clean layout. -->

ถ้ าไม่มีอะไรผิดพลาดคุณจะได ้ ข ้ อความแบบนี้พร ้ อมกับ Path ที่ Crypter ของคุณ ถูก Save ไว ้ :

The image shows a build output window from a development environment. It indicates that a build process for a project named "Hackdee.net" was started with the configuration "Debug Any CPU." The output states that the build succeeded with 1 successful build, 0 failures, 0 up-to-date builds, and 0 skipped builds.

<!-- image -->
<!-- image description: The image shows a build output window from a development environment. It indicates that a build process for a project named "Hackdee.net" was started with the configuration "Debug Any CPU." The output states that the build succeeded with 1 successful build, 0 failures, 0 up-to-date builds, and 0 skipped builds. -->

ถ้ าคุณเจอ Error ให ้ ย ้ อนกลับขึ้นไปอ่านให ้ ละเอียด ให ้ แน่ใจว่าไม่ตกหล่นอะไรไป.

## สร้ างไฟล์ Stub

เปิดโปรแกรม Microsoft Visual Studio 2013 ขึ้นมาแล ้ วสร ้ างโปรเจคใหม่ขึ้นมา File &gt; New &gt; Project… &gt; Windows Forms Application &gt; แล ้ วกด OK.

จากนั้นไปที่ Form1.vb แล ้ วใส่ Imports System.Text ไว ้ ด ้ านบนสุดของ Source code และประกาศใช ้  Const ไว ้ ใน Public Class Form1 โดยใส่โค ้ ตนี้ลง ไป:

<!-- image -->

## โค้ ตคุณจะออกมาตามรูปด ้ านล่าง:

The image shows a screenshot of Microsoft Visual Studio, an integrated development environment (IDE). The interface displays a code editor with a file named "Form1.vb" open, containing a snippet of Visual Basic code. The layout includes a menu bar at the top, a toolbar with various icons, and a Solution Explorer pane on the right side, listing project files and folders.

<!-- image -->
<!-- image description: The image shows a screenshot of Microsoft Visual Studio, an integrated development environment (IDE). The interface displays a code editor with a file named "Form1.vb" open, containing a snippet of Visual Basic code. The layout includes a menu bar at the top, a toolbar with various icons, and a Solution Explorer pane on the right side, listing project files and folders. -->

กลับไปที่หน้า 'Form1.vb[Design]' ดับเบิ้ลคลิกที่ Form1:

<!-- image -->

หน้าต่าง Form1 ของคุณอาจไม่เหมือนของผมเพราะผมไปแก้ ไขตรง Properties มันนิดหน่อยแต่ไม่เป็นไรครับไม่ มีผลอะไร.

## จากนั้นใส่โค ้ ตนี้ลงไป:

The image displays a sequence of code snippets, likely from a programming language such as Visual Basic, detailing a process involving file handling and encryption. The code includes steps for reading a temporary file, encrypting its contents using the RC4 algorithm, writing the encrypted data to a new file, and then starting a process to execute the encrypted file. The layout is organized with each line of code clearly separated and labeled.

<!-- image -->
<!-- image description: The image displays a sequence of code snippets, likely from a programming language such as Visual Basic, detailing a process involving file handling and encryption. The code includes steps for reading a temporary file, encrypting its contents using the RC4 algorithm, writing the encrypted data to a new file, and then starting a process to execute the encrypted file. The layout is organized with each line of code clearly separated and labeled. -->

## จะได้ แบบนี้:

The image displays a code editor window with a Visual Basic (VB) source code file named "Form1.vb." The code defines a class named "Form1" with a method that handles file loading, including steps for reading a temporary file, encrypting its contents using the RC4 algorithm, and executing the encrypted file. The interface includes a toolbar at the top and a code editor area with syntax highlighting.

<!-- image -->
<!-- image description: The image displays a code editor window with a Visual Basic (VB) source code file named "Form1.vb." The code defines a class named "Form1" with a method that handles file loading, including steps for reading a temporary file, encrypting its contents using the RC4 algorithm, and executing the encrypted file. The interface includes a toolbar at the top and a code editor area with syntax highlighting. -->

## จากนั้นใส่ Function RC4 Encryption ลงไปเหมือนในโปรแกรม Crypter ของ เรา:

Public Shared Function rc4(ByVal message As String, ByVal password As String) As String

Dim i As Integer = 0

Dim j As Integer = 0

Dim cipher As New StringBuilder

Dim returnCipher As String = String.Empty

Dim sbox As Integer() = New Integer(256) {}

Dim key As Integer() = New Integer(256) {}

Dim intLength As Integer = password.Length

Dim a As Integer = 0

While a &lt;= 255

Dim ctmp As Char = (password.Substring((a Mod intLength), 1).ToCharArray()(0))

key(a) = Microsoft.VisualBasic.Strings.Asc(ctmp)

sbox(a) = a

System.Math.Max(System.Threading.Interlocked.Increment(a), a - 1)

End While

Dim x As Integer = 0

Dim b As Integer = 0

While b &lt;= 255

x = (x + sbox(b) + key(b)) Mod 256

Dim tempSwap As Integer = sbox(b)

sbox(b) = sbox(x)

sbox(x) = tempSwap

System.Math.Max(System.Threading.Interlocked.Increment(b), b - 1)

End While a = 1

While a &lt;= message.Length

Dim itmp As Integer = 0

i = (i + 1) Mod 256

j = (j + sbox(i)) Mod 256

itmp = sbox(i)

sbox(i) = sbox(j)

sbox(j) = itmp

Dim k As Integer = sbox((sbox(i) + sbox(j)) Mod 256)

Dim ctmp As Char = message.Substring(a - 1, 1).ToCharArray()(0)

itmp = Asc(ctmp)

Dim cipherby As Integer = itmp Xor k cipher.Append(Chr(cipherby))

System.Math.Max(System.Threading.Interlocked.Increment(a), a - 1)

End While returnCipher = cipher.ToString

cipher.Length = 0

Return returnCipher

End Function

## จะได้ แบบนี้:

The image displays a code editor window with a file named "Form1.vb" open. The code appears to be a Visual Basic script that includes a function for encrypting a message using a password. The interface features a dark theme with syntax highlighting, and the code includes loops, string manipulations, and cryptographic functions.

<!-- image -->
<!-- image description: The image displays a code editor window with a file named "Form1.vb" open. The code appears to be a Visual Basic script that includes a function for encrypting a message using a password. The interface features a dark theme with syntax highlighting, and the code includes loops, string manipulations, and cryptographic functions. -->

จากนั้นกด Build ไฟล์ Stub ของคุณได ้ เลย.. แล ้ วต ้ องแน่ใจว่าชื่อไฟล์ Stub ของ คุณชื่อว่า 'Stub.exe'

นะครับ จากนั้นคุณจ าเป็ นต ้ องน าโปรแกรม Crypter และไฟล์ Stub มาไว ้ ใน

โฟลเดอร์เดียวกัน:

ปล. ผมเอาไฟล์โทรจันมาไว้ในโฟลเดอร์เดียวกันด ้ วยเพื่อสะดวกต่อการทดลอง.

The image shows a file explorer window displaying a folder named "Test." Inside the folder, there are three files listed: "HackdeeCrypter.exe," "Stub.exe," and "Trojan.exe," with their respective sizes and modification dates. The file "HackdeeCrypter.exe" is highlighted, and the folder's contents are organized in a tabular format with columns for name, date modified, type, and size.

<!-- image -->
<!-- image description: The image shows a file explorer window displaying a folder named "Test." Inside the folder, there are three files listed: "HackdeeCrypter.exe," "Stub.exe," and "Trojan.exe," with their respective sizes and modification dates. The file "HackdeeCrypter.exe" is highlighted, and the folder's contents are organized in a tabular format with columns for name, date modified, type, and size. -->

## เปิดโปรแกรม Crypter ของคุณขึ้นมา เลือกไฟล์ไวรัสที่คุณต ้ องการจะ Crypte จากนั้นกด 'Crypte'

<!-- image -->

## คุณก็จะได ้ ไฟล์ที่คุณ Crypted:

The image displays a file explorer window showing a folder named "Test" containing several executable files. The files listed include "Crypted.exe," "HackdeeCrypter.exe," "Stub.exe," and "Trojan.exe," with details such as their modification dates, types, and sizes. The interface includes a navigation pane on the left with options like Favorites, Desktop, Downloads, Recent Places, and OneDrive.

<!-- image -->
<!-- image description: The image displays a file explorer window showing a folder named "Test" containing several executable files. The files listed include "Crypted.exe," "HackdeeCrypter.exe," "Stub.exe," and "Trojan.exe," with details such as their modification dates, types, and sizes. The interface includes a navigation pane on the left with options like Favorites, Desktop, Downloads, Recent Places, and OneDrive. -->

ปล. ถ้ าคุณท าทุกอย่างถูกต ้ องและไม่มีอะไรผิดพลาดขนาดไฟล์ที่คุณ Crypted แล ้ วจะมีขนาดใกล ้ เคียง หรือเท่ากับขนาดไฟล์โทรจันบวกกับขนาดไฟล์ Stub.

## ผลสแกนไฟล์ไวรัสก่อน Crypted (44/59):

The image displays a malware analysis report showing the results of various antivirus programs scanning a file named "Trojan.exe." Each antivirus program lists its detection results, with several identifying the file as malicious, such as Trojan inject AUZ, malware, or a downloader, while others report nothing found. The report also includes technical details like the file's MD5 hash, SHA1 hash, file size, and the time scanned.

<!-- image -->
<!-- image description: The image displays a malware analysis report showing the results of various antivirus programs scanning a file named "Trojan.exe." Each antivirus program lists its detection results, with several identifying the file as malicious, such as Trojan inject AUZ, malware, or a downloader, while others report nothing found. The report also includes technical details like the file's MD5 hash, SHA1 hash, file size, and the time scanned. -->

## ผลสแกนไฟล์ไวรัสหลัง Crypted (24/59):

The image displays a malware analysis report with a list of antivirus software and their respective detection results for a file named "Crypted.exe." Each antivirus program is listed alongside its findings, such as "Gen:Heur.MSIL.Krypt2.B" or "Clean - Nothing Found," along with additional details like file hashes, sizes, and the date and time of the scan. The results indicate that several antivirus programs identified the file as malicious, while others did not detect any issues.

<!-- image -->
<!-- image description: The image displays a malware analysis report with a list of antivirus software and their respective detection results for a file named "Crypted.exe." Each antivirus program is listed alongside its findings, such as "Gen:Heur.MSIL.Krypt2.B" or "Clean - Nothing Found," along with additional details like file hashes, sizes, and the date and time of the scan. The results indicate that several antivirus programs identified the file as malicious, while others did not detect any issues. -->

เห็นผลแตกต่างไหมครับ? ลดลงมาจาก 44/59 เหลือ 24/59.. เกือบ 50%  ครับ ถึงมันจะไม่ 100% FUD แต่ Crypter ที่เราสร ้ างกันมาเป็ นแค่ Crypter พื้นฐานเท่านั้น. บทต่อไปเราจะมาลงลึกเกี่ยวกับเทคนิคการท าให ้  Crypter ของ คุณมีเปอร์เซนต์ FUD เพิ่มขึ้น.

ถึงตรงนี้หลายคนอาจมีค าถามว่า แล ้ วถ ้ าวันใด Crypter ของคุณไม่ FUD หรือมี % FUD น้อยลงเราต ้ องแก ้ จากตรงไหน..? โปรแกรม Crypter หรือไฟล์ Stub..? ค าตอบคือไฟล์ Stub ครับ.

## บทที่ 5 - เทคนิคและแนวทางในการท าให ้  Crypter ของ คุณ FUD

นี้คือหัวข ้ อโดยรวมเทคนิคและแนวทางที่ผมจะลงลึกในบทที่ 5 นี้:

-  เปลี่ยนไอคอน
-  เปลี่ยนข ้ อมูล Assembly
-  เปลี่ยนชื่อตัวแปรต่างๆในโค ้ ต (Variable Names)
-  ใส่โค ้ ตขยะ (Junk Codes)
-  แก้ ไขดัดแปลง String ต่างๆในโค ้ ต (String Conversion, Encrypt String, Reverse String)
-  แก้ ไขเปลี่ยนแปลงรูปแบบการท างานของโค ้ ต
-  เพิ่มขนาดไฟล์ (File Pumper)

นี้คือหัวข ้ อหลักในการท าให ้ โปรแกรม Crypter และไฟล์ Stub ของคุณ FUD. จ า ไว้ อย่างนะครับ คุณจ าเป ็ นต ้ องมีจินตนาการใช ้ เทคนิคที่หลากหลาย หัวข ้ อข ้ างต ้ น คือแนวทางโดยรวมของผมเท่านั้น. มันไม่มีอะไรตายตัวในการเขียนโปรแกรมครับ .. ยกตัวอย่างเช่น คุณสามารถเขียนโค ้ ตได ้ หลายรูปแบบแต่ Output (ผลของมัน) ก็ออกมาเหมือนกัน. ดังนั้นถ ้ าคุณมีความรู ้ ในการเขียนจะยิ่งท าให ้ อะไรง่ายขึ้นมาก ซึ่ งผมแนะน าครับให ้ ไปเรียนภาษาคอมฯ ที่คุณต ้ องการ เรียนให ้ ลึก เรียนให ้ เก่งไป เลยถ้ าเป ็ นไปได ้ .

การสร้ าง FUD Crypter คุณอาจจะต ้ องใช ้ เวลาฝึกฝนและหมกมุ่นอยู่กับมันจนเกิน ความเคยชินจนเกิดเทคนิคที่เป็นของตัวคุณเองขึ้นมา ไม่ซ ้ากับใคร. ไม่มีที่ไหนใน โลกหรอกครับที่จะสอนให ้  Copy และ Paste โค ้ ตไม่กี่บรรทัดแล ้ วจะท าให ้ Crypter ของคุณ FUD ไปตลอด.

## เปลี่ยนไอคอน

วิธีนี้อาจไม่ช่วยอะไรมากนักแต่อาจช่วยให ้ คุณ Bypass Anti-Virus ได ้ บางตัว มัน ก็คุ ้ มที่จะลองครับ. ก่อนอื่นคุณต ้ องใช ้ ไอคอนที่ไม่ซ ้ากับใคร และไม่มีคนใช ้ เยอะ จะได้ ผลดีมากครับ เราจะมาสร ้ างไอคอนของเราเอง ให ้ คุณไปที่

https://www.google.com/images หารูปที่คุณต ้ องการแนะน าขนาด 256x256 หรือมากกว่า เช่นผมจะเลือกรูปของ Spotify โดยค ้ นหาค าว่า Spotify Icon:

The image displays a webpage featuring a product from Cold War Legacy Records named "BRACE." The main visual is a large red circular logo with white lines resembling sound waves. The webpage includes a description of BRACE as a versatile musical hourglass guitar, along with options to view more images and related items.

<!-- image -->
<!-- image description: The image displays a webpage featuring a product from Cold War Legacy Records named "BRACE." The main visual is a large red circular logo with white lines resembling sound waves. The webpage includes a description of BRACE as a versatile musical hourglass guitar, along with options to view more images and related items. -->

ผมจะเลือกรูปนี้ Save ไว ้ แล ้ วจากนั้นเราต ้ องเปลี่ยนให ้ มันเป ็ นไฟล์ .ico โดยการ ไปที่เว็บไซต์ http://www.converticon.com กด Get Started แล ้ วเลือกรูปภาพ ที่ต ้ องการจะเปลี่ยนแล ้ วกด Export ให ้ เลือกขนาด 256x256

The image displays a dialog box titled "Export Options" with two tabs labeled "Icon" and "PNG." Under the "Icon" tab, there is a list of checkboxes for different image sizes, including 16x16, 24x24, 32x32, 48x48, 64x64, 96x96, 128x128, 192x192, 256x256, 512x512, and "Original Size (400 x 400)." The checkbox next to "256 x 256" is selected. At the bottom of the dialog, there are "Back" and "Save As" buttons.

<!-- image -->
<!-- image description: The image displays a dialog box titled "Export Options" with two tabs labeled "Icon" and "PNG." Under the "Icon" tab, there is a list of checkboxes for different image sizes, including 16x16, 24x24, 32x32, 48x48, 64x64, 96x96, 128x128, 192x192, 256x256, 512x512, and "Original Size (400 x 400)." The checkbox next to "256 x 256" is selected. At the bottom of the dialog, there are "Back" and "Save As" buttons. -->

คุณก็จะได ้ ไอคอนของคุณ:

<!-- image -->

วิธีเปลี่ยนไอคอนมีสองวิธี.. เปลี่ยนในไฟล์โปรเจ็คโค ้ ตของคุณได ้ เลย หรือใช ้ โปรแกรม Resource Hacker. ส าหรับวิธีเปลี่ยนไอคอนโดยใช ้  Tool Resource

## Hacker ในหนังสือ Hacking E-Book 1 st  Edition

http://www.Hackdee.biz/Hacking\_E\_Book.pdf หน้าที่ 12 - 14. หรือคุณ สามารถเปลี่ยนได ้ ในโปรเจคโค ้ ตของคุณ.. เปิดโปรเจ็คไฟล์ Stub ของคุณขึ้นมา แล้ วคลิกขวาที่ Stub โปรเจ็ค แล ้ วไปที่ &gt; Properties:

The image shows a screenshot of a software development environment, specifically a Solution Explorer window in Visual Studio. The window displays a project named "My Project" with a file "Form1.vb" under it. The context menu is open, showing options such as "Build," "Rebuild," "Clean," "View," "Analyze," "Publish," and "Debug," with "Stub" highlighted as the selected option.

<!-- image -->
<!-- image description: The image shows a screenshot of a software development environment, specifically a Solution Explorer window in Visual Studio. The window displays a project named "My Project" with a file "Form1.vb" under it. The context menu is open, showing options such as "Build," "Rebuild," "Clean," "View," "Analyze," "Publish," and "Debug," with "Stub" highlighted as the selected option. -->

## ในช่อง Application คุณสามารถเปลี่ยนไอคอนได ้ จากตรงนี้:

The image displays a configuration window for a Visual Basic (VB) application named "Stub." The layout includes various tabs such as "Application," "Compile," "Debug," "References," "Resources," "Services," "Settings," "Signing," "My Extensions," and "Security." Within the "Application" tab, key settings like "sembly name," "Root namespace," "rgt framework," "artup form," and "Icon" are visible, with the "Icon" setting currently set to a default icon.

<!-- image -->
<!-- image description: The image displays a configuration window for a Visual Basic (VB) application named "Stub." The layout includes various tabs such as "Application," "Compile," "Debug," "References," "Resources," "Services," "Settings," "Signing," "My Extensions," and "Security." Within the "Application" tab, key settings like "sembly name," "Root namespace," "rgt framework," "artup form," and "Icon" are visible, with the "Icon" setting currently set to a default icon. -->

## นี้คือผลสแกนก่อนเปลี่ยนไอคอน:

The image displays a scan result summary from a malware detection tool, showing the analysis of a file by various antivirus engines. Each antivirus engine lists its detection results, with some identifying the file as malicious (e.g., Gen:Heur MSIL.Krypt2, Win32.GenMalicious!BNW [Troj]) while others report nothing found. The summary includes details such as file hashes, file size, and the timestamp of the scan.

<!-- image -->
<!-- image description: The image displays a scan result summary from a malware detection tool, showing the analysis of a file by various antivirus engines. Each antivirus engine lists its detection results, with some identifying the file as malicious (e.g., Gen:Heur MSIL.Krypt2, Win32.GenMalicious!BNW [Troj]) while others report nothing found. The summary includes details such as file hashes, file size, and the timestamp of the scan. -->

## ผลสแกนหลังการเปลี่ยนไอคอน:

The image displays a malware scan result summary for a file named "Hackdee.exe." The layout includes a list of antivirus software names on the left, their corresponding results in the middle, and details such as filename, file hashes, file size, and scan time on the right. Key findings indicate that several antivirus programs identified the file as malicious, with names like "Gen:Heur.MSIL.Krypt.2" and "Win32.GenMalicious.A," while others reported nothing found.

<!-- image -->
<!-- image description: The image displays a malware scan result summary for a file named "Hackdee.exe." The layout includes a list of antivirus software names on the left, their corresponding results in the middle, and details such as filename, file hashes, file size, and scan time on the right. Key findings indicate that several antivirus programs identified the file as malicious, with names like "Gen:Heur.MSIL.Krypt.2" and "Win32.GenMalicious.A," while others reported nothing found. -->

ลดลงไป 5 ตัว  . ทั้งนี้ทั้งนั้นมันขึ้นอยู่กับคุณภาพของไอคอนที่คุณหามา บางที อาจลดลง 2-3 ตัวบางทีอาจลดลงมากสุดถึง 5-7 ตัวเลยทีเดียว.

## แก้ ไขข ้ อมูล Assembly

นี้คือข ้ อมูล Assembly ของไฟล์ Stub ของคุณ:

The image displays a properties window for a file named "Stub.exe." The window is divided into several tabs: General, Compatibility, Security, and Details. The General tab shows various attributes of the file, including its description as "Stub," type as "Application," version as "1.0.0.0," and other metadata such as the product name, company, and date modified. The window also includes buttons for "OK," "Cancel," and "Apply" at the bottom.

<!-- image -->
<!-- image description: The image displays a properties window for a file named "Stub.exe." The window is divided into several tabs: General, Compatibility, Security, and Details. The General tab shows various attributes of the file, including its description as "Stub," type as "Application," version as "1.0.0.0," and other metadata such as the product name, company, and date modified. The window also includes buttons for "OK," "Cancel," and "Apply" at the bottom. -->

## คุณสามารถแก้ ไข Assembly ให ้ เป็ นแบบสุ่ม:

The image displays a software interface window titled "Assembly Information" with various fields such as Title, Description, Company, Product, Copyright, and Trademark filled with text. The window also includes version information for the assembly and file, a GUID, a neutral language dropdown, and an option to make the assembly COM-visible, along with OK and Cancel buttons at the bottom.

<!-- image -->
<!-- image description: The image displays a software interface window titled "Assembly Information" with various fields such as Title, Description, Company, Product, Copyright, and Trademark filled with text. The window also includes version information for the assembly and file, a GUID, a neutral language dropdown, and an option to make the assembly COM-visible, along with OK and Cancel buttons at the bottom. -->

หรือ Copy มาจากโปรแกรมที่หน้าเชื่อถือเช่น Microsoft, Adobe, Malwarebytes และอื่นๆ ในบทความนี้ผมจะ Copy ของ Malwarebytes ครับ. เราสามารถ Copy Assembly ของโปรแกรมอื่นได ้ โดยการใช ้  Resource Hacker เปิดโปรแกรม Resource Hacker ของคุณขึ้นมาแล ้ วไปที่ File &gt; Open เปิดโปรแกรมที่คุณ ต้ องการจะท าการ Copy ในโฟลเดอร์ที่ชื่อว่า Version Info คุณจะเห็นข ้ อมูล Assembly ทั้งหมด.

The image displays a software interface titled "Resource Hacker" that is analyzing a file named "mbam.exe." The interface shows a section labeled "Version Info" with detailed metadata about the file, including its version number, company name, file description, internal name, legal copyright, legal trademarks, original filename, product name, and product version. The layout includes a menu bar at the top, a sidebar on the left with options like "Icon," "Icon Group," "Version Info," and "Manifest," and a main panel displaying the version information.

<!-- image -->
<!-- image description: The image displays a software interface titled "Resource Hacker" that is analyzing a file named "mbam.exe." The interface shows a section labeled "Version Info" with detailed metadata about the file, including its version number, company name, file description, internal name, legal copyright, legal trademarks, original filename, product name, and product version. The layout includes a menu bar at the top, a sidebar on the left with options like "Icon," "Icon Group," "Version Info," and "Manifest," and a main panel displaying the version information. -->

ให้ คุณเปลี่ยน Assembly ในโปรเจ็ค Stub ของคุณนะครับ.. เปิดโปรเจ็คขึ้น มาแล้ วคลิกขวาที่โปรเจ็ค Stub &gt; Properties &gt; Assembly Information…

The image shows a software development environment with a project named "Stub" being compiled. The interface displays the "Assembly Information" dialog box, which includes details such as the title "Malwarebytes Anti-Malware," company "Malwarebytes Corporation," and version information. The main window also shows the build process output at the bottom, indicating that the build has succeeded.

<!-- image -->
<!-- image description: The image shows a software development environment with a project named "Stub" being compiled. The interface displays the "Assembly Information" dialog box, which includes details such as the title "Malwarebytes Anti-Malware," company "Malwarebytes Corporation," and version information. The main window also shows the build process output at the bottom, indicating that the build has succeeded. -->

Note: อย่าลืมเปลี่ยนตรง 'Assembly name:' ด ้ วยนะครับให ้ เป็นชื่อโปรแกรมที่ คุณ Copy Assembly มา. กด Build ไฟล์ Stub ของคุณได ้ เลย แต่ชื่อของไฟล์ Stub เราตอนนี้จะเปลี่ยนเป็ น 'Malwarebytes Anti-Malware.exe' ตามที่คุณ เปลี่ยนในช่อง 'Assembly name:' ให ้ คุณเปลี่ยนกลับไปเป็น 'Stub.exe' ถ ้ า ไม่อย่างนั้นไฟล์ Stub ของคุณจะไม่ท างาน. หลายท่านอาจสงสัยว่าแล ้ วจะ เปลี่ยนไปเปลี่ยนมาท าไมให ้ ยุ่งยาก ท าไมไม่ตั้งชื่อ 'Assembly name:' ว่า Stub

## ไปเลยทีเดียว..

<!-- image -->

ตรงบรรทัด 'Original filename' คือเหตุผลครับ.. มันจะแสดงชื่อ Assembly name ตามที่คุณตั้งไว ้ ในโปรเจ็คของคุณ ดังนั้นในไฟล์โปรเจ็คเราเปลี่ยนให ้ ตรง ตามชื่อโปรแกรมที่คุณ Copy ข ้ อมูล Assembly มา แล ้ วหลังจากกด Build ออกมาแล้ ว แล ้ วค่อยมาเปลี่ยนชื่อไฟล์เป ็ นชื่อ 'Stub.exe' มันก็จะไม่มีผลกับ Original filename ครับ.

## ผลสแกนก่อนเปลี่ยนข ้ อมูล Assembly:

The image displays a malware scan result summary from various antivirus programs. Each antivirus name is listed alongside its detection result, with some identifying the malware as "Gen:Heur MSIL.Krypt2," "Win32.GenMalware.BNW," or "TR/Dropper.Gen Trojan," while others report "Clean - Nothing Found." The results include file details such as the filename, MD5 hash, SHA1 hash, file size, and the timestamp of the scan.

<!-- image -->
<!-- image description: The image displays a malware scan result summary from various antivirus programs. Each antivirus name is listed alongside its detection result, with some identifying the malware as "Gen:Heur MSIL.Krypt2," "Win32.GenMalware.BNW," or "TR/Dropper.Gen Trojan," while others report "Clean - Nothing Found." The results include file details such as the filename, MD5 hash, SHA1 hash, file size, and the timestamp of the scan. -->

## ผลสแกนหลังเปลี่ยนข ้ อมูล Assembly:

The image displays a scan result summary from various antivirus programs for a file named "Crypted.exe." Each antivirus program, listed on the left, shows the result of its scan, with most indicating "Clean - Nothing Found" in green. On the right, details about the file, including its MD5 hash, SHA1 hash, file size, and the time scanned, are provided. Additionally, there is a link to view more details about the scan results.

<!-- image -->
<!-- image description: The image displays a scan result summary from various antivirus programs for a file named "Crypted.exe." Each antivirus program, listed on the left, shows the result of its scan, with most indicating "Clean - Nothing Found" in green. On the right, details about the file, including its MD5 hash, SHA1 hash, file size, and the time scanned, are provided. Additionally, there is a link to view more details about the scan results. -->

ลดลงไป 70%!! จาก 24/59 เหลือ 10/59  ได ้ ผลดีเกินคาดครับ.. ทั้งนี้ทั้งนั้น มันก็ขึ้นอยู่กับข ้ อมูล Assembly ที่คุณจะใส่ลงไปว่าน่าเชื่อถือและมีคุณภาพแค่ ไหน.

## เปลี่ยนชื่อตัวแปรต่างๆในโค ้ ต

วิธีนี้คืออีก 1 วิธีที่คุณ 'จ าเป ็ น' ต ้ องท าครับ. ตัวแปรคืออะไร? คือชื่อที่เรา ประกาศใช ้ งานแล ้ วใส่ค่าให ้ มันเช่น:

<!-- image -->

'TPath', 'file1', 'filezb4' และ 'filezafter' คือตัวแปรครับ. สังเกตุง่ายๆคือ ใน VB.NET การที่จะประกาศใช ้ งานตัวแปรเราจะใช ้  Dim Statement (Dim) ครับ ดังนั้น String อะไรก็ตามที่อยู่หลัง 'Dim' คือตัวแปรครับ.

ผมแนะน าให้ ท า Copy Backup ของโปรเจคของคุณไว ้ ก่อนเพราะการเล่นและ แก้ ไขตัวแปรในโค ้ ตของคุณค่อนข ้ างเสี่ยงที่คุณจะท าให ้ โค ้ ตของคุณเละเทะ และ จะท าให ้ โปรแกรม Crypter ของคุณเกิด Error ท า Backup ไว ้ เลยครับเท่านี้คุณ

จะเล่นจะซนกับโค ้ ตคุณแค่ไหนคุณก็ไม่ต ้ องมากังวลอีกต่อไป แถมยัง ประหยัดเวลาให ้ คุณด ้ วยอีกเยอะเลย  หัวใจหลักของโปรแกรมเมอร์อย่างเราคือ ต้ องรอบคอบไม่ประมาท และท าทุกหนทางที่เราจะสามารถประหยัดเวลาเขียนโค ้ ตของเราลงไปได้ ให ้ มากที่สุด.

เพื่อความรวดเร็วในการเปลี่ยนตัวแปรให ้ คุณ Highlight ตัวแปรที่คุณต ้ องการจะ เปลี่ยนแล ้ วกด Ctrl+H:

The image shows a code editor displaying a Visual Basic (VB) script file named "Form1.vb." The script contains a method for loading a form and handling file operations, including reading a temporary file path, opening a file, and splitting its name. The code snippet includes comments and is partially highlighted, indicating recent or ongoing modifications.

<!-- image -->
<!-- image description: The image shows a code editor displaying a Visual Basic (VB) script file named "Form1.vb." The script contains a method for loading a form and handling file operations, including reading a temporary file path, opening a file, and splitting its name. The code snippet includes comments and is partially highlighted, indicating recent or ongoing modifications. -->

แล้ วกดปุ ่ ม 'Replace all' หรือ 'Alt+A' แต่คุณต ้ องระวังหน่อยนะครับส าหรับตัว แต่สั้นๆ เช่นตัวอักษรเดียวอย่าง j, i, key ฯลฯ เพราะถ ้ าคุณใช ้  'Ctrl+H' Replace all มันอาจไปเปลี่ยนตัวอักษรตัวอื่นในฟังชั่นอื่นๆที่ไม่เกี่ยวกับตัวแปรและจะท าให ้ โค้ ตของคุณเละเทะ! ผมแนะน าให ้ ตั้งตัวแปรแบบตัวอักษรสุ่มยาวๆ หรือตั้งชื่อที่ คุณคิดว่าจะไม่ไปกระทบต่อโค ้ ตตัวอื่นในโปรเจคของคุณ.

## ผลสแกนก่อนแก้ไขเปลี่ยนแปลงชื่อตัวแปร:

The image displays a malware scan result summary for a file named "Crypted.exe." The layout includes a list of antivirus software names on the left, their corresponding results in the middle, and file details on the right. Key details such as the file's MD5 hash, SHA-1 hash, file size, and the time scanned are provided, with some antivirus programs identifying the file as malicious, such as "TR/Dropper.Gen.Trojan" and "TR/IAgent.A."

<!-- image -->
<!-- image description: The image displays a malware scan result summary for a file named "Crypted.exe." The layout includes a list of antivirus software names on the left, their corresponding results in the middle, and file details on the right. Key details such as the file's MD5 hash, SHA-1 hash, file size, and the time scanned are provided, with some antivirus programs identifying the file as malicious, such as "TR/Dropper.Gen.Trojan" and "TR/IAgent.A." -->

## ผลสแกนหลังแก้ไขเปลี่ยนแปลงชื่อตัวแปร:

The image displays a malware scan result for a file named "222.exe." The layout includes a list of antivirus software on the left, their results in the middle, and file details on the right. Most antivirus programs report "Clean - Nothing Found," but a few, such as Avg, Avira, and BKav, flag the file with various alerts like "virus.ITcrypt," "TR/Dropper.Gen TROJAN," and "virus.ITcrypt/A."

<!-- image -->
<!-- image description: The image displays a malware scan result for a file named "222.exe." The layout includes a list of antivirus software on the left, their results in the middle, and file details on the right. Most antivirus programs report "Clean - Nothing Found," but a few, such as Avg, Avira, and BKav, flag the file with various alerts like "virus.ITcrypt," "TR/Dropper.Gen TROJAN," and "virus.ITcrypt/A." -->

เหลือ 9/59 จาก 10/59 ถือว่าผลออกมาเป็นที่น่าพอใจครับ เพราะโปรแกรม Crypter และไฟล์ Stub ของเราเป็นโปรเจคขนาดเล็กเลยมีตัวแปรจะให ้ เปลี่ยน น้ อยมันเลยไม่ส่งผลมากมายเท่าไหร่ แต่วันนึงถ ้ าคุณท าโปรเจค Crypter ที่ใหญ่ ขึ้นไปอีก ห ้ ามลืมใช ้ วิธีนี้เด็ดขาดเพราะมันจะให ้ ผลดีเกินกว่าที่คุณคาดไว ้ แน่นอน.

## ใส่โค ้ ตขยะ (Junk Codes)

โค้ ตขยะในที่นี้ผมหมายถึงกลุ่มโค ้ ตต่างๆที่ใช ้ งานไม่ได ้ แต่เราใส่เข ้ าไปเพื่อเป ็ นตัว หลอกเท่านั้น หรือเพื่อท าให ้  Anti-Virus สับสนมากขึ้นโค ้ ตขยะที่เราจะใส่เข ้ าไป:

-  โค้ ต Sub/Function ขยะ
-  String ขยะ
-  สร้ าง Call Statement ปลอม
-  สร้ างตัวแปรปลอม
-  สร้ าง Loop Statement ปลอม
-  สร้ าง If/Else Statement ปลอม

โชคดีครับหัวข ้ อนี้ผมจะเอาโปรแกรมตัวช่วยมาให ้ คุณ เป็นโปรแกรมสุ่ม Junk Codes ดาวน์โหลดที่นี้:

## http://Hackdee.biz/Junk\_Code\_VB.rar

Credit to ใครก็ตามที่โค ้ ตโปรแกรมนี้ขึ้นมา.

เปิดโปรแกรม Junk Code ขึ้นมาแล ้ วเลือกจ านวน 'Sub' และ 'Section' ผม แนะน าให ้ เริ่มจากอย่างละ 2 ก่อน:

The image shows a software interface titled "Junk Code Generator." The interface features a large blank area at the top, presumably for displaying generated code. Below this, there are buttons labeled "Clear" and "Save," along with input fields for specifying the number of "Subs" and "Sections." A prominent "Generate" button is also present, suggesting that it initiates the code generation process.

<!-- image -->
<!-- image description: The image shows a software interface titled "Junk Code Generator." The interface features a large blank area at the top, presumably for displaying generated code. Below this, there are buttons labeled "Clear" and "Save," along with input fields for specifying the number of "Subs" and "Sections." A prominent "Generate" button is also present, suggesting that it initiates the code generation process. -->

อย่างที่ผมเตือนไว ้ ข ้ างต ้ น Back up โปรเจคของคุณไว ้ ก่อนเพราะการใส่โค ้ ตขยะมี โอกาสท าโค ้ ตของคุณเละเทะและเกิด Error ได ้ . เวลาใส่โค ้ ตขยะพยายามเลือก แต่ Function นะครับถ ้ าไม่จ าเป ็ นพยายามตัด Class หรือ Module ออก มันเสี่ยง ท าให ้ โค ้ ตของคุณ Error ถ ้ าคุณไม่มีพื้นฐานความรู ้ ด ้ านการเขียนโปรแกรม.

## ผลสแกนก่อนใส่โค ้ ตขยะ:

The image displays a malware scan result summary for a file named "222.exe." The layout includes a list of antivirus software on the left, their results in the middle, and file details on the right. Key details include the file's MD5 hash, SHA1 hash, size, and scan time, with most antivirus programs indicating "Clean - Nothing Found," except for a few that detected the file as malicious, such as "virus:JCrypt" and "virus:JCryptDA."

<!-- image -->
<!-- image description: The image displays a malware scan result summary for a file named "222.exe." The layout includes a list of antivirus software on the left, their results in the middle, and file details on the right. Key details include the file's MD5 hash, SHA1 hash, size, and scan time, with most antivirus programs indicating "Clean - Nothing Found," except for a few that detected the file as malicious, such as "virus:JCrypt" and "virus:JCryptDA." -->

## ผลสแกนหลังใส่โค ้ ตขยะ:

The image displays a scan result summary from various antivirus programs. Each antivirus name is listed on the left, with corresponding results indicating whether they found any issues with the file. The file details, including its name, hash values, size, and scan time, are provided on the right side of the image. One antivirus, Avira, flagged the file as a "TR/Dropper.Gen Trojan."

<!-- image -->
<!-- image description: The image displays a scan result summary from various antivirus programs. Each antivirus name is listed on the left, with corresponding results indicating whether they found any issues with the file. The file details, including its name, hash values, size, and scan time, are provided on the right side of the image. One antivirus, Avira, flagged the file as a "TR/Dropper.Gen Trojan." -->

จาก 9/59 เหลือ 8/59.. อย่าลืมนะครับการเล่นกับโค ้ ตของคุณโดยการใส่โค ้ ตขยะ นั้นอาจท าให ้ โปรแกรม Crypter ของคุณ Error.. ให ้ ท า Back-up โปรเจ็คของคุณ ไว ้ ก่อนเพื่อความปลอดภัย แต่ถ ้ าเจอ Error ในโค ้ ตของคุณแล ้ วไม่รู ้ จะแก ้ ตรงไหน ให้ ตั้งกระทู ้ ถามในบอร์ดตามลิงค์ด ้ านล่างนี้แล ้ วผมจะมาตอบภายใน 24 ชั่วโมง: http://Hackdee.biz/community/index.php?categories/cryptography.70/

## แก้ ไขดัดแปลง String ต่างๆในโค ้ ตของคุณ และเปลี่ยนรูปแบบการ ท างานของโค้ต

เช่นเดียวกันครับ แก ้ ไขเปลี่ยนแปลง String และแก ้ ไขเปลี่ยนแปลงรูปแบบการ ท างานของโค ้ ตอาจท าให ้ โปรแกรม Crypter ของคุณเกิดการ Error ได ้ .. อย่าลืม Back-up โปรเจ็คของคุณไว ้ ด ้ วยนะครับ.

อย่างที่ผมกล่าวไว ้ ก่อนหน ้ านี้ว่าการเขียนโปรแกรมนั้นไม่มีอะไรตายตัว คุณ สามารถเขียนโค ้ ตได ้  10 รูปแบบโดยทุกๆรูปแบบมีผลการท างานออกมา เหมือนกันทั้งหมดเช่น ประกาศตัวแปรข ้ างนอก 'Sub' จะท าให ้ คุณใช ้ ตัวแปรนั้นๆ ได้ ทุกที่ในโค ้ ตของคุณ, การใช ้  Call Statement เพื่อเรียกโค ้ ตของ Sub ใด Sub หนึ่งกลับเข ้ ามาท างานใน 'Sub', การเปลี่ยนรูปแบบการใช ้ งานของ Boolean ต่างๆ เช่น 'False' คุณสามารถเปลี่ยนเป็น '0' หรือใช ้  'Operator' ต่างๆเป็นตัว ช่วยเช่น Operator 'Not', 'And' หรือ 'Or' เช่น แทนที่คุณจะใช ้  'ตัวแปร = False' คุณสามารถใช ้  'ตัวแปร = Not (1)' ค่าของมันคือ False เหมือนกัน.. ผม แนะน าให ้ คุณไปศึกษาเกี่ยวกับการท างานของ Logical/Bitwise Operator ต่างๆ ใน VB.NET ก่อนนะครับ.. คุณสามารถเข ้ าไปอ่านได ้ ที่:

https://msdn.microsoft.com/en-us/library/2h9cz2eb.aspx เป็ นภาษาอังกฤษนะครับ ถ ้ าไม่เข ้ าใจหรืออยากให ้ แปลบทความไหนให ้  ให ้ คุณ โพสในไว้ในบอร์ด:

http://Hackdee.biz/community/index.php?categories/cryptography.70/

## โอเคเรามาต่อกันที่บทความ.... โค ้ ตในโปรเจค Stub ก่อนจะท าการแก ้ ไขรูปแบบ การท างาน:

The image displays a code snippet in a Visual Basic .NET environment, specifically within a file named "form1.vb." The code includes a method named "Form1_Load" which handles the loading of a form. This method involves file operations such as opening, reading, encrypting, and executing a file, with comments in Thai providing additional context. The code uses the RC4 encryption algorithm to process the file before executing it.

<!-- image -->
<!-- image description: The image displays a code snippet in a Visual Basic .NET environment, specifically within a file named "form1.vb." The code includes a method named "Form1_Load" which handles the loading of a form. This method involves file operations such as opening, reading, encrypting, and executing a file, with comments in Thai providing additional context. The code uses the RC4 encryption algorithm to process the file before executing it. -->

## โค้ ตในโปรเจค Stub หลังจากท าการแก ้ ไขรูปแบบการท างาน:

คุณสังเกตุเห็นว่ามีอะไรเปลี่ยนแปลงไปบ ้ าง?.. ผมจะมาอธิบายว่าผมเปลี่ยนการ ท างานของโค ้ ตอย่างไรบ ้ าง

The image displays a code editor window with a file named "Form1.vb" open. The code appears to be written in Visual Basic and includes functions for file handling, encryption, and process management. Key elements include file path manipulations, encryption using the RC4 algorithm, and the execution of a decrypted executable file.

<!-- image -->
<!-- image description: The image displays a code editor window with a file named "Form1.vb" open. The code appears to be written in Visual Basic and includes functions for file handling, encryption, and process management. Key elements include file path manipulations, encryption using the RC4 algorithm, and the execution of a decrypted executable file. -->

ก่อนอื่นเลยผมเปลี่ยนชื่อตัวแปรทั้งหมดเป็นชื่อแบบสุ่มมั่วๆจากนั้นผม Encrypt String ของ Statement Const filesplit เปลี่ยนจาก:

<!-- image -->

Encrypt โดย Rijndael Encryption เลยออกมาเป็น:

<!-- image -->

ค าเตือน: คุณต ้ องเปลี่ยน Const String ในโปรแกรม Crypter ของคุณให ้ เหมือนกันนะครับ.

เว็บไซต์ที่ใช ้  Encrypt คือเว็บนี้ครับ: http://scarlettcrypt.com/Rijndael คุณ สามารถใช ้  Encryption ตัวอื่นได ้ แล ้ วแต่คุณครับ.

## จากนั้นผมน าตัวแปรทั้ง 3 ตัว:

<!-- image -->

ประกาศใช ้ งานนอก 'Private Sub Form1\_Load' จะท าให ้ เราสามารถใช ้ ตัวแปร Algorithm ออกไปใส่ไว ้ ใน 'Sub' ใหม่:

Dim n4HAaef12v0VY2pFS6ejbw, G1Bsg9GxKwdzrBn91tIFWw(), jOniuV8SzM4LteVm1ioQ As Stringออกไป สามตัวนี้ได ้ ทุกที่ภายในโปรเจ็คโค ้ ตของคุณ. จากนั้นผมเอาบรรทัดที่ใช ้ งาน RC4

## Sub Rj56Kpism2BTUjnHpsE2Vg()

<!-- image -->

<!-- image -->

จากนั้นเรียกมันกลับเข ้ ามาใช ้ งานโดยใช ้  Call Statement:

## Call Rj56Kpism2BTUjnHpsE2Vg()

ถ้ าคุณสังเกตุผลได ้  Encrypte String จาก 'Panatkorn' เปลี่ยนเป็ นเป็น:

## YeqJBj5/8NjMl+wWcLUi4A==

คุณจ าเป็ นต ้ องเปลี่ยน String นี้ในโปรเจ็คโปรแกรม Crypter ของคุณด ้ วยนะครับ ไม่งั้นโปรแกรม Crypter ของคุณจะ Error:

The image displays a snippet of code written in a programming language, likely C or C++, with comments and function calls related to file operations. The code includes opening and closing files, reading from and writing to files, and manipulating file contents, with a section of the code encrypted or obfuscated as indicated by a blue arrow pointing to a specific line.

<!-- image -->
<!-- image description: The image displays a snippet of code written in a programming language, likely C or C++, with comments and function calls related to file operations. The code includes opening and closing files, reading from and writing to files, and manipulating file contents, with a section of the code encrypted or obfuscated as indicated by a blue arrow pointing to a specific line. -->

## ผลสแกนก่อนแก้ไขเปลี่ยนแปลง String และรูปแบบการท างานของโค ้ ต:

The image displays a scan result summary from various antivirus programs, showing whether they detected any issues with a file named "132.exe." Most antivirus programs, such as A-Squared, Agnitum, and AhnLab, reported "Clean: Nothing Found," indicating no threats were detected. However, Avast flagged the file as "Trojan," and Avira identified it as "Gen: Trojan," suggesting potential malware concerns. Additional details include the file's hash, size, and the scan date and time.

<!-- image -->
<!-- image description: The image displays a scan result summary from various antivirus programs, showing whether they detected any issues with a file named "132.exe." Most antivirus programs, such as A-Squared, Agnitum, and AhnLab, reported "Clean: Nothing Found," indicating no threats were detected. However, Avast flagged the file as "Trojan," and Avira identified it as "Gen: Trojan," suggesting potential malware concerns. Additional details include the file's hash, size, and the scan date and time. -->

## ผลสแกนหลังแก้ไขเปลี่ยนแปลง String และรูปแบบการท างานของโค ้ ต:

The image displays a scan result summary from various antivirus programs, indicating that the file "FUD.exe" was scanned and found to be clean with no malware detected. The summary includes details such as the file's MD5 hash, SHA1 hash, file size, and the time the scan was conducted, along with a link to view more information.

<!-- image -->
<!-- image description: The image displays a scan result summary from various antivirus programs, indicating that the file "FUD.exe" was scanned and found to be clean with no malware detected. The summary includes details such as the file's MD5 hash, SHA1 hash, file size, and the time the scan was conducted, along with a link to view more information. -->

จาก 8/59 เหลือ 2/60.  เหลือ 2/60 คุณลองแก ้ ไขดัดแปลงเทคนิคต่างๆที่ผม สอนมาข้ างต ้ น โดยลองใช ้ วิธีของคุณเอง ลองไปเรื่อยๆจนกกว่าคุณจะได ้ ผลที่น่า พอใจ.. แต่อย่าลืมนะครับว่าโปรแกรม Crypter ที่เราสร ้ างกันมาถึงตรงที่เป็ นแค่ Scan-Time Crypter (ผมได ้ อธิบายไว ้ ในหน้าที่ 6 ถึงความแตกต่างของโปรแกรม Crypter Scan-Time และ Run-Time ถ ้ าจ าไม่ได ้ ลองย ้ อนกลับขึ้นไปอ่านก่อนนะ ครับ) ดังนั้นขีดจ ากัดของมันอาจได ้ ผลออกมาเต็มที่แค่นี้ อาจไม่ถึงกับ FUD แต่ มันก็เป ็ นแนวทางให ้ คุณได ้ เยอะเลยทีเดียว  .

## เพิ่มขนาดไฟล์ (File pumper)

ที่คือทางเลือกสุดท ้ ายที่เราจะใช ้ เพราะบางครั้งมันอาจท าให ้ ไฟล์ไวรัสเรา Corrupt ได้ . โปรแกรม File pumper จะเพิ่มขนาดไฟล์ให ้ คุณมันอาจจะช่วยคุณหลบแอนตี้ ไวรัสได ้ บางตัวแล ้ วแต่สถาณการณ์แต่ก็คุ ้ มค่าที่จะลอง. คุณสามารถดาวน์โหลด โปรแกรม File Pumper ได ้ ตาม Google โดยค ้ นหาค าว่า File Pumper.

## Runtime Crypter (Built-in Stub และฟังชั่นต่างๆ)

โหลด Crypter ตัวนี้ไปศึกษาดูครับ เป็น Crypter ที่มีฟังชั่นเพิ่มมากขึ้นที่จ าเป ็ น ต่อการ FUD เช่น แก ้ ไขข ้ อมูล Assembly, เปลี่ยนไอคอน และเพิ่มขนาดไฟล์:

http://Hackdee.biz/community/index.php?threads/2428/

The image displays three windows from a software application named "Hackdee.net," primarily in the Thai language. The top-left window appears to be a main interface with options related to cryptography. The top-right window includes options for assembly and a section for entering data, featuring an image of a person wearing a hat. The bottom window provides detailed information about an assembly, including fields for assembly name, company name, product name, copyright, trademark, and version numbers.

<!-- image -->
<!-- image description: The image displays three windows from a software application named "Hackdee.net," primarily in the Thai language. The top-left window appears to be a main interface with options related to cryptography. The top-right window includes options for assembly and a section for entering data, featuring an image of a person wearing a hat. The bottom window provides detailed information about an assembly, including fields for assembly name, company name, product name, copyright, trademark, and version numbers. -->

Crypter ตัวนี้เป ็ น Built-in Stub ครับ ดังนั้นถ ้ าคุณจะแก ้ ไขดัดแปลง หรือต ้ องการ ท าให ้ มันกลับมา FUD ให ้ แก ้ ที่ 'source.txt':

<!-- image -->

โหลดไปศึกษาเอานะครับเพราะถ ้ าจะให ้ สอนในหนังสือต่อคงยาวไปอีกหลายหน้า แน่ๆ แต่ไม่ต ้ องห่วงผมได ้ เขียน Comment ก ากับไว ้ ทุกโค ้ ตว่าใช ้ งานยังไง คุณได ้ ศึกษาวิธีสร ้ าง Crypter จากบทความที่แล ้ วมาแล ้ ว ดังนั้นผมคิดว่าถึงตอนนี้คุณ น่าจะเข ้ าใจหลักการท างานต่างๆของโปรแกรม Crypter และเข ้ าใจโค ้ ตต่างๆได ้

## บ้ างแล ้ ว แต่ถ ้ าเกิดมีปัญหาหรือเจอ Error หรือบัคที่แก ้ ไม่ได ้ ให ้ โพสถามผมใน กระทู ้ :

http://Hackdee.biz/community/index.php?forums/cryptography.72/ ได้ เลยนะครับ โปรแกรมนี้ผมเขียนขึ้นมาเอง 100% ดังนั้นผมสามารถช่วยเหลือ คุณได้ ทุกปัญหาทุก Error และโค ้ ตทุกบรรทัดแน่นอน แต่ทั้งนั้นทั้งนี้ให ้ คุณลอง พยายามด้ วยตัวเองให ้ ถึงที่สุดก่อนขอความช่วยเหลือจากผมนะครับ.

## บทสรุปหนังสือ Cryptography

มาถึงตรงนี้แล ้ วคุณได ้ เรียนรู ้ เกี่ยวกับการสร ้ างโปรแกรม Crypter และวิธีแนว ทางการ FUD Crypter ของคุณถึงจุดนี้แล ้ วคุณสามารถไปต่อไปสองทางครับ.. ส าหรับคนที่ยังไม่ช านาญภาษา VB.NET ผมแนะน าให ้ ไปศึกษาให ้ เก่งแล ้ วเริ่มลง มือสร ้ างโปรเจค Crypter เป็ นของตัวเองหรือดาวน์โหลด Crypter Source ของ คนอื่นแล ้ วมาศึกษาและใช ้ เทคนิคแนวทางที่ผมสอนด ้ านบนท าให ้ มันกลับมา FUD. คุณสามารถโหลด Crypter Source ของฟรีได ้ ในบอร์ด Cryptography: http://Hackdee.biz/community/index.php?forums/cryptography.72/ ผมจะคัดสรรแต่ Source ที่ได ้ มาตรฐานและใช ้ งานได ้ จริงเอามาแจกนะครับ แต่ถ ้ า คุณน า Crypter Source คนอื่นมาดัดแปลงแก ้ ไขอย่าลืมให ้ เครดิตผู ้ เขียนโค ้ ตด ้ วย นะครับ.

อย่าลืมนะครับการเขียนโปรแกรม Crypter ยิ่งคุณเขียนให ้ ซับซ ้ อนและไม่ซ ้าใคร มากเท่าไหร่ยิ่งท าให ้ โอกาส FUD มีมากขึ้นเท่านั้น ถ ้ าเกิดโปรแกรมของคุณเกิดไม่ FUD ขึ้นมาอาจถูกสแกนเจอโดย 3-4 แอนตี้ไวรัส คุณต ้ องหาว่าโค ้ ตตัวไหนที่ท า ให้ แอนตี้ไวรัสตัวไหนสแกนพบ เช่น Avira จะสแกนเจอหากคุณใส่ RunPE Module ลงไปใน Crypter เพื่อท าให ้  Crypter คุณเป็น Runtime คุณต ้ องแก ้ ไข ให้ ตรงจุดครับบางทีถึงกับต ้ องมาไล่ลบโค ้ ตทีละบรรทัดกันเลยทีเดียวว่าโค ้ ตบรร ทัดไหนที่ถูกบันทึกว่าเป็ นไวรัส มันอาจดูยากและใช ้ เวลามากแต่ถ ้ าคุณอยู่กับมัน จนชินจนช านาญ จากที่จะต ้ องมานั่งแก ้ โค ้ ตเป ็ นอาทิตย์ๆเพื่อให ้ มัน FUD คุณก็จะ เริ่มท ามันได ้ เร็วขึ้นกว่าเดิม วันสองวันก็เสร็จ ถ ้ าเกิดแก ้ แล ้ วแก ้ อีกยังไงมันก็ไม่ FUD สักทีนั้นแปลว่าโค ้ ตในไฟล์ Stub ของคุณนั้นไปซ ้ากับของคนอื่นครับ (เรา อาจจะไม่ได ้  Copy เขามาแต่เขาอาจจะเขียนโค ้ ตคล ้ ายๆกับเรา) และถูกแอนตี้ ไวรัสบันทึกว่าโค ้ ตบรรทัดนั้นๆเป ็ นไวรัสไปแล ้ ว ในกรณีนี้คุณต ้ องเขียนโค ้ ตไฟล์ Stub ของคุณใหม่ทั้งหมดครับให ้ ใช่แนวทางเทคนิคของตัวเองไม่ซ ้าไม่ก็อปของ ใครแล้ วคุณก็จะได ้  Crypter ที่ FUD ที่เขียนขึ้นด ้ วยมือของคุณเอง. การที่จะเขียน ไฟล์ Stub ขึ้นมาใหม่ทั้งหมดคุณจ าเป็นต ้ องมีความรู ้ ความช านาญในการใช ้ ภาษา VB.NET เป็นอย่างมาก ดังนั้นผมแนะน าให ้ ศึกษาภาษา VB.NET ควบคู่กันไปนะ

ครับ. ภาษา VB.NET เป็นภาษาที่เรียนง่ายเรียนไวครับ แต่ที่ยากจริงๆคือเทคนิค การเขียนโค ้ ตของแต่ละคนนั้นไม่เหมือนกัน โปรแกรม Crypter ของคุณจะออกมา ได้ มาตรฐานแค่ไหนก็ขึ้นอยู่กับฝีมือและจินตนาการของแต่ละคนว่าจะเขียนไฟล์ Stub ออกมาได้ ซับซ ้ อนและไม่ซ ้าใครขนาดไหน.

ขอบคุณครับ Pound - Administrator Hackdee.biz