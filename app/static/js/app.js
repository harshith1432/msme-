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
      userBubble.className = 'd-flex justify-content-end mb-2';
      userBubble.innerHTML = `<div class="p-2 rounded bg-dark text-white" style="max-width: 80%; font-size: 0.875rem;">${escapeHtml(query)}</div>`;
      chatMessages.appendChild(userBubble);
      chatInput.value = '';
      chatMessages.scrollTop = chatMessages.scrollHeight;

      // Loading bubble
      const loadingBubble = document.createElement('div');
      loadingBubble.className = 'd-flex justify-content-start mb-2';
      loadingBubble.innerHTML = `<div class="p-2 rounded bg-light border text-muted" style="max-width: 80%; font-size: 0.875rem;"><span class="spinner-border spinner-border-sm me-1"></span> Analyzing official regulatory rules...</div>`;
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
        const plan = data.action_plan;
        const aiBubble = document.createElement('div');
        aiBubble.className = 'd-flex justify-content-start mb-3';

        let topAction = (plan.immediate_priorities && plan.immediate_priorities[0]) 
          ? plan.immediate_priorities[0] 
          : { action: 'Verify Udyam & State Registration', why: 'Core requirement' };

        aiBubble.innerHTML = `
          <div class="p-3 rounded bg-light border text-dark" style="max-width: 90%; font-size: 0.875rem;">
            <div class="fw-bold mb-1">⚡ Recommended Immediate Action:</div>
            <div class="mb-2"><strong>${escapeHtml(topAction.action)}</strong></div>
            <p class="small text-muted mb-2">${escapeHtml(topAction.why)}</p>
            <div class="d-flex gap-2">
              <a href="${topAction.portal}" target="_blank" class="btn btn-sm btn-dark">Open Official Portal</a>
              <a href="/advisor" class="btn btn-sm btn-outline-secondary">View 5-Part Plan</a>
            </div>
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
  }

  function escapeHtml(text) {
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return text.replace(/[&<>"']/g, m => map[m]);
  }
});
