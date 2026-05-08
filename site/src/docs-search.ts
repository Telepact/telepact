(() => {
  const searchInput = document.getElementById('docs-search');
  if (!(searchInput instanceof HTMLInputElement)) {
    return;
  }

  const clearButton = document.querySelector('.docs-search-clear');
  const noResultsMessage = document.querySelector('.docs-search-empty');

  /**
   * @param {string} value
   * @returns {string}
   */
  const normalize = (value) => value.toLowerCase().replace(/\s+/g, ' ').trim();

  const navGroups = Array.from(document.querySelectorAll('.docs-nav-group'))
    .filter((group) => group instanceof HTMLElement)
    .map((group) => {
      if (!(group instanceof HTMLElement)) {
        return null;
      }
      const directChildren = Array.from(group.children);
      const topLevelList = directChildren.find((child) => child.tagName === 'UL');
      const subgroups = directChildren
        .filter((child) => child instanceof HTMLElement && child.classList.contains('docs-nav-subgroup'))
        .map((subgroup) => ({
          element: subgroup,
          heading: normalize(subgroup.querySelector('.docs-nav-subheading')?.textContent || ''),
          items: Array.from(subgroup.querySelectorAll('li'))
            .filter((item) => item instanceof HTMLElement)
            .map((item) => ({
              element: item,
              text: normalize(item.textContent || ''),
            })),
        }));

      return {
        element: group,
        heading: normalize(group.querySelector('h3')?.textContent || ''),
        items: Array.from(topLevelList?.children || [])
          .filter((item) => item instanceof HTMLElement)
          .map((item) => ({
            element: item,
            text: normalize(item.textContent || ''),
          })),
        subgroups,
      };
    })
    .filter((group) => group !== null);

  /**
   * @param {Array<{ element: HTMLElement; text: string }>} items
   * @param {string} query
   * @param {boolean} parentMatches
   * @returns {boolean}
   */
  const setLinkVisibility = (items, query, parentMatches) => {
    let anyVisible = false;
    items.forEach((item) => {
      const visible = !query || parentMatches || item.text.includes(query);
      item.element.hidden = !visible;
      if (visible) {
        anyVisible = true;
      }
    });
    return anyVisible;
  };

  const applyFilter = () => {
    const query = normalize(searchInput.value);
    if (clearButton instanceof HTMLElement) {
      clearButton.hidden = !query;
    }

    let anyGroupVisible = false;
    navGroups.forEach((group) => {
      const groupMatches = Boolean(query) && group.heading.includes(query);

      let groupVisible = setLinkVisibility(group.items, query, groupMatches);

      group.subgroups.forEach((subgroup) => {
        const subgroupMatches = groupMatches || (Boolean(query) && subgroup.heading.includes(query));
        const subgroupVisible = setLinkVisibility(subgroup.items, query, subgroupMatches);
        subgroup.element.hidden = Boolean(query) && !subgroupVisible;
        groupVisible = groupVisible || subgroupVisible;
      });

      group.element.hidden = Boolean(query) && !groupVisible;
      if (!group.element.hidden) {
        anyGroupVisible = true;
      }
    });

    if (noResultsMessage instanceof HTMLElement) {
      noResultsMessage.hidden = !query || anyGroupVisible;
    }
  };

  searchInput.addEventListener('input', applyFilter);
  if (clearButton instanceof HTMLButtonElement) {
    clearButton.addEventListener('click', () => {
      searchInput.value = '';
      applyFilter();
      searchInput.focus();
    });
  }
})();
