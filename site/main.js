document.addEventListener("DOMContentLoaded", () => {
    const yearEl = document.getElementById("year");
    if (yearEl) {
        yearEl.textContent = new Date().getFullYear();
    }

    const nav = document.getElementById("primary-nav");
    const menuToggle = document.querySelector(".menu-toggle");
    const navLinks = Array.from(document.querySelectorAll(".nav-list a"));
    const sections = navLinks
        .map((link) => document.querySelector(link.getAttribute("href")))
        .filter(Boolean);

    if (menuToggle && nav) {
        menuToggle.addEventListener("click", () => {
            const expanded = menuToggle.getAttribute("aria-expanded") === "true";
            menuToggle.setAttribute("aria-expanded", String(!expanded));
            nav.classList.toggle("open", !expanded);
            menuToggle.classList.toggle("is-active", !expanded);
        });

        navLinks.forEach((link) =>
            link.addEventListener("click", () => {
                if (menuToggle.getAttribute("aria-expanded") === "true") {
                    menuToggle.setAttribute("aria-expanded", "false");
                    nav.classList.remove("open");
                    menuToggle.classList.remove("is-active");
                }
            })
        );
    }

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                const id = entry.target.getAttribute("id");
                const link = navLinks.find((a) => a.getAttribute("href") === `#${id}`);
                if (link) {
                    link.classList.toggle("is-active", entry.isIntersecting);
                }
            });
        },
        {
            rootMargin: "-60% 0px -20% 0px",
            threshold: [0, 1]
        }
    );

    sections.forEach((section) => observer.observe(section));
});
