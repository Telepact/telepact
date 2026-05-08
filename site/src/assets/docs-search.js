(() => {
  const script = document.currentScript;
  const searchIndexUrl = script?.dataset.searchIndex;
  const modal = document.getElementById("docs-search-modal");
  if (!searchIndexUrl || !modal) {
    return;
  }

  const input = modal.querySelector("[data-docs-search-input]");
  const statusNode = modal.querySelector("[data-docs-search-status]");
  const resultsNode = modal.querySelector("[data-docs-search-results]");
  const openButtons = document.querySelectorAll("[data-docs-search-open]");
  const closeButtons = modal.querySelectorAll("[data-docs-search-close]");
  const shortcutNodes = document.querySelectorAll("[data-docs-search-shortcut]");
  const platform = navigator.userAgentData?.platform || navigator.platform || navigator.userAgent || "";
  const isMac = /(Mac|iPhone|iPad)/i.test(platform);
  const MAX_SNIPPET_LENGTH = 160;
  const TRUNCATED_SNIPPET_LENGTH = MAX_SNIPPET_LENGTH - 3;
  const SNIPPET_CONTEXT_BEFORE = 64;
  const SNIPPET_CONTEXT_AFTER = 96;
  const MIN_HIGHLIGHT_TOKEN_LENGTH = 2;
  const SCORE_TITLE_PREFIX = 140;
  const SCORE_TITLE_MATCH = 110;
  const SCORE_PAGE_TITLE_MATCH = 70;
  const SCORE_TEXT_MATCH = 28;
  const SCORE_PAGE_RESULT = 8;
  const SCORE_TEXT_INDEX_CAP = 400;
  const SCORE_TEXT_INDEX_DIVISOR = 100;

  shortcutNodes.forEach((node) => {
    node.textContent = isMac ? "⌘K" : "Ctrl K";
  });

  let indexEntries = null;
  let loadPromise = null;
  let activeIndex = -1;

  const escapeHtml = (value) =>
    value
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");

  const escapeRegExp = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const normalize = (value) => value.toLowerCase();
  const queryTokens = (value) => normalize(value).trim().split(/\s+/).filter(Boolean);

  const setStatus = (message) => {
    statusNode.textContent = message;
    statusNode.hidden = false;
  };

  const hideStatus = () => {
    statusNode.hidden = true;
  };

  const firstMatchIndex = (text, tokens) => {
    const haystack = normalize(text);
    let best = -1;
    for (const token of tokens) {
      const index = haystack.indexOf(token);
      if (index !== -1 && (best === -1 || index < best)) {
        best = index;
      }
    }
    return best;
  };

  const buildSnippet = (text, query) => {
    const clean = text.replace(/\s+/g, " ").trim();
    if (!clean) {
      return "";
    }
    const tokens = queryTokens(query);
    if (!tokens.length) {
      return clean.length > MAX_SNIPPET_LENGTH ? `${clean.slice(0, TRUNCATED_SNIPPET_LENGTH).trim()}…` : clean;
    }
    const matchIndex = firstMatchIndex(clean, tokens);
    if (matchIndex === -1) {
      return clean.length > MAX_SNIPPET_LENGTH ? `${clean.slice(0, TRUNCATED_SNIPPET_LENGTH).trim()}…` : clean;
    }
    let start = Math.max(0, matchIndex - SNIPPET_CONTEXT_BEFORE);
    let end = Math.min(clean.length, matchIndex + SNIPPET_CONTEXT_AFTER);
    if (start > 0) {
      const nextSpace = clean.indexOf(" ", start);
      if (nextSpace !== -1 && nextSpace < matchIndex) {
        start = nextSpace + 1;
      }
    }
    if (end < clean.length) {
      const previousSpace = clean.lastIndexOf(" ", end);
      if (previousSpace > matchIndex) {
        end = previousSpace;
      }
    }
    return `${start > 0 ? "…" : ""}${clean.slice(start, end).trim()}${end < clean.length ? "…" : ""}`;
  };

  const highlight = (text, query) => {
    let rendered = escapeHtml(text);
    const tokens = [...new Set(queryTokens(query))].sort((left, right) => right.length - left.length);
    for (const token of tokens) {
      if (token.length < MIN_HIGHLIGHT_TOKEN_LENGTH) {
        continue;
      }
      rendered = rendered.replace(new RegExp(`(${escapeRegExp(token)})`, "ig"), "<mark>$1</mark>");
    }
    return rendered;
  };

  const scoreEntry = (entry, query) => {
    const tokens = queryTokens(query);
    if (!tokens.length) {
      return null;
    }
    const title = normalize(entry.title);
    const pageTitle = normalize(entry.pageTitle);
    const text = normalize(entry.text);
    let score = 0;
    let bestTextIndex = Number.POSITIVE_INFINITY;

    for (const token of tokens) {
      if (title.startsWith(token)) {
        score += SCORE_TITLE_PREFIX;
      } else if (title.includes(token)) {
        score += SCORE_TITLE_MATCH;
      } else if (pageTitle.includes(token)) {
        score += SCORE_PAGE_TITLE_MATCH;
      } else if (text.includes(token)) {
        score += SCORE_TEXT_MATCH;
      } else {
        return null;
      }

      const textIndex = text.indexOf(token);
      if (textIndex !== -1) {
        bestTextIndex = Math.min(bestTextIndex, textIndex);
      }
    }

    if (bestTextIndex < Number.POSITIVE_INFINITY) {
      score -= Math.min(bestTextIndex, SCORE_TEXT_INDEX_CAP) / SCORE_TEXT_INDEX_DIVISOR;
    }
    if (entry.title === entry.pageTitle) {
      score += SCORE_PAGE_RESULT;
    }
    return score;
  };

  const setActiveResult = (index) => {
    const nodes = [...resultsNode.querySelectorAll(".docs-search-result")];
    activeIndex = nodes.length ? ((index % nodes.length) + nodes.length) % nodes.length : -1;
    nodes.forEach((node, nodeIndex) => {
      const selected = nodeIndex === activeIndex;
      node.classList.toggle("active", selected);
      node.setAttribute("aria-selected", selected ? "true" : "false");
      if (selected) {
        node.scrollIntoView({ block: "nearest" });
      }
    });
  };

  const renderResults = (query) => {
    const trimmedQuery = query.trim();
    activeIndex = -1;
    resultsNode.innerHTML = "";

    if (!trimmedQuery) {
      setStatus("Type to search the documentation.");
      return;
    }

    const matches = indexEntries
      .map((entry) => ({ entry, score: scoreEntry(entry, trimmedQuery) }))
      .filter((match) => match.score !== null)
      .sort((left, right) => right.score - left.score || left.entry.url.localeCompare(right.entry.url))
      .slice(0, 12);

    if (!matches.length) {
      setStatus(`No results for “${trimmedQuery}”.`);
      return;
    }

    hideStatus();
    for (const [index, match] of matches.entries()) {
      const pageLabel = match.entry.title === match.entry.pageTitle ? "Page" : match.entry.pageTitle;
      const result = document.createElement("a");
      result.href = match.entry.url;
      result.className = "docs-search-result";
      result.dataset.index = String(index);
      result.setAttribute("role", "option");
      result.setAttribute("aria-selected", "false");
      result.innerHTML = `
        <div class="docs-search-result-meta">${escapeHtml(pageLabel)}</div>
        <div class="docs-search-result-title">${highlight(match.entry.title, trimmedQuery)}</div>
        <p class="docs-search-result-snippet">${highlight(buildSnippet(match.entry.text, trimmedQuery), trimmedQuery)}</p>
      `;
      resultsNode.append(result);
    }
  };

  const ensureIndex = async () => {
    if (indexEntries !== null) {
      return;
    }
    if (loadPromise === null) {
      loadPromise = fetch(searchIndexUrl)
        .then((response) => {
          if (!response.ok) {
            throw new Error(`Failed to load ${searchIndexUrl}: ${response.status}`);
          }
          return response.json();
        })
        .then((payload) => {
          indexEntries = Array.isArray(payload) ? payload : [];
        });
    }
    await loadPromise;
  };

  const closeModal = () => {
    modal.hidden = true;
    document.body.classList.remove("docs-search-open");
    activeIndex = -1;
  };

  const openModal = async () => {
    modal.hidden = false;
    document.body.classList.add("docs-search-open");
    input.focus();
    input.select();
    setStatus("Loading search index…");
    try {
      await ensureIndex();
      renderResults(input.value);
    } catch (error) {
      console.error(error);
      setStatus("Search is temporarily unavailable.");
    }
  };

  input.addEventListener("input", () => {
    if (indexEntries === null) {
      return;
    }
    renderResults(input.value);
  });

  resultsNode.addEventListener("mousemove", (event) => {
    const target = event.target instanceof Element ? event.target.closest(".docs-search-result") : null;
    if (!(target instanceof HTMLElement) || !target.dataset.index) {
      return;
    }
    setActiveResult(Number(target.dataset.index));
  });

  resultsNode.addEventListener("click", () => {
    closeModal();
  });

  modal.addEventListener("click", (event) => {
    const target = event.target;
    if (target instanceof HTMLElement && target.hasAttribute("data-docs-search-close")) {
      closeModal();
    }
  });

  document.addEventListener("keydown", (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      if (modal.hidden) {
        void openModal();
      } else {
        input.focus();
        input.select();
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
      setActiveResult(activeIndex + 1);
      return;
    }
    if (event.key === "ArrowUp") {
      event.preventDefault();
      setActiveResult(activeIndex - 1);
      return;
    }
    if (event.key === "Enter" && activeIndex >= 0) {
      const activeResult = resultsNode.querySelector(`.docs-search-result[data-index="${activeIndex}"]`);
      if (activeResult instanceof HTMLElement) {
        activeResult.click();
      }
    }
  });

  openButtons.forEach((button) => {
    button.addEventListener("click", () => {
      void openModal();
    });
  });

  closeButtons.forEach((button) => {
    button.addEventListener("click", closeModal);
  });
})();
