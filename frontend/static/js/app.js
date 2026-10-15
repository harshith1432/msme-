/**
 * MSME Compliance & Incentives Navigator — Client-side App Logic
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Task Checkboxes
  const taskCheckboxes = document.querySelectorAll('.task-checkbox');
  taskCheckboxes.forEach(cb => {
    const id = cb.dataset.taskId;
    if (localStorage.getItem(`task_${id}`) === 'done') {
      cb.checked = true;
      const textElem = document.getElementById(`task_text_${id}`);
      if (textElem) textElem.classList.add('text-decoration-line-through', 'text-muted');
    }

    cb.addEventListener('change', function () {
      const textElem = document.getElementById(`task_text_${id}`);
      if (this.checked) {
        localStorage.setItem(`task_${id}`, 'done');
        if (textElem) textElem.classList.add('text-decoration-line-through', 'text-muted');
      } else {
        localStorage.removeItem(`task_${id}`);
        if (textElem) textElem.classList.remove('text-decoration-line-through', 'text-muted');
      }
    });
  });

  // 2. Compliance Table Filter
  const complianceSearch = document.getElementById('complianceSearch');
  const complianceDomainFilter = document.getElementById('complianceDomainFilter');
  const complianceRows = document.querySelectorAll('.compliance-row');

  function filterCompliance() {
    const q = (complianceSearch ? complianceSearch.value : '').toLowerCase();
    const domain = (complianceDomainFilter ? complianceDomainFilter.value : '').toLowerCase();

    complianceRows.forEach(row => {
      const text = row.innerText.toLowerCase();
      const rowDomain = (row.dataset.domain || '').toLowerCase();

      const matchQ = !q || text.includes(q);
      const matchDomain = !domain || rowDomain === domain;

      if (matchQ && matchDomain) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    });
  }

  if (complianceSearch) complianceSearch.addEventListener('input', filterCompliance);
  if (complianceDomainFilter) complianceDomainFilter.addEventListener('change', filterCompliance);

  // 3. Incentives Filter
  const incentiveSearch = document.getElementById('incentiveSearch');
  const incentiveCategoryFilter = document.getElementById('incentiveCategoryFilter');
  const incentiveCards = document.querySelectorAll('.incentive-card-wrapper');

  function filterIncentives() {
    const q = (incentiveSearch ? incentiveSearch.value : '').toLowerCase();
    const cat = (incentiveCategoryFilter ? incentiveCategoryFilter.value : '').toLowerCase();

    incentiveCards.forEach(card => {
      const text = card.innerText.toLowerCase();
      const cardCat = (card.dataset.category || '').toLowerCase();

      const matchQ = !q || text.includes(q);
      const matchCat = !cat || cardCat === cat;

      if (matchQ && matchCat) {
        card.style.display = '';
      } else {
        card.style.display = 'none';
      }
    });
  }

  if (incentiveSearch) incentiveSearch.addEventListener('input', filterIncentives);
  if (incentiveCategoryFilter) incentiveCategoryFilter.addEventListener('change', filterIncentives);

  // 4. AI Copilot Chat Drawer
  const chatForm = document.getElementById('copilotChatForm');
  const chatInput = document.getElementById('copilotInput');
  const chatMessages = document.getElementById('copilotMessages');

  if (chatForm && chatInput && chatMessages) {
    chatForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const query = chatInput.value.trim();
      if (!query) return;

      // Append user message
      const userBubble = document.createElement('div');
      userBubble.className = 'd-flex justify-content-end mb-2 w-100';
      userBubble.innerHTML = `<div class="p-2 px-3 rounded bg-dark text-white user-msg-bubble" style="max-width: 85%; font-size: 0.85rem; word-break: break-word; overflow-wrap: anywhere;">${escapeHtml(query)}</div>`;
      chatMessages.appendChild(userBubble);
      chatInput.value = '';
      chatMessages.scrollTop = chatMessages.scrollHeight;

      // Loading bubble
      const loadingBubble = document.createElement('div');
      loadingBubble.className = 'd-flex justify-content-start mb-2 w-100';
      loadingBubble.innerHTML = `<div class="p-2 rounded bg-light border text-muted copilot-msg-bubble" style="max-width: 100%; font-size: 0.85rem;"><span class="spinner-border spinner-border-sm me-1"></span> Analyzing official regulatory rules...</div>`;
      chatMessages.appendChild(loadingBubble);
      chatMessages.scrollTop = chatMessages.scrollHeight;

      // Fetch response
      fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: query })
      })
      .then(res => res.json())
      .then(data => {
        loadingBubble.remove();
        const plan = data.action_plan || {};
        const isRefusal = data.refusal;
        const answerText = data.text || "Guidance generated.";
        const aiBubble = document.createElement('div');
        aiBubble.className = 'd-flex justify-content-start mb-3 w-100';

        let citationsHtml = '';
        if (data.citations && data.citations.length > 0) {
          citationsHtml = '<div class="mt-2 pt-1 border-top"><div class="text-muted fw-bold" style="font-size: 0.7rem;">Verified Sources:</div><div class="d-flex flex-wrap gap-1 mt-1">';
          data.citations.forEach(c => {
            const label = c.law || c.authority || 'Regulatory Source';
            if (c.link) {
              citationsHtml += `<a href="${c.link}" target="_blank" class="badge bg-white text-dark border text-decoration-none" style="font-size: 0.68rem;"><i class="bi bi-link-45deg"></i> ${escapeHtml(label)}</a>`;
            } else {
              citationsHtml += `<span class="badge bg-white text-dark border" style="font-size: 0.68rem;">${escapeHtml(label)}</span>`;
            }
          });
          citationsHtml += '</div></div>';
        }

        let topicsHtml = '';
        if (data.available_topics && isRefusal) {
          const topDocs = data.available_topics.documents || [];
          const topCompliances = data.available_topics.compliances || [];
          const topIncentives = data.available_topics.incentives || [];
          const topVault = data.available_topics.vault || [];

          if (topDocs.length > 0 || topCompliances.length > 0 || topIncentives.length > 0 || topVault.length > 0) {
            topicsHtml = `
              <div class="mt-2 pt-2 border-top">
                <div class="fw-semibold text-muted mb-1" style="font-size: 0.72rem;">
                  <i class="bi bi-database-check text-success me-1"></i>Available in Authorized RAG Knowledge Base:
                </div>
                <div class="small text-muted" style="font-size: 0.74rem; line-height: 1.4; word-break: break-word; overflow-wrap: anywhere;">
                  ${topDocs.length > 0 ? `<div class="mb-1">&bull; <strong>Regulations:</strong> ${escapeHtml(topDocs.join(', '))}</div>` : ''}
                  ${topCompliances.length > 0 ? `<div class="mb-1">&bull; <strong>Compliances:</strong> ${escapeHtml(topCompliances.join(', '))}</div>` : ''}
                  ${topIncentives.length > 0 ? `<div class="mb-1">&bull; <strong>Subsidies:</strong> ${escapeHtml(topIncentives.join(', '))}</div>` : ''}
                  ${topVault.length > 0 ? `<div class="mb-1">&bull; <strong>Company Documents:</strong> ${escapeHtml(topVault.join(', '))}</div>` : ''}
                </div>
              </div>
            `;
          }
        }

        let suggestionsHtml = '';
        if (data.suggestions && data.suggestions.length > 0) {
          suggestionsHtml = `
            <div class="mt-2 pt-2 border-top">
              <div class="fw-semibold text-dark mb-1 d-flex align-items-center gap-1" style="font-size: 0.74rem;">
                <i class="bi bi-lightbulb-fill text-warning flex-shrink-0"></i>
                <span>${isRefusal ? 'You can ask me questions like (Click to ask):' : 'Suggested questions (Click to ask):'}</span>
              </div>
              <div class="d-flex flex-column gap-1 mt-1 w-100">
                ${data.suggestions.map(s => `
                  <button type="button" class="btn btn-sm btn-outline-secondary text-start py-1 px-2 suggestion-chip w-100" data-query="${escapeHtml(s)}" style="font-size: 0.75rem; border-radius: 6px; white-space: normal; word-break: break-word; overflow-wrap: anywhere;">
                    <i class="bi bi-arrow-right-circle text-primary me-1 flex-shrink-0"></i><span class="chip-text">${escapeHtml(s)}</span>
                  </button>
                `).join('')}
              </div>
            </div>
          `;
        }

        let topActionHtml = '';
        if (!isRefusal && plan.immediate_priorities && plan.immediate_priorities.length > 0) {
          const topAction = plan.immediate_priorities[0];
          topActionHtml = `
            <div class="mt-2 pt-2 border-top">
              <div class="small fw-semibold text-primary mb-1"><i class="bi bi-lightning-charge-fill me-1"></i>Related Immediate Milestone:</div>
              <div class="small text-muted mb-2">${escapeHtml(topAction.action)}</div>
              <div class="d-flex gap-2">
                ${topAction.portal ? `<a href="${topAction.portal}" target="_blank" class="btn btn-sm btn-dark py-0 px-2" style="font-size: 0.75rem;">Open Portal</a>` : ''}
                <a href="/advisor" class="btn btn-sm btn-outline-secondary py-0 px-2" style="font-size: 0.75rem;">Advisor Workspace</a>
              </div>
            </div>
          `;
        }

        let headerBadge = '';
        if (isRefusal) {
          headerBadge = `<span class="badge bg-warning-subtle text-dark border border-warning-subtle" style="font-size: 0.7rem;"><i class="bi bi-info-circle me-1"></i>Topic Not Found in RAG</span>`;
        } else if (data.is_greeting) {
          headerBadge = `<span class="badge bg-primary-subtle text-primary border border-primary-subtle" style="font-size: 0.7rem;"><i class="bi bi-stars me-1"></i>Regulatory Assistant</span>`;
        } else {
          headerBadge = `<span class="badge bg-success-subtle text-success border border-success-subtle" style="font-size: 0.7rem;"><i class="bi bi-shield-check me-1"></i>RAG Grounded</span>`;
        }

        aiBubble.innerHTML = `
          <div class="p-3 rounded bg-light border text-dark shadow-sm copilot-msg-bubble w-100" style="max-width: 100%; font-size: 0.85rem; word-break: break-word; overflow-wrap: anywhere; box-sizing: border-box;">
            <div class="d-flex justify-content-between align-items-center mb-2 flex-wrap gap-1">
              ${headerBadge}
              <span class="text-muted" style="font-size: 0.7rem;">Hugging Face LLM</span>
            </div>
            <div class="mb-1 text-dark" style="line-height: 1.45; word-break: break-word; overflow-wrap: anywhere;">${formatMarkdown(answerText)}</div>
            ${citationsHtml}
            ${topicsHtml}
            ${suggestionsHtml}
            ${topActionHtml}
          </div>
        `;
        chatMessages.appendChild(aiBubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
      })
      .catch(err => {
        loadingBubble.remove();
        const errBubble = document.createElement('div');
        errBubble.className = 'd-flex justify-content-start mb-2';
        errBubble.innerHTML = `<div class="p-2 rounded bg-danger text-white" style="font-size: 0.85rem;">Error retrieving guidance. Please try again.</div>`;
        chatMessages.appendChild(errBubble);
      });
    });

    // Handle suggestion chip and quick prompt clicks
    chatMessages.addEventListener('click', function (e) {
      const chip = e.target.closest('.suggestion-chip, .copilot-quick-prompt');
      if (chip) {
        const q = chip.getAttribute('data-query') || chip.getAttribute('data-prompt') || chip.innerText.trim();
        if (q) {
          chatInput.value = q;
          chatForm.dispatchEvent(new Event('submit', { cancelable: true }));
        }
      }
    });
  }

  function escapeHtml(text) {
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return (text || '').replace(/[&<>"']/g, m => map[m]);
  }

  function formatMarkdown(text) {
    if (!text) return '';
    let escaped = escapeHtml(text);
    escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    escaped = escaped.replace(/\*(.*?)\*/g, '<em>$1</em>');
    return escaped;
  }
});
