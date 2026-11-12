
document.addEventListener("DOMContentLoaded", () => {
    const root = document.documentElement;
    const themeSelect = document.getElementById("themeSelect");
    const menuToggle = document.getElementById("menuToggle");
    const sidebar = document.getElementById("sidebar");

    // Restore previously selected theme
    const savedTheme = localStorage.getItem("blogify-theme") || "neon";
    root.setAttribute("data-theme", savedTheme);

    if (themeSelect) {
        themeSelect.value = savedTheme;

        themeSelect.addEventListener("change", () => {
            const selectedTheme = themeSelect.value;
            root.setAttribute("data-theme", selectedTheme);
            localStorage.setItem("blogify-theme", selectedTheme);
        });
    }

    // Mobile sidebar
    if (menuToggle && sidebar) {
        menuToggle.addEventListener("click", () => {
            sidebar.classList.toggle("open");
        });

        document.addEventListener("click", (event) => {
            if (
                window.innerWidth <= 850 &&
                !sidebar.contains(event.target) &&
                !menuToggle.contains(event.target)
            ) {
                sidebar.classList.remove("open");
            }
        });
    }

    // Confirm destructive actions
    document.querySelectorAll("form[onsubmit]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            const message = form.getAttribute("onsubmit");

            if (message && !confirm("Are you sure you want to continue?")) {
                event.preventDefault();
            }
        });
    });
});
