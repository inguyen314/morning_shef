# morning_shef
Import Forecast Outflow Data From Lake Sheets (WM_MVS_LAKE Schemas) and NETMISS then convert to SHEF file format. (Save to Z, Email and Push to Public Site)

REQUIRED: Map the Z Drive
REQUIRED: Install Putty from App Portal (Simon Tatham PuTTY 0.78 (64-bit))
REQUIRED: (FOR FIRST TIME USER ONLY) RUN THE COMMAND BELOW IN WINDOWS'S "COMMAND PROMPT". Take Out the double quotes. When prompted, type "y"
"pscp -i Z:\DailyOps\morning_shef\id_rsa.ppk Z:\DailyOps\morning_shef\morning_shef_test.shef d1wm1a95@199.124.16.152:/I:/web/mvs-wc/inetpub/wwwroot/morning_shef_allen.txt"


Step 01. Open CWMS-VUE > Tools > Script Editor

Step 02. Right click on "HecDssVue" > "New Script"

Step 03. Go to repository https://github.com/inguyen314/morning_shef

Step 04. Click and Open "morning_shef.py" file in the repository

Step 05. Copy everything from morning_shef.py to "New Script" and name the label to "morning_shef"

Step 06. Click "Save and Test"

Step 07. Enter you notes for each lake/ld when a window is prompted

Step 08. Verify the morning_shef data is correct, make changes if needed

Step 09. Click the "X" on the top right corner

Steo 10. Click "Yes" when prompted. Click "No" if you dont want to send

Step 11. Send email completed via pop-up message
