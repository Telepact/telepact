(() => {
  const SEARCH_INDEX_FILENAME = "search-index.json";
  const MAX_SEARCH_RESULTS = 12;
  const SNIPPET_MAX_LENGTH = 180;
  const SNIPPET_CONTEXT_PADDING = 56;
  const DOCS_PRIORITY_CONCEPT = 0;
  const DOCS_PRIORITY_DEFAULT = 1;
  const DOCS_PRIORITY_EXAMPLE = 2;
  const script = document.currentScript;
  const modal = document.querySelector("[data-docs-search-modal]");
  const openButtons = Array.from(document.querySelectorAll("[data-docs-search-open]"));
  const closeButtons = Array.from(document.querySelectorAll("[data-docs-search-close]"));
  const input = document.querySelector("[data-docs-search-input]");
  const results = document.querySelector("[data-docs-search-results]");
  const status = document.querySelector("[data-docs-search-status]");
  const shortcut = document.querySelector("[data-docs-search-shortcut]");

  if (!script || !modal || !input || !results || !status) {
    return;
  }

  const isApplePlatform = /Mac|iPhone|iPad|iPod/.test(navigator.platform);
  const docsBaseUrl = new URL("../", script.src);
  const indexUrl = script.dataset.docsSearchIndex
    ? new URL(script.dataset.docsSearchIndex, document.baseURI)
    : new URL(`assets/${SEARCH_INDEX_FILENAME}`, docsBaseUrl);
  const shortcutText = isApplePlatform ? "⌘K" : "Ctrl K";
  const currentDocumentPath = normalizeDocsPath(window.location.href);
  let searchIndexPromise;
  let searchEntries = [];
  let isOpen = false;

  if (shortcut) {
    shortcut.textContent = shortcutText;
  }
  for (const button of openButtons) {
    const key = button.querySelector("[data-docs-search-shortcut]");
    if (key) {
      key.textContent = shortcutText;
    }
  }

  function ensureSearchIndex() {
    if (!searchIndexPromise) {
      searchIndexPromise = fetch(indexUrl.toString())
        .then((response) => {
          if (!response.ok) {
            throw new Error(`Search index request failed: ${response.status}`);
          }
          return response.json();
        })
        .then((entries) => {
          searchEntries = Array.isArray(entries) ? entries : [];
          return searchEntries;
        });
    }
    return searchIndexPromise;
  }

  function escapeHtml(value) {
    return value
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function escapeRegex(value) {
    return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function tokenize(value) {
    return value
      .toLowerCase()
      .trim()
      .split(/\s+/)
      .filter(Boolean);
  }

  function normalizeDocsPath(value) {
    const url = new URL(value || "./", docsBaseUrl);
    let pathname = url.pathname;
    if (pathname.startsWith(docsBaseUrl.pathname)) {
      pathname = pathname.slice(docsBaseUrl.pathname.length);
    }
    pathname = pathname.replace(/^\/+/, "").replace(/index\.html$/, "");
    if (!pathname) {
      return "./";
    }
    return pathname.endsWith("/") ? pathname : `${pathname}/`;
  }

  function documentPriority(path) {
    const normalizedPath = normalizeDocsPath(path);
    if (normalizedPath === "concepts/" || normalizedPath.startsWith("concepts/")) {
      return DOCS_PRIORITY_CONCEPT;
    }
    if (normalizedPath === "examples/" || normalizedPath.startsWith("examples/")) {
      return DOCS_PRIORITY_EXAMPLE;
    }
    return DOCS_PRIORITY_DEFAULT;
  }

  function renderHighlight(value, terms) {
    const escaped = escapeHtml(value);
    if (!terms.length) {
      return escaped;
    }
    const pattern = new RegExp(`(${terms.map(escapeRegex).join("|")})`, "ig");
    return escaped.replace(pattern, "<mark>$1</mark>");
  }

  function snippetFor(entry, terms) {
    const content = (entry.content || "").trim();
    if (!content) {
      return "";
    }
    if (!terms.length) {
      return content.slice(0, SNIPPET_MAX_LENGTH).trim();
    }
    const lowered = content.toLowerCase();
    let start = 0;
    for (const term of terms) {
      const matchIndex = lowered.indexOf(term);
      if (matchIndex >= 0) {
        start = Math.max(0, matchIndex - SNIPPET_CONTEXT_PADDING);
        break;
      }
    }
    const end = Math.min(content.length, start + SNIPPET_MAX_LENGTH);
    const prefix = start > 0 ? "…" : "";
    const suffix = end < content.length ? "…" : "";
    return `${prefix}${content.slice(start, end).trim()}${suffix}`;
  }

  function scoreEntry(entry, query, terms) {
    const title = (entry.title || "").toLowerCase();
    const section = (entry.section || "").toLowerCase();
    const content = (entry.content || "").toLowerCase();
    const text = (entry.searchText || `${title} ${section} ${content}`).toLowerCase();

    let score = 0;
    let matchedTerms = 0;
    for (const term of terms) {
      let matched = false;
      if (title.includes(term)) {
        score += 24;
        matched = true;
      }
      if (section.includes(term)) {
        score += 12;
        matched = true;
      }
      if (content.includes(term)) {
        score += 6;
        matched = true;
      }
      if (text.includes(term)) {
        score += 2;
        matched = true;
      }
      if (matched) {
        matchedTerms += 1;
      }
    }

    if (!matchedTerms) {
      return -1;
    }
    if (query && title.includes(query)) {
      score += 40;
    }
    if (query && section.includes(query)) {
      score += 18;
    }
    if (terms.length > 1 && matchedTerms === terms.length) {
      score += 16;
    }
    if (text.startsWith(query)) {
      score += 8;
    }
    return score;
  }

  function search(query) {
    const normalizedQuery = query.toLowerCase().trim();
    const terms = tokenize(normalizedQuery);
    if (!terms.length) {
      return [];
    }
    return searchEntries
      .map((entry) => ({ entry, score: scoreEntry(entry, normalizedQuery, terms) }))
      .filter((item) => item.score >= 0 && normalizeDocsPath(item.entry.path) !== currentDocumentPath)
      .sort((left, right) => {
        const priorityDiff = documentPriority(left.entry.path) - documentPriority(right.entry.path);
        if (priorityDiff !== 0) {
          return priorityDiff;
        }
        if (right.score !== left.score) {
          return right.score - left.score;
        }
        return (left.entry.path || "").localeCompare(right.entry.path || "");
      })
      .slice(0, MAX_SEARCH_RESULTS)
      .map((item) => item.entry);
  }

  function renderEmpty(message) {
    status.hidden = false;
    status.textContent = message;
    results.hidden = true;
    results.innerHTML = "";
  }

  function renderResults(matches, terms) {
    if (!matches.length) {
      renderEmpty("No matching docs yet. Try a different keyword.");
      return;
    }
    status.hidden = false;
    status.textContent = `${matches.length} result${matches.length === 1 ? "" : "s"}`;
    results.hidden = false;
    results.innerHTML = matches
      .map((entry) => {
        const href = entry.path ? new URL(entry.path, docsBaseUrl).toString() : docsBaseUrl.toString();
        const title = renderHighlight(entry.title || "Untitled", terms);
        const section = entry.section ? renderHighlight(entry.section, terms) : "Documentation";
        const snippet = renderHighlight(snippetFor(entry, terms), terms);
        return [
          `<a class="docs-search-result" href="${href}">`,
          '<div class="docs-search-result-meta">',
          `<span class="docs-search-result-title">${title}</span>`,
          `<span class="docs-search-result-section">${section}</span>`,
          "</div>",
          `<p class="docs-search-result-snippet">${snippet}</p>`,
          "</a>",
        ].join("");
      })
      .join("");
  }

  function updateResults() {
    const query = input.value;
    const terms = tokenize(query);
    if (!terms.length) {
      renderEmpty(`Type to search the docs. Press ${shortcutText} from anywhere on the page.`);
      return;
    }
    renderResults(search(query), terms);
  }

  function openModal() {
    if (isOpen) {
      input.focus();
      input.select();
      return;
    }
    isOpen = true;
    modal.hidden = false;
    document.body.classList.add("docs-search-open");
    renderEmpty("Loading search index…");
    ensureSearchIndex()
      .then(() => {
        if (!isOpen) {
          return;
        }
        updateResults();
      })
      .catch(() => {
        renderEmpty("Search is unavailable right now. Reload the page and try again.");
      });
    window.requestAnimationFrame(() => {
      input.focus();
      input.select();
    });
  }

  function closeModal() {
    if (!isOpen) {
      return;
    }
    isOpen = false;
    modal.hidden = true;
    document.body.classList.remove("docs-search-open");
  }

  for (const button of openButtons) {
    button.addEventListener("click", openModal);
  }
  for (const button of closeButtons) {
    button.addEventListener("click", closeModal);
  }

  modal.addEventListener("click", (event) => {
    if (event.target === modal) {
      closeModal();
    }
  });

  input.addEventListener("input", updateResults);
  document.addEventListener("keydown", (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      openModal();
      return;
    }
    if (event.key === "Escape" && isOpen) {
      closeModal();
    }
  });

  ensureSearchIndex().catch(() => undefined);
})();
