(function () {
  const script = document.currentScript;
  const modal = document.getElementById("docs-search-modal");
  const input = document.querySelector("[data-docs-search-input]");
  const results = document.querySelector("[data-docs-search-results]");
  const status = document.getElementById("docs-search-title");
  const openButtons = Array.from(document.querySelectorAll("[data-docs-search-open]"));
  const closeButtons = Array.from(document.querySelectorAll("[data-docs-search-close]"));
  const shortcutNodes = Array.from(document.querySelectorAll("[data-docs-search-shortcut]"));

  if (!script || !modal || !input || !results || !status || openButtons.length === 0) {
    return;
  }

  const docsRootUrl = new URL("../", script.src);
  const searchIndexUrl = new URL(script.dataset.searchIndex || "search-index.json", window.location.href);
  const isMac = /(Mac|iPhone|iPad|iPod)/i.test(navigator.platform || navigator.userAgent);
  const shortcutLabel = isMac ? "⌘K" : "Ctrl K";

  shortcutNodes.forEach((node) => {
    node.textContent = shortcutLabel;
  });

  let searchEntries = null;
  let activeIndex = -1;
  let activeResultNodes = [];
  let lastFocusedElement = null;

  function escapeHtml(value) {
    return value
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function escapeRegExp(value) {
    return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function normalizeText(value) {
    return value.toLowerCase().replace(/\s+/g, " ").trim();
  }

  async function ensureSearchEntries() {
    if (searchEntries) {
      return searchEntries;
    }
    status.textContent = "Loading search index…";
    const response = await fetch(searchIndexUrl);
    if (!response.ok) {
      throw new Error("Unable to load the docs search index.");
    }
    searchEntries = await response.json();
    return searchEntries;
  }

  function renderEmptyState(message) {
    activeIndex = -1;
    activeResultNodes = [];
    results.innerHTML = '<div class="docs-search-empty">' + escapeHtml(message) + "</div>";
  }

  function matchIndex(text, term) {
    return text.toLowerCase().indexOf(term.toLowerCase());
  }

  function buildSnippet(text, terms) {
    const matchPosition = terms
      .map((term) => matchIndex(text, term))
      .find((index) => index >= 0);
    const center = matchPosition >= 0 ? matchPosition : 0;
    const start = Math.max(0, center - 70);
    const end = Math.min(text.length, center + 140);
    let snippet = text.slice(start, end).trim();
    if (start > 0) {
      snippet = "…" + snippet;
    }
    if (end < text.length) {
      snippet += "…";
    }

    let snippetHtml = escapeHtml(snippet);
    terms
      .slice()
      .sort((left, right) => right.length - left.length)
      .forEach((term) => {
        if (!term) {
          return;
        }
        const expression = new RegExp("(" + escapeRegExp(term) + ")", "gi");
        snippetHtml = snippetHtml.replace(expression, "<mark>$1</mark>");
      });
    return snippetHtml;
  }

  function scoreEntry(entry, terms) {
    const title = normalizeText(entry.title || "");
    const section = normalizeText(entry.section || "");
    const text = normalizeText(entry.text || "");
    const searchable = [title, section, text].join(" ");
    let score = 0;
    let matchedTerms = 0;

    terms.forEach((term) => {
      if (!searchable.includes(term)) {
        return;
      }
      matchedTerms += 1;
      score += 10;
      if (title.includes(term)) {
        score += 80;
      }
      if (section.includes(term)) {
        score += 45;
      }
      if (text.includes(term)) {
        score += 20;
      }
    });

    if (matchedTerms === 0) {
      return null;
    }

    score += matchedTerms * 100;
    return score;
  }

  function setActiveIndex(index) {
    if (activeResultNodes.length === 0) {
      activeIndex = -1;
      return;
    }
    activeIndex = ((index % activeResultNodes.length) + activeResultNodes.length) % activeResultNodes.length;
    activeResultNodes.forEach((node, nodeIndex) => {
      node.classList.toggle("is-active", nodeIndex === activeIndex);
      node.setAttribute("aria-selected", nodeIndex === activeIndex ? "true" : "false");
    });
    activeResultNodes[activeIndex].scrollIntoView({ block: "nearest" });
  }

  function renderMatches(matches, terms) {
    if (matches.length === 0) {
      status.textContent = "No matches";
      renderEmptyState("No documentation matched that search yet.");
      return;
    }

    status.textContent = matches.length === 1 ? "1 match" : matches.length + " matches";
    results.innerHTML =
      '<div class="docs-search-list">' +
      matches
        .map((match) => {
          const meta = match.section ? [match.title, match.section].join(" · ") : "";
          const href = new URL(match.href || "./", docsRootUrl);
          return (
            '<a class="docs-search-result" href="' +
            escapeHtml(href.href) +
            '" role="option">' +
            '<div class="docs-search-result-title">' +
            escapeHtml(match.section || match.title) +
            "</div>" +
            (meta
              ? '<div class="docs-search-result-meta">' + escapeHtml(meta) + "</div>"
              : "") +
            '<div class="docs-search-result-snippet">' +
            buildSnippet(match.text || "", terms) +
            "</div>" +
            "</a>"
          );
        })
        .join("") +
      "</div>";

    activeResultNodes = Array.from(results.querySelectorAll(".docs-search-result"));
    activeResultNodes.forEach((node, index) => {
      node.addEventListener("mouseenter", () => setActiveIndex(index));
      node.addEventListener("click", () => closeModal());
    });
    setActiveIndex(0);
  }

  async function updateResults() {
    const query = input.value.trim();
    if (!query) {
      status.textContent = "Search docs by title, section, or prose.";
      renderEmptyState("Start typing to search every docs page in real time.");
      return;
    }

    try {
      const entries = await ensureSearchEntries();
      const terms = normalizeText(query).split(" ").filter(Boolean);
      const matches = entries
        .map((entry) => {
          const score = scoreEntry(entry, terms);
          if (score === null) {
            return null;
          }
          return { ...entry, score };
        })
        .filter(Boolean)
        .sort((left, right) => right.score - left.score)
        .slice(0, 8);
      renderMatches(matches, terms);
    } catch (error) {
      status.textContent = "Search unavailable";
      renderEmptyState(error instanceof Error ? error.message : "Search is unavailable.");
    }
  }

  function openModal() {
    lastFocusedElement = document.activeElement;
    modal.hidden = false;
    document.body.classList.add("docs-search-open");
    input.focus();
    input.select();
    void ensureSearchEntries().catch(() => {});
    void updateResults();
  }

  function closeModal() {
    modal.hidden = true;
    document.body.classList.remove("docs-search-open");
    activeIndex = -1;
    activeResultNodes = [];
    if (lastFocusedElement instanceof HTMLElement) {
      lastFocusedElement.focus();
    }
  }

  openButtons.forEach((button) => {
    button.addEventListener("click", openModal);
  });

  closeButtons.forEach((button) => {
    button.addEventListener("click", closeModal);
  });

  input.addEventListener("input", () => {
    void updateResults();
  });

  document.addEventListener("keydown", (event) => {
    const isShortcut = event.key.toLowerCase() === "k" && (event.metaKey || event.ctrlKey);
    if (isShortcut) {
      event.preventDefault();
      if (modal.hidden) {
        openModal();
      } else {
        closeModal();
      }
      return;
    }

    if (modal.hidden) {
      return;
    }

    if (event.key === "Escape") {
      event.preventDefault();
      closeModal();
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActiveIndex(activeIndex + 1);
      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      setActiveIndex(activeIndex - 1);
      return;
    }

    if (event.key === "Enter" && activeIndex >= 0 && activeResultNodes[activeIndex]) {
      event.preventDefault();
      activeResultNodes[activeIndex].click();
    }
  });

  renderEmptyState("Start typing to search every docs page in real time.");
})();
