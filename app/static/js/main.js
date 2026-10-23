// Main UI Helpers
document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function () {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Dynamic category filtering based on transaction type (Expense / Income)
    const typeRadios = document.querySelectorAll('input[name="type"]');
    const categorySelect = document.getElementById('categorySelect');

    function filterCategoriesByType(selectedType) {
        if (!categorySelect) return;
        const options = categorySelect.querySelectorAll('option[data-type]');
        let firstVisibleSet = false;

        options.forEach(opt => {
            const optType = opt.getAttribute('data-type');
            if (optType === selectedType) {
                opt.style.display = '';
                if (!firstVisibleSet) {
                    categorySelect.value = opt.value;
                    firstVisibleSet = true;
                }
            } else {
                opt.style.display = 'none';
            }
        });
    }

    typeRadios.forEach(radio => {
        radio.addEventListener('change', function () {
            filterCategoriesByType(this.value);
        });
    });

    // Initial trigger for active radio
    const activeRadio = document.querySelector('input[name="type"]:checked');
    if (activeRadio) {
        filterCategoriesByType(activeRadio.value);
    }

    // Default today's date for date inputs if empty
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const todayStr = new Date().toISOString().split('T')[0];
    dateInputs.forEach(input => {
        if (!input.value && !input.getAttribute('data-preserve-empty')) {
            input.value = todayStr;
        }
    });
});
