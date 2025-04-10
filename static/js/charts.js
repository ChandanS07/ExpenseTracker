/**
 * Initialize dashboard charts
 */
function initDashboardCharts() {
    // Get the chart canvas elements
    const categoryChartCanvas = document.getElementById('categoryChart');
    const trendChartCanvas = document.getElementById('trendChart');
    
    if (!categoryChartCanvas || !trendChartCanvas) {
        console.error('Chart canvas elements not found');
        return;
    }
    
    // Set the default period
    const period = document.getElementById('chartPeriod') ? 
        document.getElementById('chartPeriod').value : 'month';
    
    // Load category breakdown data
    fetch(`/api/category-breakdown?period=${period}`)
        .then(response => response.json())
        .then(data => {
            if (data.labels.length === 0) {
                displayNoDataMessage(categoryChartCanvas, 'No expense data available for the selected period');
                return;
            }
            
            const categoryColors = generateCategoryColors(data.labels.length);
            
            // Create the category pie chart
            new Chart(categoryChartCanvas, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: categoryColors,
                        borderColor: 'rgba(255, 255, 255, 0.8)',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    legend: {
                        position: 'right',
                        labels: {
                            padding: 20,
                            fontFamily: "'Roboto', 'Open Sans', sans-serif",
                            fontColor: '#212121'
                        }
                    },
                    tooltips: {
                        callbacks: {
                            label: function(tooltipItem, data) {
                                const value = data.datasets[0].data[tooltipItem.index];
                                return `${data.labels[tooltipItem.index]}: $${value.toFixed(2)}`;
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: 'Spending by Category',
                        fontFamily: "'Roboto', 'Open Sans', sans-serif",
                        fontSize: 16,
                        fontColor: '#212121'
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading category data:', error);
            displayNoDataMessage(categoryChartCanvas, 'Error loading category data');
        });
    
    // Load monthly trend data
    fetch('/api/monthly-trend?months=6')
        .then(response => response.json())
        .then(data => {
            if (data.labels.length === 0) {
                displayNoDataMessage(trendChartCanvas, 'No expense trend data available');
                return;
            }
            
            // Create the monthly trend line chart
            new Chart(trendChartCanvas, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Monthly Expenses',
                        data: data.data,
                        backgroundColor: 'rgba(25, 118, 210, 0.1)',
                        borderColor: '#1976D2',
                        pointBackgroundColor: '#1976D2',
                        pointBorderColor: '#FFF',
                        pointRadius: 4,
                        borderWidth: 3,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        xAxes: [{
                            gridLines: {
                                display: false
                            },
                            ticks: {
                                fontFamily: "'Roboto', 'Open Sans', sans-serif",
                                fontColor: '#757575'
                            }
                        }],
                        yAxes: [{
                            gridLines: {
                                color: 'rgba(0, 0, 0, 0.05)',
                                zeroLineColor: 'rgba(0, 0, 0, 0.1)'
                            },
                            ticks: {
                                beginAtZero: true,
                                fontFamily: "'Roboto', 'Open Sans', sans-serif",
                                fontColor: '#757575',
                                callback: function(value) {
                                    return '$' + value;
                                }
                            }
                        }]
                    },
                    legend: {
                        display: false
                    },
                    tooltips: {
                        callbacks: {
                            label: function(tooltipItem) {
                                return 'Expenses: $' + tooltipItem.yLabel.toFixed(2);
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: 'Monthly Spending Trend',
                        fontFamily: "'Roboto', 'Open Sans', sans-serif",
                        fontSize: 16,
                        fontColor: '#212121'
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading trend data:', error);
            displayNoDataMessage(trendChartCanvas, 'Error loading trend data');
        });
}

/**
 * Generate colors for the categories
 */
function generateCategoryColors(count) {
    const baseColors = [
        '#2E7D32', // Primary (Forest Green)
        '#1976D2', // Secondary (Royal Blue)
        '#FFC107', // Accent (Amber)
        '#9C27B0', // Purple
        '#E91E63', // Pink
        '#FF5722', // Deep Orange
        '#00BCD4', // Cyan
        '#3F51B5', // Indigo
        '#009688', // Teal
        '#8BC34A'  // Light Green
    ];
    
    let colors = [];
    
    // If we have 10 or fewer categories, use the base colors
    if (count <= baseColors.length) {
        colors = baseColors.slice(0, count);
    } else {
        // Otherwise, create additional colors by adjusting lightness
        colors = [...baseColors];
        
        while (colors.length < count) {
            const index = colors.length % baseColors.length;
            const baseColor = baseColors[index];
            
            // Adjust the color by making it slightly lighter
            const lighterColor = adjustColorLightness(baseColor, 10 * (Math.floor(colors.length / baseColors.length) + 1));
            colors.push(lighterColor);
        }
    }
    
    return colors;
}

/**
 * Adjust color lightness
 */
function adjustColorLightness(hex, percent) {
    // Convert hex to RGB
    let r = parseInt(hex.substring(1, 3), 16);
    let g = parseInt(hex.substring(3, 5), 16);
    let b = parseInt(hex.substring(5, 7), 16);
    
    // Increase each channel by the percentage
    r = Math.min(255, r + Math.floor(255 * percent / 100));
    g = Math.min(255, g + Math.floor(255 * percent / 100));
    b = Math.min(255, b + Math.floor(255 * percent / 100));
    
    // Convert RGB back to hex
    return '#' + 
        (r.toString(16).padStart(2, '0')) + 
        (g.toString(16).padStart(2, '0')) + 
        (b.toString(16).padStart(2, '0'));
}

/**
 * Display a "no data" message on the chart canvas
 */
function displayNoDataMessage(canvas, message) {
    const ctx = canvas.getContext('2d');
    
    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw the message
    ctx.font = '14px Roboto, "Open Sans", sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#757575';
    ctx.fillText(message, canvas.width / 2, canvas.height / 2);
}

/**
 * Update charts when period changes
 */
function updateChartPeriod() {
    // Clear existing charts
    const categoryChartCanvas = document.getElementById('categoryChart');
    const trendChartCanvas = document.getElementById('trendChart');
    
    if (categoryChartCanvas && trendChartCanvas) {
        const categoryCtx = categoryChartCanvas.getContext('2d');
        const trendCtx = trendChartCanvas.getContext('2d');
        
        categoryCtx.clearRect(0, 0, categoryChartCanvas.width, categoryChartCanvas.height);
        trendCtx.clearRect(0, 0, trendChartCanvas.width, trendChartCanvas.height);
    }
    
    // Reinitialize charts
    initDashboardCharts();
    
    // Update financial insights
    loadFinancialInsights();
}

/**
 * Load financial insights
 */
function loadFinancialInsights() {
    const insightsContainer = document.getElementById('financialInsights');
    
    if (!insightsContainer) {
        return;
    }
    
    fetch('/api/financial-insights')
        .then(response => response.json())
        .then(data => {
            const html = `
                <div class="insight-item">
                    <div class="insight-label">Top Spending Category</div>
                    <div class="insight-value">${data.top_spending_category}</div>
                </div>
                <div class="insight-item">
                    <div class="insight-label">Biggest Expense</div>
                    <div class="insight-value">${data.biggest_expense}</div>
                </div>
                <div class="insight-item">
                    <div class="insight-label">Average Transaction</div>
                    <div class="insight-value">$${data.average_transaction.toFixed(2)}</div>
                </div>
                <div class="insight-item">
                    <div class="insight-label">Spending Trend</div>
                    <div class="insight-value">${data.spending_trend}</div>
                </div>
            `;
            
            insightsContainer.innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading financial insights:', error);
            insightsContainer.innerHTML = '<p class="text-muted">Unable to load financial insights.</p>';
        });
}

/**
 * Load expense statistics for the dashboard
 */
function loadExpenseStats() {
    const totalExpenseElem = document.getElementById('totalExpense');
    const avgExpenseElem = document.getElementById('avgExpense');
    const expenseCountElem = document.getElementById('expenseCount');
    
    if (!totalExpenseElem || !avgExpenseElem || !expenseCountElem) {
        return;
    }
    
    // Get the current period
    const period = document.getElementById('chartPeriod') ? 
        document.getElementById('chartPeriod').value : 'month';
    
    fetch(`/api/expense-stats?period=${period}`)
        .then(response => response.json())
        .then(data => {
            totalExpenseElem.textContent = `$${data.total.toFixed(2)}`;
            avgExpenseElem.textContent = `$${data.average_per_day.toFixed(2)}`;
            expenseCountElem.textContent = data.count;
        })
        .catch(error => {
            console.error('Error loading expense stats:', error);
            totalExpenseElem.textContent = '$0.00';
            avgExpenseElem.textContent = '$0.00';
            expenseCountElem.textContent = '0';
        });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('categoryChart')) {
        initDashboardCharts();
        loadFinancialInsights();
        loadExpenseStats();
    }
});
