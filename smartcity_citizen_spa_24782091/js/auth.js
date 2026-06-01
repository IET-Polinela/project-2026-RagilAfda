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
    window.location.hash = "#login";
}

function isLoggedIn() {
    return Boolean(localStorage.getItem("access_token"));
}
