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
                </div>
            </div>
        </div>
    `,
    "#dashboard": `
        <div class="row g-4">
            <aside class="col-12 col-lg-3">
                <div class="card border-0 p-3 shadow-sm sticky-top" style="top: 20px;">
                    <button class="btn btn-primary btn-lg w-100 fw-bold mb-3" data-bs-toggle="modal" data-bs-target="#reportModal">
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

function handleRouting() {
    const hash = window.location.hash || "#login";
    const appContent = document.getElementById("app-content");
    const pageContent = routes[hash] || routes["#login"];

    renderNavMenu();
    appContent.innerHTML = pageContent;

    if (hash === "#login") {
        setupLoginForm();
    }

    if (hash === "#reports") {
        initializeReportsPage();
    }
}

window.addEventListener("hashchange", handleRouting);
window.addEventListener("DOMContentLoaded", handleRouting);
