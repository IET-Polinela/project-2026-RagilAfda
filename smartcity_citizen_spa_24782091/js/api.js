const API_BASE_URL = "http://127.0.0.1:8000";

async function requestAPI(endpoint, method = "GET", bodyData = null) {
    const accessToken = localStorage.getItem("access_token");
    const headers = {};

    if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
    }

    const options = {
        method,
        headers,
        mode: "cors",
    };

    if (bodyData !== null) {
        headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(bodyData);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    const contentType = response.headers.get("content-type") || "";
    const responseData = contentType.includes("application/json")
        ? await response.json()
        : await response.text();

    if (response.status === 401) {
        localStorage.clear();
        window.location.hash = "#login";
    }

    return {
        ok: response.ok,
        status: response.status,
        data: responseData,
    };
}
