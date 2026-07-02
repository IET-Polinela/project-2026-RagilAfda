# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: tests\citizen_portal.spec.js >> Modul 5: Interaktivitas UI (UI-01 through UI-06) >> UI-05: Isi form dan simpan draft → modal tutup, notifikasi muncul
- Location: tests\citizen_portal.spec.js:1115:5

# Error details

```
Error: page.goto: net::ERR_FILE_NOT_FOUND at file:///D:/projekgit/project-2026-RagilAfda/smartcity_citizen_spa/index.html
Call log:
  - navigating to "file:///D:/projekgit/project-2026-RagilAfda/smartcity_citizen_spa/index.html", waiting until "load"

```

# Test source

```ts
  1019 |                 });
  1020 |                 return;
  1021 |             }
  1022 | 
  1023 |             // Untuk endpoint report, kembalikan data kosong
  1024 |             await route.fulfill({
  1025 |                 status: 200,
  1026 |                 contentType: 'application/json',
  1027 |                 body: JSON.stringify({ count: 0, results: [] })
  1028 |             });
  1029 |         });
  1030 | 
  1031 |         // Simpan token agar bisa akses dashboard
  1032 |         await setupAuthTokens(page, VALID_ACCESS_TOKEN, EXPIRED_REFRESH_TOKEN);
  1033 | 
  1034 |         // Handle dialog alert (jika muncul)
  1035 |         page.on('dialog', async (dialog) => await dialog.accept());
  1036 | 
  1037 |         // -------------------------------------------------------------------
  1038 |         // LANGKAH 2: Navigasi ke dashboard
  1039 |         // -------------------------------------------------------------------
  1040 |         await page.goto(`${SPA_URL}#dashboard`);
  1041 | 
  1042 |         // Tunggu tombol "Buat Laporan Baru" muncul
  1043 |         const btnBukaModal = page.locator('[data-create-report]');
  1044 |         await expect(btnBukaModal).toBeVisible({ timeout: 10000 });
  1045 | 
  1046 |         // -------------------------------------------------------------------
  1047 |         // LANGKAH 3: Verifikasi modal belum terlihat sebelum diklik
  1048 |         // -------------------------------------------------------------------
  1049 |         const reportModal = page.locator('#reportModal');
  1050 | 
  1051 |         // Modal awalnya memiliki class "modal fade" (tanpa "show")
  1052 |         // Sehingga tidak terlihat oleh pengguna
  1053 |         await expect(reportModal).not.toBeVisible();
  1054 | 
  1055 |         // -------------------------------------------------------------------
  1056 |         // LANGKAH 4: Klik tombol "Buat Laporan Baru"
  1057 |         // -------------------------------------------------------------------
  1058 |         await btnBukaModal.click();
  1059 | 
  1060 |         // -------------------------------------------------------------------
  1061 |         // LANGKAH 5: Tunggu dan verifikasi modal muncul
  1062 |         // -------------------------------------------------------------------
  1063 |         // Bootstrap menambahkan class 'show' ke modal saat ditampilkan,
  1064 |         // dan mengubah style display dari 'none' ke 'block'.
  1065 |         //
  1066 |         // Kita gunakan toBeVisible() yang secara internal memeriksa apakah
  1067 |         // elemen memiliki ukuran > 0 dan tidak di-hidden.
  1068 |         //
  1069 |         await expect(reportModal).toBeVisible({ timeout: 5000 });
  1070 | 
  1071 |         // Verifikasi tambahan: cek class 'show' pada modal
  1072 |         const hasShowClass = await reportModal.evaluate(
  1073 |             (el) => el.classList.contains('show')
  1074 |         );
  1075 |         expect(hasShowClass).toBe(true);
  1076 | 
  1077 |         // -------------------------------------------------------------------
  1078 |         // LANGKAH 6: Verifikasi form dan elemen input ada di dalam modal
  1079 |         // -------------------------------------------------------------------
  1080 |         // Form laporan harus memiliki semua field yang diperlukan
  1081 |         await expect(page.locator('#reportForm')).toBeVisible();
  1082 |         await expect(page.locator('#reportTitle')).toBeVisible();
  1083 |         await expect(page.locator('#reportCategory')).toBeVisible();
  1084 |         await expect(page.locator('#reportLocation')).toBeVisible();
  1085 |         await expect(page.locator('#reportDescription')).toBeVisible();
  1086 |         await expect(page.locator('#btnDraft')).toBeVisible();
  1087 |         await expect(page.locator('#btnSubmit')).toBeVisible();
  1088 | 
  1089 |         // Verifikasi judul modal
  1090 |         const modalTitle = page.locator('#reportModalLabel');
  1091 |         await expect(modalTitle).toContainText('Buat Laporan Baru');
  1092 | 
  1093 |         console.log('[UI-04] ✅ Modal #reportModal berhasil dibuka dengan semua elemen form');
  1094 |     });
  1095 | 
  1096 |     // =========================================================================
  1097 |     // TEST CASE: UI-05
  1098 |     // =========================================================================
  1099 |     // JUDUL:
  1100 |     //   Form Submission: Simpan Draft laporan via modal form
  1101 |     //
  1102 |     // SKENARIO:
  1103 |     //   Login ke SPA, buka modal form, isi semua field, klik "Simpan Draft",
  1104 |     //   dan verifikasi:
  1105 |     //   1. Modal tertutup setelah submit berhasil
  1106 |     //   2. Notifikasi sukses muncul (alert)
  1107 |     //   3. Badge count Draf di #draftCount terupdate
  1108 |     //
  1109 |     // REFERENSI KODE:
  1110 |     //   app.js baris 347-412: setupReportForm()
  1111 |     //   - btnDraft → kirimLaporan('DRAFT')
  1112 |     //   - Jika response.status 200/201 → reportModalInstance.hide(), alert, loadDashboardData()
  1113 |     //   - loadDashboardData() memanggil loadSummaryStats() → update badge
  1114 |     // =========================================================================
  1115 |     test('UI-05: Isi form dan simpan draft → modal tutup, notifikasi muncul', async ({ page }) => {
  1116 |         // -------------------------------------------------------------------
  1117 |         // LANGKAH 1: Setup environment
  1118 |         // -------------------------------------------------------------------
> 1119 |         await page.goto(SPA_URL);
       |                    ^ Error: page.goto: net::ERR_FILE_NOT_FOUND at file:///D:/projekgit/project-2026-RagilAfda/smartcity_citizen_spa/index.html
  1120 | 
  1121 |         // Variabel untuk tracking apakah POST draft berhasil
  1122 |         let draftSubmitted = false;
  1123 | 
  1124 |         // Mock API endpoint dengan respons yang sesuai
  1125 |         await page.route('**/api/reports/**', async (route) => {
  1126 |             const method = route.request().method();
  1127 |             const url = route.request().url();
  1128 | 
  1129 |             if (method === 'POST') {
  1130 |                 // -----------------------------------------------------------
  1131 |                 // Mock untuk POST /api/reports/ (membuat laporan baru)
  1132 |                 // -----------------------------------------------------------
  1133 |                 draftSubmitted = true;
  1134 | 
  1135 |                 // Ambil data dari request body untuk verifikasi
  1136 |                 const postData = route.request().postDataJSON();
  1137 |                 console.log(`[UI-05] POST received: ${JSON.stringify(postData)}`);
  1138 | 
  1139 |                 await route.fulfill({
  1140 |                     status: 201, // 201 Created
  1141 |                     contentType: 'application/json',
  1142 |                     body: JSON.stringify({
  1143 |                         id: 99,
  1144 |                         title: postData?.title || 'Test Draft',
  1145 |                         category: postData?.category || 'Infrastruktur',
  1146 |                         location: postData?.location || 'Test Location',
  1147 |                         description: postData?.description || 'Test Description',
  1148 |                         status: 'DRAFT',
  1149 |                         reporter_name: 'testwarga',
  1150 |                         is_owner: true
  1151 |                     })
  1152 |                 });
  1153 |             } else if (method === 'GET' && url.includes('page_size=100')) {
  1154 |                 // -----------------------------------------------------------
  1155 |                 // Mock untuk GET /api/reports/?tab=my_reports&page_size=100
  1156 |                 // (digunakan oleh loadSummaryStats() untuk menghitung badge)
  1157 |                 //
  1158 |                 // -----------------------------------------------------------
  1159 |                 await route.fulfill({
  1160 |                     status: 200,
  1161 |                     contentType: 'application/json',
  1162 |                     body: JSON.stringify({
  1163 |                         count: 1,
  1164 |                         results: [{
  1165 |                             id: 99,
  1166 |                             title: 'Test Draft',
  1167 |                             status: 'DRAFT',
  1168 |                             category: 'Infrastruktur',
  1169 |                             location: 'Gedung Lab',
  1170 |                             description: 'Deskripsi test',
  1171 |                             reporter_name: 'testwarga',
  1172 |                             is_owner: true
  1173 |                         }]
  1174 |                     })
  1175 |                 });
  1176 |             } else {
  1177 |                 // Mock default: kembalikan list kosong
  1178 |                 await route.fulfill({
  1179 |                     status: 200,
  1180 |                     contentType: 'application/json',
  1181 |                     body: JSON.stringify({ count: 0, results: [] })
  1182 |                 });
  1183 |             }
  1184 |         });
  1185 |         await mockCurrentCitizen(page);
  1186 | 
  1187 |         // Setup token
  1188 |         await setupAuthTokens(page, VALID_ACCESS_TOKEN, EXPIRED_REFRESH_TOKEN);
  1189 | 
  1190 |         // -------------------------------------------------------------------
  1191 |         // LANGKAH 2: Handle dialog alert
  1192 |         // -------------------------------------------------------------------
  1193 |         // app.js menampilkan alert setelah berhasil simpan draft:
  1194 |         //   alert('Laporan berhasil disimpan sebagai DRAFT')
  1195 |         //
  1196 |         let alertMessage = '';
  1197 |         page.on('dialog', async (dialog) => {
  1198 |             alertMessage = dialog.message();
  1199 |             console.log(`[UI-05] Alert: "${alertMessage}"`);
  1200 |             await dialog.accept();
  1201 |         });
  1202 | 
  1203 |         // -------------------------------------------------------------------
  1204 |         // LANGKAH 3: Navigasi ke dashboard dan buka modal
  1205 |         // -------------------------------------------------------------------
  1206 |         await page.goto(`${SPA_URL}#dashboard`);
  1207 |         await page.waitForSelector('[data-create-report]', { state: 'visible', timeout: 10000 });
  1208 | 
  1209 |         // Klik tombol buka modal
  1210 |         await page.locator('[data-create-report]').click();
  1211 | 
  1212 |         // Tunggu modal muncul
  1213 |         await expect(page.locator('#reportModal')).toBeVisible({ timeout: 5000 });
  1214 | 
  1215 |         // -------------------------------------------------------------------
  1216 |         // LANGKAH 4: Isi form laporan dengan data test
  1217 |         // -------------------------------------------------------------------
  1218 |         // Mengisi setiap field form satu per satu
  1219 | 
```