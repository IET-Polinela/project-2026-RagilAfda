function renderNavMenu() {
    const navMenus = document.getElementById("nav-menus");
    if (!navMenus) {
        return;
    }

    if (isLoggedIn()) {
        navMenus.innerHTML = `
            <div class="d-flex align-items-center gap-2">
                <a href="#dashboard" class="btn btn-outline-light btn-sm">
                    <i class="bi bi-speedometer2 me-1"></i>Dashboard
                </a>
                <button class="btn btn-light btn-sm" id="logoutButton">
                    <i class="bi bi-box-arrow-right me-1"></i>Logout
                </button>
            </div>
        `;

        const logoutButton = document.getElementById("logoutButton");
        if (logoutButton) {
            logoutButton.addEventListener("click", logout);
        }

        return;
    }

    navMenus.innerHTML = `
        <a href="#login" class="btn btn-outline-light btn-sm">
            <i class="bi bi-person-circle me-1"></i>Login
        </a>
    `;
}
