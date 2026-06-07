let allReports = [];
let currentTab = "my_reports";
let currentPage = 1;
let totalPages = 0;
let editingReportId = null;
let editingReportStatus = null;

const REPORTS_PER_PAGE = 10;

const REPORT_STATUS_META = {
    DRAFT: { label: "Draft", progress: 0, colorClass: "bg-secondary" },
    REPORTED: { label: "Reported", progress: 25, colorClass: "bg-primary" },
    VERIFIED: { label: "Verified", progress: 50, colorClass: "bg-info" },
    IN_PROGRESS: { label: "In Progress", progress: 75, colorClass: "bg-warning" },
    RESOLVED: { label: "Resolved", progress: 100, colorClass: "bg-success" },
};

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

function renderReportsPage() {
    const defaultTab = isAdmin() ? "feed" : "my_reports";
    const citizenTabs = `
        <button type="button" class="btn btn-primary" data-report-tab="my_reports">Laporan Saya</button>
        <button type="button" class="btn btn-outline-primary" data-report-tab="feed">Feed</button>
    `;
    const adminTabs = `
        <button type="button" class="btn btn-primary" data-report-tab="feed">Semua Laporan</button>
    `;

    return `
        <div class="row g-4">
            <aside class="col-12 col-xl-4">
                <div class="card border-0 shadow-sm sticky-xl-top" style="top: 20px;">
                    <div class="card-body p-4">
                        <h5 class="fw-bold mb-3">Rekap Status</h5>
                        <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                            <span>Draft</span>
                            <span class="badge text-bg-secondary" id="draftCount">0</span>
                        </div>
                        <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                            <span>Reported</span>
                            <span class="badge text-bg-primary" id="reportedCount">0</span>
                        </div>
                        <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                            <span>Verified</span>
                            <span class="badge text-bg-info" id="verifiedCount">0</span>
                        </div>
                        <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                            <span>In Progress</span>
                            <span class="badge text-bg-warning" id="inProgressCount">0</span>
                        </div>
                        <div class="d-flex justify-content-between align-items-center py-2">
                            <span>Resolved</span>
                            <span class="badge text-bg-success" id="resolvedCount">0</span>
                        </div>
                    </div>
                </div>
            </aside>
            <div class="col-12 col-xl-8">
                <div class="card border-0 shadow-sm">
                    <div class="card-body p-4">
                        <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">
                            <div>
                                <h4 class="fw-bold mb-1">Daftar Laporan</h4>
                                <p class="text-muted mb-0">Data laporan warga dengan pagination dan progress penanganan.</p>
                            </div>
                            <div class="btn-group" role="group" aria-label="Filter tab laporan">
                                ${defaultTab === "feed" ? adminTabs : citizenTabs}
                            </div>
                        </div>
                        <div id="listContainer" class="row g-3"></div>
                        <div id="paginationContainer" class="mt-4"></div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function initializeReportsPage() {
    currentTab = isAdmin() ? "feed" : "my_reports";
    bindReportTabEvents();
    setupReportForm();
    loadDashboardData();
}

function bindReportTabEvents() {
    const tabButtons = document.querySelectorAll("[data-report-tab]");
    tabButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const nextTab = button.dataset.reportTab || "all";
            loadDashboardData(nextTab, 1);
        });
    });
}

function updateActiveTabButtons() {
    const tabButtons = document.querySelectorAll("[data-report-tab]");
    tabButtons.forEach((button) => {
        const isActive = button.dataset.reportTab === currentTab;
        button.className = isActive ? "btn btn-primary" : "btn btn-outline-primary";
    });
}

function getStatusMeta(status) {
    return REPORT_STATUS_META[status] || {
        label: status || "Unknown",
        progress: 0,
        colorClass: "bg-dark",
    };
}

function renderStatusOptions(selectedStatus) {
    return Object.entries(REPORT_STATUS_META)
        .filter(([status]) => status !== "DRAFT")
        .map(([status, meta]) => `
            <option value="${status}" ${status === selectedStatus ? "selected" : ""}>
                ${meta.label}
            </option>
        `)
        .join("");
}

function formatDateTime(value) {
    if (!value) {
        return "-";
    }

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString("id-ID", {
        dateStyle: "medium",
        timeStyle: "short",
    });
}

function getApiErrorMessage(response, fallbackMessage) {
    if (!response) {
        return fallbackMessage;
    }

    const responseData = response.data;
    if (typeof responseData === "string" && responseData.trim()) {
        return responseData;
    }

    if (responseData?.detail) {
        return responseData.detail;
    }

    if (typeof responseData === "object" && responseData !== null) {
        const flattenedMessages = Object.values(responseData)
            .flat()
            .filter(Boolean)
            .join(" ");

        if (flattenedMessages) {
            return flattenedMessages;
        }
    }

    return fallbackMessage;
}

function renderList() {
    const listContainer = document.getElementById("listContainer");
    if (!listContainer) {
        return;
    }

    if (!allReports.length) {
        listContainer.innerHTML = `
            <div class="col-12 text-center text-muted p-5">
                <i class="bi bi-inbox fs-1"></i>
                <p class="mt-3 mb-0">Belum ada data laporan untuk tab ini.</p>
            </div>
        `;
        return;
    }

    listContainer.innerHTML = allReports
        .map((report) => {
            const statusMeta = getStatusMeta(report.status);
            const editButton = report.can_edit
                ? `
                    <button
                        type="button"
                        class="btn btn-outline-primary btn-sm"
                        data-edit-report-id="${report.id}"
                    >
                        <i class="bi bi-pencil-square me-1"></i>Edit
                    </button>
                `
                : "";
            const deleteButton = report.can_delete
                ? `
                    <button
                        type="button"
                        class="btn btn-outline-danger btn-sm"
                        data-delete-report-id="${report.id}"
                    >
                        <i class="bi bi-trash me-1"></i>Hapus
                    </button>
                `
                : "";
            const statusControl = report.can_update_status
                ? `
                    <div class="input-group input-group-sm" style="max-width: 360px;">
                        <label class="input-group-text" for="reportStatus-${report.id}">
                            Status
                        </label>
                        <select class="form-select" id="reportStatus-${report.id}">
                            ${renderStatusOptions(report.status)}
                        </select>
                        <button
                            type="button"
                            class="btn btn-primary"
                            data-update-status-id="${report.id}"
                        >
                            Simpan Status
                        </button>
                    </div>
                `
                : "";
            const actionButtons = `${editButton}${deleteButton}${statusControl}`;

            return `
                <div class="col-12">
                    <div class="card border-0 shadow-sm h-100">
                        <div class="card-body p-4">
                            <div class="d-flex flex-column flex-md-row justify-content-between gap-3 mb-3">
                                <div>
                                    <h5 class="fw-bold mb-1">${report.title || "Tanpa Judul"}</h5>
                                    <div class="text-muted small">
                                        <i class="bi bi-tag-fill me-1"></i>${report.category || "-"}
                                        <span class="mx-2">|</span>
                                        <i class="bi bi-geo-alt-fill me-1"></i>${report.location || "-"}
                                    </div>
                                </div>
                                <span class="badge text-bg-light border align-self-start">${statusMeta.label}</span>
                            </div>

                            <p class="text-muted mb-3">${report.description || "Tidak ada deskripsi."}</p>

                            <div class="d-flex justify-content-between small mb-2">
                                <span>Progress Penanganan</span>
                                <span>${statusMeta.progress}%</span>
                            </div>
                            <div class="progress" style="height: 10px;">
                                <div
                                    class="progress-bar ${statusMeta.colorClass}"
                                    role="progressbar"
                                    style="width: ${statusMeta.progress}%"
                                    aria-valuenow="${statusMeta.progress}"
                                    aria-valuemin="0"
                                    aria-valuemax="100"
                                ></div>
                            </div>

                            <div class="d-flex justify-content-between align-items-center mt-3 small text-muted">
                                <span>Pelapor: ${report.reporter || "Warga Anonim"}</span>
                                <span>Diperbarui: ${formatDateTime(report.updated_at)}</span>
                            </div>
                            ${actionButtons ? `<div class="d-flex flex-wrap gap-2 mt-3">${actionButtons}</div>` : ""}
                        </div>
                    </div>
                </div>
            `;
        })
        .join("");

    bindReportActionButtons();
    bindStatusUpdateButtons();
}

function renderPagination() {
    const paginationContainer = document.getElementById("paginationContainer");
    if (!paginationContainer) {
        return;
    }

    if (totalPages <= 1) {
        paginationContainer.innerHTML = "";
        return;
    }

    let paginationHtml = `
        <nav aria-label="Pagination laporan">
            <ul class="pagination justify-content-center mb-0">
    `;

    for (let page = 1; page <= totalPages; page += 1) {
        paginationHtml += `
            <li class="page-item ${page === currentPage ? "active" : ""}">
                <button class="page-link" type="button" data-page="${page}">
                    ${page}
                </button>
            </li>
        `;
    }

    paginationHtml += `
            </ul>
        </nav>
    `;

    paginationContainer.innerHTML = paginationHtml;

    const pageButtons = paginationContainer.querySelectorAll("[data-page]");
    pageButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const selectedPage = Number(button.dataset.page);
            if (selectedPage !== currentPage) {
                loadDashboardData(currentTab, selectedPage);
            }
        });
    });
}

async function loadDashboardData(tab = currentTab, page = currentPage) {
    currentTab = tab;
    currentPage = page;
    updateActiveTabButtons();

    // Menembak API Backend dengan parameter tab dan halaman
    const response = await requestAPI(`/api/reports/?tab=${tab}&page=${page}`, "GET");

    if (response && response.status === 200) {
        // ==========================================================
        // INSTRUKSI 1: Ekstraksi Data Paginasi (Destructuring)
        // 1. Simpan array data laporan dari 'response.data.results' ke variabel global 'allReports'. Jika kosong/undefined, set sebagai array kosong [].
        // 2. Ambil total jumlah data keseluruhan dari 'response.data.count' (set default 0).
        // 3. Hitung variabel 'totalPages' dengan membagi total data dengan 10, lalu bulatkan ke atas menggunakan fungsi Math.ceil().
        // ==========================================================
        const { results = [], count = 0 } = response.data || {};
        allReports = results;
        totalPages = Math.ceil(count / REPORTS_PER_PAGE);

        // ==========================================================
        // INSTRUKSI 2: Pemicu Perbaruan UI (Sinkronisasi Antarmuka)
        // Panggil 2 fungsi ini secara berurutan agar layar langsung diperbarui:
        // 1. renderList() -> menggambar susunan kartu laporan
        // 2. renderPagination() -> menggambar ulang tombol halaman di bawah
        // ==========================================================
        renderList();
        renderPagination();
        loadSummaryStats(currentTab);
    } else {
        // Penanganan jika API gagal ditarik atau server mati
        const listContainer = document.getElementById("listContainer");
        const isUnauthorized = response && (response.status === 401 || response.status === 403);
        if (listContainer) {
            listContainer.innerHTML = `
                <div class="col-12 text-center text-muted p-5">
                    <i class="bi ${isUnauthorized ? "bi-lock-fill" : "bi-exclamation-triangle"} fs-1"></i>
                    <p class="mt-3 mb-0">
                        ${isUnauthorized ? "Silakan login di SPA terlebih dahulu agar data laporan bisa dimuat." : "Gagal memuat data laporan."}
                    </p>
                </div>
            `;
        }

        const paginationContainer = document.getElementById("paginationContainer");
        if (paginationContainer) {
            paginationContainer.innerHTML = "";
        }
    }
}

async function loadSummaryStats(tab = currentTab) {
    const response = await requestAPI(`/api/reports/?tab=${tab}&page_size=100`, "GET");
    if (!response || response.status !== 200) {
        ["draftCount", "reportedCount", "verifiedCount", "inProgressCount", "resolvedCount"]
            .forEach((elementId) => {
                const countElement = document.getElementById(elementId);
                if (countElement) {
                    countElement.textContent = "-";
                }
            });
        return;
    }

    const reports = response.data?.results || [];
    const statusCountElements = {
        DRAFT: "draftCount",
        REPORTED: "reportedCount",
        VERIFIED: "verifiedCount",
        IN_PROGRESS: "inProgressCount",
        RESOLVED: "resolvedCount",
    };

    Object.entries(statusCountElements).forEach(([status, elementId]) => {
        const countElement = document.getElementById(elementId);
        if (countElement) {
            countElement.textContent = reports.filter(
                (report) => report.status === status
            ).length;
        }
    });
}

function bindReportActionButtons() {
    const editButtons = document.querySelectorAll("[data-edit-report-id]");
    editButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const reportId = button.dataset.editReportId;
            if (reportId) {
                editReport(reportId);
            }
        });
    });

    const deleteButtons = document.querySelectorAll("[data-delete-report-id]");
    deleteButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const reportId = button.dataset.deleteReportId;
            if (reportId) {
                deleteReport(reportId);
            }
        });
    });
}

function bindStatusUpdateButtons() {
    const statusButtons = document.querySelectorAll("[data-update-status-id]");
    statusButtons.forEach((button) => {
        button.addEventListener("click", async () => {
            const reportId = button.dataset.updateStatusId;
            const statusSelect = document.getElementById(`reportStatus-${reportId}`);
            if (!reportId || !statusSelect) {
                return;
            }

            button.disabled = true;
            const originalText = button.textContent;
            button.textContent = "Menyimpan...";

            const response = await requestAPI(
                `/api/reports/${reportId}/`,
                "PATCH",
                { status: statusSelect.value }
            );

            if (response && response.status === 200) {
                await loadDashboardData(currentTab, currentPage);
                return;
            }

            button.disabled = false;
            button.textContent = originalText;
            alert(getApiErrorMessage(response, "Gagal memperbarui status laporan."));
        });
    });
}

function getReportModalInstance() {
    const modalElement = document.getElementById("reportModal");
    if (!modalElement) {
        return null;
    }

    return bootstrap.Modal.getOrCreateInstance(modalElement);
}

function fillReportForm(report = {}) {
    const titleInput = document.getElementById("reportTitle");
    const categoryInput = document.getElementById("reportCategory");
    const locationInput = document.getElementById("reportLocation");
    const descriptionInput = document.getElementById("reportDescription");

    if (titleInput) {
        titleInput.value = report.title || "";
    }
    if (categoryInput) {
        categoryInput.value = report.category || "";
    }
    if (locationInput) {
        locationInput.value = report.location || "";
    }
    if (descriptionInput) {
        descriptionInput.value = report.description || "";
    }
}

function resetReportFormState() {
    const reportForm = document.getElementById("reportForm");
    if (reportForm) {
        reportForm.reset();
    }

    editingReportId = null;
    editingReportStatus = null;

    const modalTitle = document.getElementById("reportModalLabel");
    if (modalTitle) {
        modalTitle.innerHTML = `<i class="bi bi-pencil-square me-2"></i>Buat Laporan Baru`;
    }

    const btnDraft = document.getElementById("btnDraft");
    const btnSubmit = document.getElementById("btnSubmit");
    if (btnDraft) {
        btnDraft.classList.remove("d-none");
    }
    if (btnSubmit) {
        btnSubmit.innerHTML = `Ajukan <i class="bi bi-send-fill ms-1"></i>`;
    }
}

async function editReport(id) {
    const response = await requestAPI(`/api/reports/${id}/`, "GET");
    if (!response || response.status !== 200) {
        alert("Gagal mengambil data laporan.");
        return;
    }

    editingReportId = id;
    editingReportStatus = response.data?.status || null;
    fillReportForm(response.data || {});

    const modalTitle = document.getElementById("reportModalLabel");
    if (modalTitle) {
        modalTitle.innerHTML = `<i class="bi bi-pencil-square me-2"></i>Edit Laporan`;
    }

    const btnDraft = document.getElementById("btnDraft");
    const btnSubmit = document.getElementById("btnSubmit");
    if (btnDraft && editingReportStatus === "DRAFT") {
        btnDraft.classList.remove("d-none");
        btnDraft.textContent = "Simpan Draft";
    } else if (btnDraft) {
        btnDraft.classList.add("d-none");
    }
    if (btnSubmit) {
        btnSubmit.textContent = editingReportStatus === "DRAFT"
            ? "Ajukan Laporan"
            : "Simpan Perubahan";
    }

    const modalInstance = getReportModalInstance();
    if (modalInstance) {
        modalInstance.show();
    }
}

async function deleteReport(id) {
    if (!window.confirm("Hapus laporan ini secara permanen?")) {
        return;
    }

    const response = await requestAPI(`/api/reports/${id}/`, "DELETE");
    if (response && response.status === 204) {
        await loadDashboardData(currentTab, currentPage);
        return;
    }

    alert(getApiErrorMessage(response, "Gagal menghapus laporan."));
}

function setupReportForm() {
    const reportForm = document.getElementById("reportForm");
    const btnDraft = document.getElementById("btnDraft");
    const btnSubmit = document.getElementById("btnSubmit");
    const modalElement = document.getElementById("reportModal");

    if (reportForm && !reportForm.dataset.bound) {
        reportForm.dataset.bound = "true";
        reportForm.addEventListener("submit", (event) => {
            event.preventDefault();
            handleReportSubmit("REPORTED");
        });
    }

    if (btnDraft && !btnDraft.dataset.bound) {
        btnDraft.dataset.bound = "true";
        btnDraft.addEventListener("click", () => {
            handleReportSubmit("DRAFT");
        });
    }

    if (btnSubmit && !btnSubmit.dataset.bound) {
        btnSubmit.dataset.bound = "true";
        btnSubmit.addEventListener("click", () => {
            handleReportSubmit("REPORTED");
        });
    }

    if (modalElement && !modalElement.dataset.bound) {
        modalElement.dataset.bound = "true";
        modalElement.addEventListener("hidden.bs.modal", () => {
            resetReportFormState();
        });
    }
}

async function handleReportSubmit(statusValue) {
    const reportForm = document.getElementById("reportForm");
    if (!reportForm) {
        return;
    }

    const reportFields = {
        title: document.getElementById("reportTitle")?.value.trim() || "",
        category: document.getElementById("reportCategory")?.value.trim() || "",
        location: document.getElementById("reportLocation")?.value.trim() || "",
        description: document.getElementById("reportDescription")?.value.trim() || "",
    };

    if (!reportFields.title || !reportFields.category || !reportFields.location || !reportFields.description) {
        alert("Semua field laporan wajib diisi sebelum disimpan.");
        return;
    }

    const isEditing = editingReportId !== null;
    const endpoint = isEditing ? `/api/reports/${editingReportId}/` : "/api/reports/";
    const method = isEditing ? "PATCH" : "POST";
    const isSubmittingDraft = (
        isEditing
        && editingReportStatus === "DRAFT"
        && statusValue === "REPORTED"
    );
    const payload = {
        ...reportFields,
        ...((!isEditing || isSubmittingDraft) ? { status: statusValue } : {}),
    };

    const response = await requestAPI(endpoint, method, payload);
    console.log("Report submit response:", response);

    if (response && (response.status === 201 || response.status === 200)) {
        const modalInstance = getReportModalInstance();
        if (modalInstance) {
            modalInstance.hide();
        }

        reportForm.reset();
        editingReportId = null;
        loadDashboardData();
        return;
    }

    alert(getApiErrorMessage(response, "Gagal menyimpan laporan."));
}
