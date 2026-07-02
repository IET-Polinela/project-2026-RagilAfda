# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: tests\citizen_portal.spec.js >> Modul 5: Interaktivitas UI (UI-01 through UI-06) >> UI-06: Responsive navbar pada viewport mobile (400x800)
- Location: tests\citizen_portal.spec.js:1317:5

# Error details

```
Error: page.goto: net::ERR_FILE_NOT_FOUND at file:///D:/projekgit/project-2026-RagilAfda/smartcity_citizen_spa/index.html
Call log:
  - navigating to "file:///D:/projekgit/project-2026-RagilAfda/smartcity_citizen_spa/index.html", waiting until "load"

```

# Test source

```ts
  1234 |         );
  1235 | 
  1236 |         // -------------------------------------------------------------------
  1237 |         // LANGKAH 5: Klik tombol "Simpan Draft" (#btnDraft)
  1238 |         // -------------------------------------------------------------------
  1239 |         // Tombol ini akan memanggil kirimLaporan('DRAFT') di app.js
  1240 |         await page.locator('#btnDraft').click();
  1241 | 
  1242 |         // Tunggu proses POST selesai dan modal menutup
  1243 |         await page.waitForTimeout(2000);
  1244 |         expect(draftSubmitted).toBe(true);
  1245 | 
  1246 |         // -------------------------------------------------------------------
  1247 |         // LANGKAH 6: Verifikasi modal tertutup setelah submit berhasil
  1248 |         // -------------------------------------------------------------------
  1249 |         // Setelah berhasil, app.js memanggil reportModalInstance.hide()
  1250 |         const reportModal = page.locator('#reportModal');
  1251 |         await expect(reportModal).not.toBeVisible({ timeout: 5000 });
  1252 | 
  1253 |         // -------------------------------------------------------------------
  1254 |         // LANGKAH 7: Verifikasi notifikasi sukses muncul
  1255 |         // -------------------------------------------------------------------
  1256 |         // Kita sudah menangkap alert message di event handler di atas
  1257 |         //
  1258 |         // app.js baris 387: alert('Laporan berhasil disimpan sebagai DRAFT')
  1259 |         expect(alertMessage).toContain('berhasil');
  1260 | 
  1261 |         // -------------------------------------------------------------------
  1262 |         // LANGKAH 8: Verifikasi badge Draf di summaryStats terupdate
  1263 |         // -------------------------------------------------------------------
  1264 |         // Setelah simpan berhasil, loadDashboardData() dipanggil yang
  1265 |         // memanggil loadSummaryStats(). Badge Draf harus menunjukkan angka > 0.
  1266 |         //
  1267 |         await page.waitForTimeout(2000);
  1268 |         await page.goto(`${SPA_URL}#reports`);
  1269 |         await page.waitForSelector('#draftCount', { state: 'visible', timeout: 10000 });
  1270 | 
  1271 |         const draftBadge = page.locator('#draftCount');
  1272 |         await expect(draftBadge).toBeVisible();
  1273 | 
  1274 |         // Cek bahwa ada setidaknya satu badge yang menunjukkan angka > 0
  1275 |         const draftCountText = await draftBadge.textContent();
  1276 |         const draftCount = parseInt(draftCountText, 10);
  1277 | 
  1278 |         expect(draftCount).toBeGreaterThanOrEqual(1);
  1279 | 
  1280 |         console.log(`[UI-05] ✅ Draft tersimpan: modal tutup, alert muncul, badge Draf = ${draftCount}`);
  1281 |     });
  1282 | 
  1283 |     // =========================================================================
  1284 |     // TEST CASE: UI-06
  1285 |     // =========================================================================
  1286 |     // JUDUL:
  1287 |     //   Responsive Design: Navbar collapse pada viewport mobile
  1288 |     //
  1289 |     // SKENARIO:
  1290 |     //   Set viewport ke ukuran mobile (400x800), muat halaman SPA, dan
  1291 |     //   verifikasi bahwa navbar dalam keadaan collapsed (tombol toggler
  1292 |     //   terlihat, atau menu collapse tidak ditampilkan secara default).
  1293 |     //
  1294 |     // KONSEP TEKNIS:
  1295 |     //   - Bootstrap Responsive Navbar:
  1296 |     //     - navbar-expand-lg: collapse di bawah breakpoint lg (992px)
  1297 |     //     - navbar-toggler: tombol hamburger yang muncul saat collapsed
  1298 |     //     - collapse navbar-collapse: div yang di-toggle show/hide
  1299 |     //
  1300 |     // REFERENSI KODE:
  1301 |     //   index.html baris 16-23:
  1302 |     //     <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
  1303 |     //       ...
  1304 |     //       <div id="nav-menus" class="ms-auto">
  1305 |     //
  1306 |     //   CATATAN: Navbar SPA ini menggunakan struktur sederhana tanpa
  1307 |     //   Bootstrap collapse standard (tidak ada .navbar-collapse).
  1308 |     //   Elemen #nav-menus langsung berada di dalam navbar.
  1309 |     //   Saat viewport kecil, elemen-elemen navbar akan wrap/stack.
  1310 |     //
  1311 |     // PLAYWRIGHT VIEWPORT TESTING:
  1312 |     //   Kita dapat mengatur ukuran viewport per test pada Playwright.
  1313 |     //   Ini lebih handal dari CSS media query test karena benar-benar
  1314 |     //   mengubah dimensi rendering browser.
  1315 |     //
  1316 |     // =========================================================================
  1317 |     test('UI-06: Responsive navbar pada viewport mobile (400x800)', async ({ page }) => {
  1318 |         // -------------------------------------------------------------------
  1319 |         // LANGKAH 1: Set viewport ke ukuran mobile
  1320 |         // -------------------------------------------------------------------
  1321 |         // page.setViewportSize() mengubah dimensi viewport browser.
  1322 |         // Ini mensimulasikan pengguna yang membuka halaman di smartphone.
  1323 |         //
  1324 |         // Ukuran 400x800 adalah ukuran umum smartphone
  1325 |         //
  1326 |         // Catatan: Ini HANYA mengubah viewport, bukan user agent.
  1327 |         // Jika perlu mengubah user agent, gunakan page.context().
  1328 |         //
  1329 |         await page.setViewportSize({ width: 400, height: 800 });
  1330 | 
  1331 |         // -------------------------------------------------------------------
  1332 |         // LANGKAH 2: Navigasi ke SPA
  1333 |         // -------------------------------------------------------------------
> 1334 |         await page.goto(SPA_URL);
       |                    ^ Error: page.goto: net::ERR_FILE_NOT_FOUND at file:///D:/projekgit/project-2026-RagilAfda/smartcity_citizen_spa/index.html
  1335 |         await page.waitForLoadState('domcontentloaded');
  1336 | 
  1337 |         // -------------------------------------------------------------------
  1338 |         // LANGKAH 3: Verifikasi navbar ada dan terlihat
  1339 |         // -------------------------------------------------------------------
  1340 |         const navbar = page.locator('.navbar');
  1341 |         await expect(navbar).toBeVisible({ timeout: 5000 });
  1342 | 
  1343 |         // -------------------------------------------------------------------
  1344 |         // LANGKAH 4: Verifikasi responsive behavior
  1345 |         // -------------------------------------------------------------------
  1346 |         // Navbar menggunakan class 'navbar-expand-lg' yang berarti:
  1347 |         // - Di atas 992px: navbar expanded (horizontal, semua item terlihat)
  1348 |         // - Di bawah 992px: navbar collapsed (vertikal, tombol toggler muncul)
  1349 |         //
  1350 |         // Viewport kita 400px < 992px, jadi navbar harus dalam state collapsed.
  1351 |         //
  1352 |         // STRATEGI VERIFIKASI:
  1353 |         // Struktur navbar di SPA ini sederhana (tanpa navbar-collapse standard).
  1354 |         // Kita verifikasi bahwa di viewport mobile, navbar toggler button
  1355 |         // terlihat ATAU elemen #nav-menus memiliki layout terbatas.
  1356 |         //
  1357 |         // -------------------------------------------------------------------
  1358 | 
  1359 |         // Cek apakah ada tombol navbar-toggler (Bootstrap standard)
  1360 |         const navbarToggler = page.locator('.navbar-toggler');
  1361 |         const togglerCount = await navbarToggler.count();
  1362 | 
  1363 |         if (togglerCount > 0) {
  1364 |             // Jika ada tombol toggler, pastikan ia terlihat di mobile
  1365 |             await expect(navbarToggler).toBeVisible();
  1366 |             console.log('[UI-06] ✓ Navbar toggler (hamburger) button terlihat di mobile');
  1367 | 
  1368 |             // Verifikasi bahwa collapse container tidak dalam state 'show'
  1369 |             const navbarCollapse = page.locator('.navbar-collapse');
  1370 |             const collapseCount = await navbarCollapse.count();
  1371 |             if (collapseCount > 0) {
  1372 |                 const hasShow = await navbarCollapse.evaluate(
  1373 |                     (el) => el.classList.contains('show')
  1374 |                 );
  1375 |                 // Secara default, collapse tidak memiliki class 'show' di mobile
  1376 |                 expect(hasShow).toBe(false);
  1377 |                 console.log('[UI-06] ✓ Navbar collapse TIDAK dalam state "show" (tersembunyi)');
  1378 |             }
  1379 |         } else {
  1380 |             // Jika tidak ada toggler (struktur navbar sederhana seperti di SPA ini),
  1381 |             // verifikasi bahwa navbar memiliki layout yang sesuai untuk mobile
  1382 |             //
  1383 |             // Verifikasi bahwa lebar navbar sesuai viewport
  1384 |             const navbarBox = await navbar.boundingBox();
  1385 |             expect(navbarBox).not.toBeNull();
  1386 | 
  1387 |             // Lebar navbar harus <= lebar viewport (400px)
  1388 |             expect(navbarBox.width).toBeLessThanOrEqual(400);
  1389 | 
  1390 |             // Verifikasi elemen nav-menus masih ada
  1391 |             const navMenus = page.locator('#nav-menus');
  1392 |             const navMenusCount = await navMenus.count();
  1393 |             expect(navMenusCount).toBeGreaterThanOrEqual(1);
  1394 | 
  1395 |             console.log('[UI-06] ✓ Navbar beradaptasi dengan viewport mobile (400px)');
  1396 |         }
  1397 | 
  1398 |         // -------------------------------------------------------------------
  1399 |         // LANGKAH 5: Verifikasi kontras — bandingkan dengan viewport desktop
  1400 |         // -------------------------------------------------------------------
  1401 |         // Sebagai verifikasi tambahan, kita bisa membuktikan perbedaan
  1402 |         // antara layout mobile dan desktop.
  1403 |         //
  1404 |         // Simpan state mobile untuk perbandingan
  1405 |         const mobileNavbarBox = await navbar.boundingBox();
  1406 |         const mobileWidth = mobileNavbarBox?.width || 0;
  1407 | 
  1408 |         // Ubah ke viewport desktop
  1409 |         await page.setViewportSize({ width: 1280, height: 800 });
  1410 |         await page.waitForTimeout(500); // Tunggu re-layout / Wait for re-layout
  1411 | 
  1412 |         const desktopNavbarBox = await navbar.boundingBox();
  1413 |         const desktopWidth = desktopNavbarBox?.width || 0;
  1414 | 
  1415 |         // Navbar desktop harus lebih lebar dari mobile
  1416 |         expect(desktopWidth).toBeGreaterThan(mobileWidth);
  1417 | 
  1418 |         console.log(`[UI-06] ✅ Responsive terverifikasi: mobile=${mobileWidth}px, desktop=${desktopWidth}px`);
  1419 | 
  1420 |         // Reset viewport ke default (opsional, untuk test berikutnya)
  1421 |         await page.setViewportSize({ width: 1280, height: 720 });
  1422 |     });
  1423 | });
  1424 | 
  1425 | 
  1426 | // #############################################################################
  1427 | // #                                                                           #
  1428 | // #   CATATAN AKHIR                                                           #
  1429 | // #                                                                           #
  1430 | // #############################################################################
  1431 | //
  1432 | // 1. MOCK vs REAL SERVER:
  1433 | //    Test di atas menggunakan page.route() untuk mock API responses di
  1434 | //    beberapa tempat. Ini dilakukan untuk:
```