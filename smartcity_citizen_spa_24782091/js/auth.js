let currentUser = null;

async function loadCurrentUser() {
    if (!isLoggedIn()) {
        currentUser = null;
        return null;
    }

    const result = await requestAPI("/api/me/", "GET");
    if (result.status === 200) {
        currentUser = result.data;
        return currentUser;
    }

    currentUser = null;
    return null;
}

function isAdmin() {
    return Boolean(currentUser?.is_admin);
}

function setupLoginForm() {
    const loginForm = document.getElementById("loginForm");
    if (!loginForm) {
        return;
    }

    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const username = document.getElementById("loginUsername").value.trim();
        const password = document.getElementById("loginPassword").value;

        const result = await requestAPI("/api/token/", "POST", {
            username,
            password,
        });

        if (result.status === 200) {
            localStorage.setItem("access_token", result.data.access);
            localStorage.setItem("refresh_token", result.data.refresh);
            await loadCurrentUser();
            alert("Login berhasil.");
            window.location.hash = "#dashboard";
            return;
        }

        alert("Login gagal. Periksa username dan password.");
    });
}

function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    currentUser = null;
    window.location.hash = "#login";
}

function isLoggedIn() {
    return Boolean(localStorage.getItem("access_token"));
}
