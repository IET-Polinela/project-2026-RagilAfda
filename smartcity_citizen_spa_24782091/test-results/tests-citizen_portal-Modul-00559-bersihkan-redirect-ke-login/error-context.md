# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: tests\citizen_portal.spec.js >> Modul 1: Otorisasi & Sesi (AUTH-04, AUTH-05, AUTH-06) >> AUTH-06: Kedua token kadaluarsa → localStorage dibersihkan, redirect ke #login
- Location: tests\citizen_portal.spec.js:532:5

# Error details

```
Error: page.goto: net::ERR_FILE_NOT_FOUND at file:///D:/projekgit/project-2026-RagilAfda/smartcity_citizen_spa/index.html
Call log:
  - navigating to "file:///D:/projekgit/project-2026-RagilAfda/smartcity_citizen_spa/index.html", waiting until "load"

```

# Test source

```ts
  210 |         // localStorage.clear() menghapus SEMUA data di localStorage domain ini
  211 |         localStorage.clear();
  212 |     });
  213 | }
  214 | 
  215 | /**
  216 |  * mockSPAApiUrl - Memastikan SEMUA request API di SPA mengarah ke localhost:8000
  217 |  *
  218 |  * Menggunakan wildcard API global, fungsi ini akan mencegat request ke domain apapun
  219 |  * (misal: http://103.151.63.71:8013/api, http://192.168.1.5/api, dll)
  220 |  * dan membelokkannya secara paksa ke server Django lokal di http://localhost:8000/api.
  221 |  *
  222 |  * @param {import('@playwright/test').Page} page - Objek halaman Playwright
  223 |  */
  224 | async function mockSPAApiUrl(page) {
  225 |     const BASE_URL = 'http://103.151.63.88:8008';
  226 | 
  227 |     // Gunakan wildcard **/api/** untuk menangkap dari host/domain mana saja
  228 |     await page.route('**/api/**', async (route) => {
  229 |         const originalUrl = route.request().url();
  230 | 
  231 |         // [PENTING] Mencegah infinite loop: 
  232 |         // Jika request sudah benar mengarah ke localhost:8000, biarkan saja lewat.
  233 |         if (originalUrl.startsWith(BASE_URL)) {
  234 |             return route.continue();
  235 |         }
  236 | 
  237 |         // Parsing URL asli menggunakan objek URL bawaan JavaScript
  238 |         const urlObj = new URL(originalUrl);
  239 |         
  240 |         // urlObj.pathname akan mengambil "/api/endpoint/"
  241 |         // urlObj.search akan mengambil query string (misal: "?search=jalan") jika ada
  242 |         const newUrl = `${BASE_URL}${urlObj.pathname}${urlObj.search}`;
  243 | 
  244 |         // Lanjutkan request dengan URL yang sudah dibelokkan ke localhost
  245 |         await route.continue({ url: newUrl });
  246 |     });
  247 | }
  248 | 
  249 | /**
  250 |  * mockCurrentCitizen - Mock endpoint /api/me/ agar token dummy dianggap
  251 |  * sebagai warga biasa yang sudah login.
  252 |  *
  253 |  * @param {import('@playwright/test').Page} page - Objek halaman Playwright
  254 |  */
  255 | async function mockCurrentCitizen(page) {
  256 |     await page.route('**/api/me/**', async (route) => {
  257 |         await route.fulfill({
  258 |             status: 200,
  259 |             contentType: 'application/json',
  260 |             body: JSON.stringify({
  261 |                 id: 1,
  262 |                 username: TEST_CITIZEN_USERNAME,
  263 |                 is_admin: false,
  264 |                 is_staff: false
  265 |             })
  266 |         });
  267 |     });
  268 | }
  269 | 
  270 | 
  271 | // #############################################################################
  272 | // #                                                                           #
  273 | // #   MODUL 1: OTORISASI & SESI (AUTH-04, AUTH-05, AUTH-06)                   #
  274 | // #                                                                           #
  275 | // #   Modul ini menguji mekanisme perlindungan rute (auth guard) pada SPA.    #
  276 | // #                                                                           #
  277 | // #   Konsep yang diuji:                                                      #
  278 | // #   - Auth Guard: redirect pengguna yang belum login ke halaman login       #
  279 | // #   - Token Expiry: penanganan token JWT yang sudah kadaluarsa              #
  280 | // #   - Session Cleanup: pembersihan localStorage saat sesi berakhir          #
  281 | // #                                                                           #
  282 | // #############################################################################
  283 | 
  284 | test.describe('Modul 1: Otorisasi & Sesi (AUTH-04, AUTH-05, AUTH-06)', () => {
  285 |     // =========================================================================
  286 |     // PENGANTAR MODUL
  287 |     // =========================================================================
  288 |     // Setiap aplikasi SPA yang menggunakan token-based authentication (JWT)
  289 |     // harus memiliki mekanisme auth guard yang melindungi halaman tertentu
  290 |     // dari akses tanpa otentikasi.
  291 |     //
  292 |     // Dalam aplikasi ini (lihat router.js baris 122-139):
  293 |     //   - Fungsi handleRouting() memeriksa token di localStorage
  294 |     //   - Jika TIDAK ada token dan user mengakses #dashboard → redirect ke #login
  295 |     //   - Jika ADA token dan user mengakses #login/#register → redirect ke #dashboard
  296 |     // =========================================================================
  297 | 
  298 |     // -------------------------------------------------------------------------
  299 |     // beforeEach: Dijalankan sebelum SETIAP test dalam describe block ini.
  300 |     //
  301 |     // Tujuan: Membersihkan state browser agar setiap test independen.
  302 |     //
  303 |     // PRINSIP TESTING:
  304 |     //   Setiap test harus bisa berjalan secara independen (isolated).
  305 |     //   Hasil test A tidak boleh mempengaruhi test B.
  306 |     // -------------------------------------------------------------------------
  307 |     test.beforeEach(async ({ page }) => {
  308 |         // 1. Navigasi ke SPA terlebih dahulu agar localStorage tersedia
  309 |         //    (localStorage hanya tersedia setelah halaman dimuat)
> 310 |         await page.goto(SPA_URL);
      |                    ^ Error: page.goto: net::ERR_FILE_NOT_FOUND at file:///D:/projekgit/project-2026-RagilAfda/smartcity_citizen_spa/index.html
  311 | 
  312 |         // 2. Bersihkan localStorage untuk memastikan state bersih
  313 |         await clearAuthTokens(page);
  314 | 
  315 |         // 3. Setup route interceptor agar API calls diarahkan ke localhost
  316 |         await mockSPAApiUrl(page);
  317 |     });
  318 | 
  319 |     // =========================================================================
  320 |     // TEST CASE: AUTH-04
  321 |     // =========================================================================
  322 |     // JUDUL:
  323 |     //   Auth Guard: Akses dashboard tanpa token harus redirect ke login
  324 |     //
  325 |     // SKENARIO:
  326 |     //   Pengguna yang BELUM login (tidak memiliki access_token di localStorage)
  327 |     //   mencoba mengakses halaman #dashboard secara langsung melalui URL.
  328 |     //
  329 |     // EKSPEKTASI:
  330 |     //   Router SPA (handleRouting di router.js) mendeteksi tidak ada token
  331 |     //   dan melakukan redirect otomatis ke #login.
  332 |     //
  333 |     // REFERENSI KODE:
  334 |     //   Lihat router.js baris 133-138:
  335 |     //     } else {
  336 |     //         if (hash === '#dashboard') {
  337 |     //             window.location.hash = '#login';
  338 |     //             return;
  339 |     //         }
  340 |     //     }
  341 |     // =========================================================================
  342 |     test('AUTH-04: Akses #dashboard tanpa token → redirect ke #login', async ({ page }) => {
  343 |         // -------------------------------------------------------------------
  344 |         // LANGKAH 1: Pastikan localStorage benar-benar kosong (tidak ada token)
  345 |         // -------------------------------------------------------------------
  346 |         const tokenBefore = await page.evaluate(() => {
  347 |             // Jalankan di browser: cek apakah ada access_token
  348 |             return localStorage.getItem('access_token');
  349 |         });
  350 | 
  351 |         // Assertion: token harus null (tidak ada)
  352 |         expect(tokenBefore).toBeNull();
  353 | 
  354 |         // -------------------------------------------------------------------
  355 |         // LANGKAH 2: Navigasi langsung ke #dashboard (tanpa login)
  356 |         // -------------------------------------------------------------------
  357 |         // Ini mensimulasikan pengguna yang mengetik URL langsung di address bar
  358 |         // atau mengklik bookmark ke halaman dashboard.
  359 |         await page.goto(`${SPA_URL}#dashboard`);
  360 | 
  361 |         // -------------------------------------------------------------------
  362 |         // LANGKAH 3: Tunggu router SPA melakukan redirect
  363 |         // -------------------------------------------------------------------
  364 |         // page.waitForFunction() menunggu hingga kondisi tertentu terpenuhi
  365 |         // di dalam browser. Kita menunggu hash URL berubah menjadi '#login'.
  366 |         //
  367 |         await page.waitForFunction(
  368 |             () => window.location.hash === '#login',
  369 |             null,
  370 |             { timeout: 5000 }
  371 |         );
  372 | 
  373 |         // -------------------------------------------------------------------
  374 |         // LANGKAH 4: Verifikasi bahwa URL hash sekarang adalah #login
  375 |         // -------------------------------------------------------------------
  376 |         // expect(page).toHaveURL() memeriksa URL lengkap halaman saat ini.
  377 |         // Kita gunakan regex agar fleksibel dengan base URL.
  378 |         //
  379 |         await expect(page).toHaveURL(/#login/);
  380 | 
  381 |         // -------------------------------------------------------------------
  382 |         // LANGKAH 5: Verifikasi bahwa form login ditampilkan
  383 |         // -------------------------------------------------------------------
  384 |         // Ini adalah verifikasi tambahan: bukan hanya URL yang berubah,
  385 |         // tapi konten halaman juga harus menampilkan form login.
  386 |         //
  387 |         const loginForm = page.locator('#loginForm');
  388 |         await expect(loginForm).toBeVisible({ timeout: 5000 });
  389 | 
  390 |         // Cetak info debug ke console test (opsional, untuk debugging)
  391 |         console.log('[AUTH-04] ✅ Redirect dari #dashboard ke #login berhasil diverifikasi');
  392 |     });
  393 | 
  394 |     // =========================================================================
  395 |     // TEST CASE: AUTH-05
  396 |     // =========================================================================
  397 |     // JUDUL:
  398 |     //   Token Interceptor: Access token kadaluarsa → SPA menangani 401 error
  399 |     //
  400 |     // SKENARIO:
  401 |     //   Pengguna memiliki access_token yang sudah kadaluarsa (expired) namun
  402 |     //   refresh_token masih valid. Saat SPA melakukan API call dan mendapat
  403 |     //   respons 401, interceptor di api.js harus membersihkan localStorage
  404 |     //   dan mengarahkan pengguna ke halaman login.
  405 |     //
  406 |     // CATATAN TEKNIS:
  407 |     //   Dalam kode api.js (baris 28-33), interceptor sederhana diimplementasikan:
  408 |     //     if(response.status == 401){
  409 |     //         alert('Sesi Anda telah habis atau Anda belum login.');
  410 |     //         localStorage.clear();
```