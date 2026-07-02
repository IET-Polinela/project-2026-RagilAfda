# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: tests\citizen_portal.spec.js >> Modul 5: Interaktivitas UI (UI-01 through UI-06) >> UI-03: Pagination Feed Kota — maks 10 kartu, kontrol pagination muncul
- Location: tests\citizen_portal.spec.js:856:5

# Error details

```
Error: page.goto: net::ERR_FILE_NOT_FOUND at file:///D:/projekgit/project-2026-RagilAfda/smartcity_citizen_spa/index.html
Call log:
  - navigating to "file:///D:/projekgit/project-2026-RagilAfda/smartcity_citizen_spa/index.html", waiting until "load"

```

# Test source

```ts
  760 |         // Halaman ini berisi tabel semua laporan dan input pencarian.
  761 |         // URL /reports/ didefinisikan di main_app/urls.py
  762 |         await page.goto(`${BASE_URL}/reports/`);
  763 |         await page.waitForLoadState('networkidle');
  764 | 
  765 |         // -------------------------------------------------------------------
  766 |         // LANGKAH 3: Verifikasi elemen pencarian dan tabel ada
  767 |         // -------------------------------------------------------------------
  768 |         const searchInput = page.locator('#searchInput');
  769 |         const tableBody   = page.locator('#tableBody');
  770 | 
  771 |         await expect(searchInput).toBeVisible({ timeout: 10000 });
  772 |         await expect(tableBody).toBeVisible({ timeout: 10000 });
  773 | 
  774 |         // Catat jumlah baris awal sebelum pencarian
  775 |         const initialRowCount = await tableBody.locator('tr').count();
  776 |         console.log(`[UI-02] Jumlah baris awal: ${initialRowCount}`);
  777 | 
  778 |         // -------------------------------------------------------------------
  779 |         // LANGKAH 4: Ketik keyword pencarian dan tunggu respons AJAX
  780 |         // -------------------------------------------------------------------
  781 |         // Kita menggunakan Promise.all() untuk menjalankan dua operasi secara
  782 |         // bersamaan (concurrent):
  783 |         //   1. Menunggu respons HTTP dari /search/
  784 |         //   2. Mengetik keyword ke input field
  785 |         //
  786 |         // MENGAPA Promise.all()?
  787 |         // Jika kita ketik dulu baru tunggu response, response mungkin sudah
  788 |         // datang sebelum waitForResponse dipanggil → timeout.
  789 |         const searchKeyword = 'Lampu';
  790 | 
  791 |         // Mulai mendengarkan response spesifik untuk query pencarian 'Lampu'
  792 |         const responsePromise = page.waitForResponse(
  793 |             (response) => response.url().includes(`/search/?q=${searchKeyword}`) && response.status() === 200,
  794 |             { timeout: 15000 }
  795 |         );
  796 | 
  797 |         // Ketik keyword pencarian secara berurutan
  798 |         await searchInput.click();
  799 |         await searchInput.fill('');
  800 |         await searchInput.type(searchKeyword, { delay: 100 });
  801 | 
  802 |         // Tunggu hingga respon AJAX selesai diterima
  803 |         const searchResponse = await responsePromise;
  804 | 
  805 |         // -------------------------------------------------------------------
  806 |         // LANGKAH 5: Verifikasi respons AJAX berhasil
  807 |         // -------------------------------------------------------------------
  808 |         expect(searchResponse.status()).toBe(200);
  809 | 
  810 |         // Parse data JSON dari respons
  811 |         const responseData = await searchResponse.json();
  812 |         console.log(`[UI-02] Hasil pencarian "${searchKeyword}": ${responseData.length || 0} item`);
  813 | 
  814 |         // -------------------------------------------------------------------
  815 |         // LANGKAH 6: Tunggu tabel diperbarui dan verifikasi
  816 |         // -------------------------------------------------------------------
  817 |         // Beri waktu untuk DOM update setelah data diterima
  818 |         await page.waitForTimeout(1000);
  819 | 
  820 |         // Hitung jumlah baris setelah pencarian
  821 |         const filteredRowCount = await tableBody.locator('tr').count();
  822 |         console.log(`[UI-02] Jumlah baris setelah filter: ${filteredRowCount}`);
  823 | 
  824 |         // Verifikasi: jumlah baris setelah filter harus sesuai dengan data respons
  825 |         // Jika ada hasil, baris harus > 0
  826 |         if (Array.isArray(responseData) && responseData.length > 0) {
  827 |             expect(filteredRowCount).toBeGreaterThan(0);
  828 |             expect(filteredRowCount).toBe(responseData.length);
  829 |         }
  830 | 
  831 |         console.log('[UI-02] ✅ Live search berfungsi: input → AJAX → tabel terupdate');
  832 |     });
  833 | 
  834 |     // =========================================================================
  835 |     // TEST CASE: UI-03
  836 |     // =========================================================================
  837 |     // JUDUL:
  838 |     //   Pagination: Daftar laporan publik (Feed Kota) dibatasi maks 10 item
  839 |     //
  840 |     // SKENARIO:
  841 |     //   Dengan asumsi ada 25+ laporan di database, navigasi ke SPA #dashboard,
  842 |     //   klik tab "Feed Kota (Publik)", hitung jumlah kartu laporan di
  843 |     //   #listContainer, dan pastikan tidak lebih dari 10. Juga verifikasi
  844 |     //   bahwa kontrol pagination ada di #paginationContainer.
  845 |     //
  846 |     // KONSEP TEKNIS:
  847 |     //   - Pagination server-side: API mengembalikan data terpaginasi
  848 |     //   - app.js menggunakan page_size=10 sebagai default
  849 |     //   - totalPages dihitung dari: Math.ceil(count / 10)
  850 |     //
  851 |     // REFERENSI KODE:
  852 |     //   app.js baris 64: const response = await requestAPI(`/report/?tab=${tab}&page=${page}`)
  853 |     //   app.js baris 69: totalPages = Math.ceil(count / 10) || 1;
  854 |     //   app.js baris 230-264: renderPagination() → membuat navigasi halaman
  855 |     // =========================================================================
  856 |     test('UI-03: Pagination Feed Kota — maks 10 kartu, kontrol pagination muncul', async ({ page }) => {
  857 |         // -------------------------------------------------------------------
  858 |         // LANGKAH 1: Siapkan environment (navigasi ke SPA dan setup mock)
  859 |         // -------------------------------------------------------------------
> 860 |         await page.goto(SPA_URL);
      |                    ^ Error: page.goto: net::ERR_FILE_NOT_FOUND at file:///D:/projekgit/project-2026-RagilAfda/smartcity_citizen_spa/index.html
  861 |         await mockSPAApiUrl(page);
  862 |         await mockCurrentCitizen(page);
  863 | 
  864 |         // -------------------------------------------------------------------
  865 |         // LANGKAH 2: Simulasi login dengan menyimpan token
  866 |         // -------------------------------------------------------------------
  867 |         // Untuk test ini, kita perlu berada dalam state "login" agar bisa
  868 |         // mengakses dashboard. Kita gunakan mock API untuk token dan data.
  869 |         // -------------------------------------------------------------------
  870 | 
  871 |         // Buat data mock: 25 laporan dummy untuk simulasi pagination
  872 |         const mockReports = [];
  873 |         for (let i = 1; i <= 25; i++) {
  874 |             mockReports.push({
  875 |                 id: i,
  876 |                 title: `Laporan Test #${i}`,
  877 |                 description: `Deskripsi laporan pengujian nomor ${i}`,
  878 |                 category: i % 2 === 0 ? 'Infrastruktur' : 'Kebersihan',
  879 |                 location: `Lokasi Test ${i}`,
  880 |                 status: ['REPORTED', 'VERIFIED', 'IN_PROGRESS', 'RESOLVED'][i % 4],
  881 |                 reporter_name: 'testwarga',
  882 |                 is_owner: false,
  883 |                 updated_at: new Date().toISOString()
  884 |             });
  885 |         }
  886 | 
  887 |         // Mock API endpoint untuk report list (feed tab, halaman 1)
  888 |         await page.route('**/api/reports/**', async (route) => {
  889 |             const url = route.request().url();
  890 | 
  891 |             if (url.includes('tab=feed') || url.includes('tab=my_reports')) {
  892 |                 // Ambil nomor halaman dari URL (default: 1)
  893 |                 const pageMatch = url.match(/page=(\d+)/);
  894 |                 const pageNum = pageMatch ? parseInt(pageMatch[1]) : 1;
  895 | 
  896 |                 // Hitung subset data untuk halaman ini (10 per halaman)
  897 |                 const pageSize = 10;
  898 |                 const startIdx = (pageNum - 1) * pageSize;
  899 |                 const endIdx = startIdx + pageSize;
  900 |                 const pageData = mockReports.slice(startIdx, endIdx);
  901 | 
  902 |                 await route.fulfill({
  903 |                     status: 200,
  904 |                     contentType: 'application/json',
  905 |                     body: JSON.stringify({
  906 |                         count: mockReports.length,   // Total: 25
  907 |                         results: pageData,            // 10 per halaman
  908 |                         next: endIdx < mockReports.length ? 'next_page_url' : null,
  909 |                         previous: pageNum > 1 ? 'prev_page_url' : null
  910 |                     })
  911 |                 });
  912 |             } else {
  913 |                 // Untuk endpoint lain, kembalikan respons kosong
  914 |                 await route.fulfill({
  915 |                     status: 200,
  916 |                     contentType: 'application/json',
  917 |                     body: JSON.stringify({ count: 0, results: [] })
  918 |                 });
  919 |             }
  920 |         });
  921 | 
  922 |         // Simpan token valid ke localStorage agar bisa akses dashboard
  923 |         await setupAuthTokens(page, VALID_ACCESS_TOKEN, EXPIRED_REFRESH_TOKEN);
  924 | 
  925 |         // Handle alert dialog (jika muncul)
  926 |         page.on('dialog', async (dialog) => await dialog.accept());
  927 | 
  928 |         // -------------------------------------------------------------------
  929 |         // LANGKAH 3: Navigasi ke halaman laporan
  930 |         // -------------------------------------------------------------------
  931 |         await page.goto(`${SPA_URL}#reports`);
  932 |         await page.waitForSelector('#listContainer', { state: 'visible', timeout: 10000 });
  933 | 
  934 |         // -------------------------------------------------------------------
  935 |         // LANGKAH 4: Klik tab "Feed Kota (Publik)"
  936 |         // -------------------------------------------------------------------
  937 |         // Tab ini ada di renderReportsPage() sebagai data-report-tab="feed"
  938 |         const tabFeedKota = page.locator('[data-report-tab="feed"]');
  939 |         await expect(tabFeedKota).toBeVisible();
  940 |         await tabFeedKota.click();
  941 | 
  942 |         // Tunggu data dimuat (AJAX call + render)
  943 |         await page.waitForTimeout(2000);
  944 | 
  945 |         // -------------------------------------------------------------------
  946 |         // LANGKAH 5: Hitung jumlah kartu laporan di listContainer
  947 |         // -------------------------------------------------------------------
  948 |         // Setiap laporan dirender sebagai <div class="col-12"> di dalam #listContainer
  949 |         const listContainer = page.locator('#listContainer');
  950 |         await expect(listContainer).toBeVisible();
  951 | 
  952 |         const reportCards = listContainer.locator('.col-12');
  953 |         const cardCount = await reportCards.count();
  954 | 
  955 |         // Assertion: jumlah kartu tidak boleh lebih dari 10
  956 |         expect(cardCount).toBeLessThanOrEqual(10);
  957 |         expect(cardCount).toBeGreaterThan(0);
  958 | 
  959 |         console.log(`[UI-03] Jumlah kartu di Feed Kota: ${cardCount} (maks 10)`);
  960 | 
```