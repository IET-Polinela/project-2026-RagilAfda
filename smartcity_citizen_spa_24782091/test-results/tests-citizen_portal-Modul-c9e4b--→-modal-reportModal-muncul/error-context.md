# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: tests\citizen_portal.spec.js >> Modul 5: Interaktivitas UI (UI-01 through UI-06) >> UI-04: Klik tombol Buat Laporan → modal #reportModal muncul
- Location: tests\citizen_portal.spec.js:1001:5

# Error details

```
Error: page.goto: net::ERR_FILE_NOT_FOUND at file:///D:/projekgit/project-2026-RagilAfda/smartcity_citizen_spa/index.html
Call log:
  - navigating to "file:///D:/projekgit/project-2026-RagilAfda/smartcity_citizen_spa/index.html", waiting until "load"

```

# Test source

```ts
  905  |                     body: JSON.stringify({
  906  |                         count: mockReports.length,   // Total: 25
  907  |                         results: pageData,            // 10 per halaman
  908  |                         next: endIdx < mockReports.length ? 'next_page_url' : null,
  909  |                         previous: pageNum > 1 ? 'prev_page_url' : null
  910  |                     })
  911  |                 });
  912  |             } else {
  913  |                 // Untuk endpoint lain, kembalikan respons kosong
  914  |                 await route.fulfill({
  915  |                     status: 200,
  916  |                     contentType: 'application/json',
  917  |                     body: JSON.stringify({ count: 0, results: [] })
  918  |                 });
  919  |             }
  920  |         });
  921  | 
  922  |         // Simpan token valid ke localStorage agar bisa akses dashboard
  923  |         await setupAuthTokens(page, VALID_ACCESS_TOKEN, EXPIRED_REFRESH_TOKEN);
  924  | 
  925  |         // Handle alert dialog (jika muncul)
  926  |         page.on('dialog', async (dialog) => await dialog.accept());
  927  | 
  928  |         // -------------------------------------------------------------------
  929  |         // LANGKAH 3: Navigasi ke halaman laporan
  930  |         // -------------------------------------------------------------------
  931  |         await page.goto(`${SPA_URL}#reports`);
  932  |         await page.waitForSelector('#listContainer', { state: 'visible', timeout: 10000 });
  933  | 
  934  |         // -------------------------------------------------------------------
  935  |         // LANGKAH 4: Klik tab "Feed Kota (Publik)"
  936  |         // -------------------------------------------------------------------
  937  |         // Tab ini ada di renderReportsPage() sebagai data-report-tab="feed"
  938  |         const tabFeedKota = page.locator('[data-report-tab="feed"]');
  939  |         await expect(tabFeedKota).toBeVisible();
  940  |         await tabFeedKota.click();
  941  | 
  942  |         // Tunggu data dimuat (AJAX call + render)
  943  |         await page.waitForTimeout(2000);
  944  | 
  945  |         // -------------------------------------------------------------------
  946  |         // LANGKAH 5: Hitung jumlah kartu laporan di listContainer
  947  |         // -------------------------------------------------------------------
  948  |         // Setiap laporan dirender sebagai <div class="col-12"> di dalam #listContainer
  949  |         const listContainer = page.locator('#listContainer');
  950  |         await expect(listContainer).toBeVisible();
  951  | 
  952  |         const reportCards = listContainer.locator('.col-12');
  953  |         const cardCount = await reportCards.count();
  954  | 
  955  |         // Assertion: jumlah kartu tidak boleh lebih dari 10
  956  |         expect(cardCount).toBeLessThanOrEqual(10);
  957  |         expect(cardCount).toBeGreaterThan(0);
  958  | 
  959  |         console.log(`[UI-03] Jumlah kartu di Feed Kota: ${cardCount} (maks 10)`);
  960  | 
  961  |         // -------------------------------------------------------------------
  962  |         // LANGKAH 6: Verifikasi kontrol pagination muncul
  963  |         // -------------------------------------------------------------------
  964  |         // Karena ada 25 laporan dan 10 per halaman, harus ada 3 halaman.
  965  |         // renderPagination() (app.js baris 230) akan membuat navigasi halaman.
  966  |         const paginationContainer = page.locator('#paginationContainer');
  967  |         await expect(paginationContainer).toBeVisible();
  968  | 
  969  |         // Verifikasi ada tombol navigasi halaman (page numbers, prev, next)
  970  |         const paginationButtons = paginationContainer.locator('.page-item');
  971  |         const paginationCount = await paginationButtons.count();
  972  | 
  973  |         // Harus ada minimal 3 tombol: Sebelumnya, 1, 2, 3, Selanjutnya = 5 tombol
  974  |         expect(paginationCount).toBeGreaterThanOrEqual(3);
  975  | 
  976  |         console.log(`[UI-03] ✅ Pagination terverifikasi: ${cardCount} kartu, ${paginationCount} tombol navigasi`);
  977  |     });
  978  | 
  979  |     // =========================================================================
  980  |     // TEST CASE: UI-04
  981  |     // =========================================================================
  982  |     // JUDUL:
  983  |     //   Modal Dialog: Tombol "Buat Laporan Baru" membuka modal #reportModal
  984  |     //
  985  |     // SKENARIO:
  986  |     //   Login ke SPA, navigasi ke #dashboard, klik tombol create report,
  987  |     //   dan verifikasi bahwa modal Bootstrap #reportModal muncul (visible).
  988  |     //
  989  |     // REFERENSI KODE:
  990  |     //   - app.js baris 282-292: setupDashboardEvents() → pasang event listener
  991  |     //     tombol data-create-report membuka modal Bootstrap
  992  |     //         reportModalInstance.show();
  993  |     //     });
  994  |     //   - index.html baris 31: <div class="modal fade" id="reportModal">
  995  |     //
  996  |     // KONSEP TEKNIS:
  997  |     //   - Bootstrap Modal: overlay dialog yang dimunculkan dengan JS
  998  |     //   - Class 'show' ditambahkan ke modal saat ditampilkan
  999  |     //   - Modal instance dibuat dengan: new bootstrap.Modal(element)
  1000 |     // =========================================================================
  1001 |     test('UI-04: Klik tombol Buat Laporan → modal #reportModal muncul', async ({ page }) => {
  1002 |         // -------------------------------------------------------------------
  1003 |         // LANGKAH 1: Setup state login dan mock API
  1004 |         // -------------------------------------------------------------------
> 1005 |         await page.goto(SPA_URL);
       |                    ^ Error: page.goto: net::ERR_FILE_NOT_FOUND at file:///D:/projekgit/project-2026-RagilAfda/smartcity_citizen_spa/index.html
  1006 | 
  1007 |         // Mock semua API calls agar tidak gagal
  1008 |         await page.route('**/api/**', async (route) => {
  1009 |             if (route.request().url().includes('/api/me/')) {
  1010 |                 await route.fulfill({
  1011 |                     status: 200,
  1012 |                     contentType: 'application/json',
  1013 |                     body: JSON.stringify({
  1014 |                         id: 1,
  1015 |                         username: TEST_CITIZEN_USERNAME,
  1016 |                         is_admin: false,
  1017 |                         is_staff: false
  1018 |                     })
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
```