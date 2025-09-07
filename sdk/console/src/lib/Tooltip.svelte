<!--|                                                                            |-->
<!--|  Copyright The Telepact Authors                                            |-->
<!--|                                                                            |-->
<!--|  Licensed under the Apache License, Version 2.0 (the "License");           |-->
<!--|  you may not use this file except in compliance with the License.          |-->
<!--|  You may obtain a copy of the License at                                   |-->
<!--|                                                                            |-->
<!--|  https://www.apache.org/licenses/LICENSE-2.0                               |-->
<!--|                                                                            |-->
<!--|  Unless required by applicable law or agreed to in writing, software       |-->
<!--|  distributed under the License is distributed on an "AS IS" BASIS,         |-->
<!--|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  |-->
<!--|  See the License for the specific language governing permissions and       |-->
<!--|  limitations under the License.                                            |-->
<!--|                                                                            |-->

<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  export let text = '';
  export let position = 'bottom'; // 'top' | 'bottom' | 'left' | 'right'
  let show = false;
  let tooltipEl: HTMLElement;
  let triggerEl: HTMLElement;

  // Optional: auto-positioning (basic)s
  let tooltipStyle = '';

  function handleMouseEnter() {
    show = true;
    setTimeout(() => {
      if (show && tooltipEl && triggerEl) {
        const rect = triggerEl.getBoundingClientRect();
        const tooltipRect = tooltipEl.getBoundingClientRect();
        let top, left;
        switch (position) {
          case 'bottom':
            top = rect.bottom + window.scrollY + 8;
            left = rect.left + window.scrollX + rect.width / 2 - tooltipRect.width / 2;
            break;
          case 'left':
            top = rect.top + window.scrollY + rect.height / 2 - tooltipRect.height / 2;
            left = rect.left + window.scrollX - tooltipRect.width - 8;
            break;
          case 'right':
            top = rect.top + window.scrollY + rect.height / 2 - tooltipRect.height / 2;
            left = rect.right + window.scrollX + 8;
            break;
          default: // top
            top = rect.top + window.scrollY - tooltipRect.height - 8;
            left = rect.left + window.scrollX + rect.width / 2 - tooltipRect.width / 2;
        }
        tooltipStyle = `top:${top}px;left:${left}px;`;
      }
    }, 1);
  }

  function handleMouseLeave() {
    show = false;
  }

  onMount(() => {
    window.addEventListener('scroll', handleMouseLeave, true);
  });
  onDestroy(() => {
    window.removeEventListener('scroll', handleMouseLeave, true);
  });
</script>

<div
  bind:this={triggerEl}
  class="relative"
  on:mouseenter={handleMouseEnter}
  on:mouseleave={handleMouseLeave}
  on:focus={handleMouseEnter}
  on:blur={handleMouseLeave}
>
  <slot />
  {#if show && text}
    <span
      bind:this={tooltipEl}
      class="fixed z-50 px-3 py-2 text-sm rounded shadow-lg bg-gray-900 text-white opacity-90 pointer-events-none transition-opacity duration-100"
      style={tooltipStyle}
      role="tooltip"
      aria-live="polite"
    >
      {text}
    </span>
  {/if}
</div>