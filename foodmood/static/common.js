// Common utilities for the FoodMood application

// Enable Bootstrap tooltips
function enableBootstrapTooltips() {
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

// CSRF token helper
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

// Initialize Tom Select for edibles/ingredients with quick-create support
function initializeTomSelect(elementId, createUrl, placeholder) {
  const selectElement = document.getElementById(elementId);
  if (!selectElement || !window.TomSelect) return;

  const csrfToken = getCookie('csrftoken');

  const ts = new TomSelect(selectElement, {
    plugins: ['remove_button'],
    create: function(input, callback) {
      fetch(createUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
          'X-CSRFToken': csrfToken || ''
        },
        body: new URLSearchParams({ name: input }).toString()
      }).then(r => r.json()).then(data => {
        if (!data.ok) { callback(); return; }
        const option = { value: String(data.id), text: data.name };
        callback(option);
        ts.addItem(option.value);
        ts.setTextboxValue('');
        ts.refreshOptions(false);
      }).catch(() => callback());
    },
    persist: false,
    maxOptions: 1000,
    placeholder: placeholder || selectElement.getAttribute('data-placeholder') || 'Select items',
    allowEmptyOption: true,
    closeAfterSelect: false,
    hideSelected: true,
    onItemAdd: function(value, item) {
      this.setTextboxValue('');
      this.refreshOptions(false);
    },
    render: {
      option: function(data, escape) {
        return '<div>' + escape(data.text) + '</div>';
      },
      item: function(data, escape) {
        return '<div>' + escape(data.text) + '</div>';
      }
    }
  });

  return ts;
}
