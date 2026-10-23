// Chart.js helper for Personal Expense Tracker
document.addEventListener('DOMContentLoaded', function () {
    const categoryChartElem = document.getElementById('categoryDoughnutChart');
    const incomeExpenseChartElem = document.getElementById('incomeExpenseBarChart');
    const spendingTrendChartElem = document.getElementById('spendingTrendLineChart');
    const paymentMethodChartElem = document.getElementById('paymentMethodChart');

    // Only load if on dashboard or analytics view
    if (!categoryChartElem && !incomeExpenseChartElem && !spendingTrendChartElem) {
        return;
    }

    const monthSelect = document.getElementById('analyticsMonthFilter');
    const yearSelect = document.getElementById('analyticsYearFilter');

    function fetchAndRenderCharts() {
        let url = '/api/analytics-data';
        const params = new URLSearchParams();
        if (monthSelect && monthSelect.value) {
            params.append('month', monthSelect.value);
        }
        if (yearSelect && yearSelect.value) {
            params.append('year', yearSelect.value);
        }
        if (params.toString()) {
            url += '?' + params.toString();
        }

        fetch(url)
            .then(res => res.json())
            .then(data => {
                renderCategoryChart(data.categories);
                if (incomeExpenseChartElem) renderIncomeExpenseChart(data.income_vs_expense);
                if (spendingTrendChartElem) renderSpendingTrendChart(data.spending_trend);
                if (paymentMethodChartElem) renderPaymentMethodChart(data.payment_methods);
            })
            .catch(err => console.error('Error fetching analytics:', err));
    }

    let catChartInstance = null;
    function renderCategoryChart(catData) {
        if (!categoryChartElem) return;
        if (catChartInstance) catChartInstance.destroy();

        if (!catData.labels || catData.labels.length === 0) {
            const ctx = categoryChartElem.getContext('2d');
            ctx.clearRect(0, 0, categoryChartElem.width, categoryChartElem.height);
            categoryChartElem.parentElement.querySelector('.chart-no-data')?.remove();
            const msg = document.createElement('div');
            msg.className = 'chart-no-data text-center text-muted py-5';
            msg.innerHTML = '<i class="bi bi-pie-chart fs-1 opacity-50 mb-2"></i><p>No expense data logged for this period.</p>';
            categoryChartElem.parentElement.appendChild(msg);
            categoryChartElem.style.display = 'none';
            return;
        } else {
            categoryChartElem.style.display = 'block';
            categoryChartElem.parentElement.querySelector('.chart-no-data')?.remove();
        }

        catChartInstance = new Chart(categoryChartElem, {
            type: 'doughnut',
            data: {
                labels: catData.labels,
                datasets: [{
                    data: catData.data,
                    backgroundColor: catData.colors && catData.colors.length ? catData.colors : [
                        '#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#8b5cf6', '#ec4899', '#64748b'
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff',
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            boxWidth: 12,
                            padding: 14,
                            font: { family: 'Inter', size: 12 }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const val = context.raw || 0;
                                return ` ${context.label}: ${val.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
                            }
                        }
                    }
                },
                cutout: '68%'
            }
        });
    }

    let incExpChartInstance = null;
    function renderIncomeExpenseChart(trendData) {
        if (!incomeExpenseChartElem) return;
        if (incExpChartInstance) incExpChartInstance.destroy();

        incExpChartInstance = new Chart(incomeExpenseChartElem, {
            type: 'bar',
            data: {
                labels: trendData.labels,
                datasets: [
                    {
                        label: 'Income',
                        data: trendData.income,
                        backgroundColor: '#10b981',
                        borderRadius: 6,
                        maxBarThickness: 30
                    },
                    {
                        label: 'Expense',
                        data: trendData.expense,
                        backgroundColor: '#ef4444',
                        borderRadius: 6,
                        maxBarThickness: 30
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { boxWidth: 12, font: { family: 'Inter' } }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: '#f1f5f9' },
                        ticks: { font: { family: 'Inter' } }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { font: { family: 'Inter' } }
                    }
                }
            }
        });
    }

    let spendingTrendInstance = null;
    function renderSpendingTrendChart(trendData) {
        if (!spendingTrendChartElem) return;
        if (spendingTrendInstance) spendingTrendInstance.destroy();

        spendingTrendInstance = new Chart(spendingTrendChartElem, {
            type: 'line',
            data: {
                labels: trendData.labels,
                datasets: [{
                    label: 'Daily Spending',
                    data: trendData.data,
                    borderColor: '#4f46e5',
                    backgroundColor: 'rgba(79, 70, 229, 0.08)',
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: '#4f46e5',
                    pointRadius: 3,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: '#f1f5f9' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: {
                            maxTicksLimit: 10,
                            font: { family: 'Inter', size: 11 }
                        }
                    }
                }
            }
        });
    }

    let pmChartInstance = null;
    function renderPaymentMethodChart(pmData) {
        if (!paymentMethodChartElem) return;
        if (pmChartInstance) pmChartInstance.destroy();

        pmChartInstance = new Chart(paymentMethodChartElem, {
            type: 'polarArea',
            data: {
                labels: pmData.labels,
                datasets: [{
                    data: pmData.data,
                    backgroundColor: [
                        'rgba(79, 70, 229, 0.7)',
                        'rgba(16, 185, 129, 0.7)',
                        'rgba(245, 158, 11, 0.7)',
                        'rgba(6, 182, 212, 0.7)',
                        'rgba(139, 92, 246, 0.7)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 10 } }
                }
            }
        });
    }

    // Attach change events if filter dropdowns exist
    if (monthSelect) monthSelect.addEventListener('change', fetchAndRenderCharts);
    if (yearSelect) yearSelect.addEventListener('change', fetchAndRenderCharts);

    // Initial fetch
    fetchAndRenderCharts();
});
