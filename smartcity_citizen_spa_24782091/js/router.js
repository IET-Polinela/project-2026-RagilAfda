const routes = {
    "#login": `
        <div class="row justify-content-center mt-5">
            <div class="col-12 col-md-6 col-lg-4">
                <div class="card border-0 shadow-sm p-4">
                    <h4 class="text-center fw-bold mb-4">Login Warga</h4>
                    <form id="loginForm">
                        <div class="mb-3">
                            <label for="loginUsername" class="form-label">Username</label>
                            <input type="text" id="loginUsername" class="form-control" placeholder="Username" required>
                        </div>
                        <div class="mb-3">
                            <label for="loginPassword" class="form-label">Password</label>
                            <input type="password" id="loginPassword" class="form-control" placeholder="Password" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100 fw-bold">
                            <i class="bi bi-box-arrow-in-right me-2"></i>Masuk
                        </button>
                    </form>
                    <p class="text-center text-muted small mt-4 mb-0">
                        Belum punya akun?
                        <a href="#register" class="text-decoration-none fw-semibold">Daftar di sini</a>
                    </p>
                </div>
            </div>
        </div>
    `,
    "#register": `
        <div class="row justify-content-center mt-5">
            <div class="col-12 col-md-7 col-lg-5">
                <div class="card border-0 shadow-sm p-4">
                    <h4 class="text-center fw-bold mb-2">Daftar Warga</h4>
                    <p class="text-center text-muted mb-4">
                        Buat akun citizen untuk mengirim dan memantau laporan.
                    </p>
                    <form id="registerForm">
                        <div class="mb-3">
                            <label for="registerUsername" class="form-label">Username</label>
                            <input type="text" id="registerUsername" class="form-control" placeholder="Pilih username" required>
                        </div>
                        <div class="mb-3">
                            <label for="registerEmail" class="form-label">Email</label>
                            <input type="email" id="registerEmail" class="form-control" placeholder="nama@email.com" required>
                        </div>
                        <div class="mb-3">
                            <label for="registerPassword" class="form-label">Password</label>
                            <input type="password" id="registerPassword" class="form-control" placeholder="Minimal 8 karakter" required>
                        </div>
                        <div class="mb-3">
                            <label for="registerPasswordConfirm" class="form-label">Konfirmasi Password</label>
                            <input type="password" id="registerPasswordConfirm" class="form-control" placeholder="Ulangi password" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100 fw-bold">
                            <i class="bi bi-person-plus-fill me-2"></i>Buat Akun
                        </button>
                    </form>
                    <p class="text-center text-muted small mt-4 mb-0">
                        Sudah punya akun?
                        <a href="#login" class="text-decoration-none fw-semibold">Masuk sekarang</a>
                    </p>
                </div>
            </div>
        </div>
    `,
    "#dashboard": `
        <div class="row g-4">
            <aside class="col-12 col-lg-3">
                <div class="card border-0 p-3 shadow-sm sticky-top" style="top: 20px;">
                    <button class="btn btn-primary btn-lg w-100 fw-bold mb-3" data-create-report data-bs-toggle="modal" data-bs-target="#reportModal">
                        <i class="bi bi-plus-circle-fill me-2"></i>Laporan Baru
                    </button>
                    <div class="list-group">
                        <a href="#dashboard" class="list-group-item list-group-item-action active">
                            <i class="bi bi-house-door-fill me-2"></i>Beranda
                        </a>
                        <a href="#reports" class="list-group-item list-group-item-action">
                            <i class="bi bi-card-list me-2"></i>Daftar Laporan
                        </a>
                    </div>
                </div>
            </aside>
            <section class="col-12 col-lg-6">
                <div class="card border-0 p-5 shadow-sm text-center">
                    <i class="bi bi-inbox fs-1 text-primary"></i>
                    <h5 class="mt-3">Selamat Datang</h5>
                    <p class="small text-muted mb-0">
                        Koneksi API untuk data laporan dan fitur citizen portal akan dilanjutkan dari dashboard ini.
                    </p>
                </div>
            </section>
            <aside class="col-12 col-lg-3">
                <div class="card border-0 p-3 shadow-sm sticky-top" style="top: 20px;">
                    <h6 class="fw-bold">
                        <i class="bi bi-info-circle-fill text-primary me-2"></i>Pengumuman
                    </h6>
                    <p class="small text-muted mb-0">
                        Layout dashboard ini sudah responsif: kiri 25%, tengah 50%, kanan 25% di layar lebar dan menumpuk penuh di layar kecil.
                    </p>
                </div>
            </aside>
        </div>
    `,
    "#reports": `
        ${renderReportsPage()}
    `,
};

async function handleRouting() {
    const hash = window.location.hash || (isLoggedIn() ? "#dashboard" : "#login");
    const appContent = document.getElementById("app-content");

    if (isLoggedIn()) {
        await loadCurrentUser();
    }

    const pageContent = hash === "#reports"
        ? renderReportsPage()
        : (routes[hash] || routes["#login"]);

    renderNavMenu();
    appContent.innerHTML = pageContent;

    if (isAdmin()) {
        document.querySelectorAll("[data-create-report]").forEach((button) => {
            button.remove();
        });
    }

    if (hash === "#login") {
        if (isLoggedIn()) {
            window.location.hash = "#dashboard";
            return;
        }

        setupLoginForm();
    }

    if (hash === "#register") {
        if (isLoggedIn()) {
            window.location.hash = "#dashboard";
            return;
        }

        setupRegisterForm();
    }

    if (hash === "#reports") {
        initializeReportsPage();
    }
}

window.addEventListener("hashchange", handleRouting);
window.addEventListener("DOMContentLoaded", handleRouting);
