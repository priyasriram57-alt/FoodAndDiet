// Charts and Visualization Functions

class NutritionCharts {
    constructor() {
        this.charts = {};
    }
    
    // Initialize all charts on page
    initializeAllCharts() {
        if (document.getElementById('macroChart')) {
            this.createMacroNutrientChart();
        }
        if (document.getElementById('calorieTrendChart')) {
            this.createCalorieTrendChart();
        }
        if (document.getElementById('nutrientTrendChart')) {
            this.createNutrientTrendChart();
        }
        if (document.getElementById('foodCategoryChart')) {
            this.createFoodCategoryChart();
        }
        if (document.getElementById('mealDistributionChart')) {
            this.createMealDistributionChart();
        }
    }
    
    // Create macro nutrient distribution chart (Doughnut)
    createMacroNutrientChart(containerId = 'macroChart') {
        const ctx = document.getElementById(containerId);
        if (!ctx) return;
        
        // Default data
        let protein = 30, carbs = 50, fat = 20;

        // Use real data if available (Goals distribution)
        if (window.userNutritionStats) {
            const stats = window.userNutritionStats;
            // Calories from macros: P=4, C=4, F=9
            const pCal = stats.daily_protein * 4;
            const cCal = stats.daily_carbs * 4;
            const fCal = stats.daily_fat * 9;
            const total = pCal + cCal + fCal;
            
            if (total > 0) {
                protein = Math.round((pCal / total) * 100);
                carbs = Math.round((cCal / total) * 100);
                fat = Math.round((fCal / total) * 100);
            }
        }
        
        const data = {
            labels: ['Protein', 'Carbohydrates', 'Fat'],
            datasets: [{
                data: [protein, carbs, fat],
                backgroundColor: [
                    '#10b981', // Success Green
                    '#3b82f6', // Info Blue
                    '#f59e0b'  // Warning Orange
                ],
                borderColor: ['#ffffff', '#ffffff', '#ffffff'],
                borderWidth: 2,
                hoverOffset: 4
            }]
        };
        
        this.charts.macro = new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: {
                                family: "'Poppins', sans-serif",
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(255, 255, 255, 0.9)',
                        titleColor: '#1f2937',
                        bodyColor: '#1f2937',
                        borderColor: '#e5e7eb',
                        borderWidth: 1,
                        padding: 10,
                        callbacks: {
                            label: function(context) {
                                return `${context.label}: ${context.parsed}%`;
                            }
                        }
                    }
                },
                cutout: '75%'
            }
        });
    }
    
    // Create calorie trend chart (Line)
    createCalorieTrendChart(containerId = 'calorieTrendChart') {
        const ctx = document.getElementById(containerId);
        if (!ctx) return;
        
        const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        // Mock data for trend
        const calorieData = [2100, 2200, 1950, 2300, 2050, 2400, 1900];
        const targetData = Array(7).fill(window.userNutritionStats?.daily_calories || 2200);
        
        this.charts.calorieTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Calories Consumed',
                        data: calorieData,
                        borderColor: '#4361ee', // Primary
                        backgroundColor: 'rgba(67, 97, 238, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: '#ffffff',
                        pointBorderColor: '#4361ee',
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Daily Target',
                        data: targetData,
                        borderColor: '#10b981', // Success
                        backgroundColor: 'transparent',
                        borderDash: [5, 5],
                        borderWidth: 2,
                        pointRadius: 0,
                        tension: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        align: 'end',
                        labels: {
                            usePointStyle: true,
                            boxWidth: 8
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(255, 255, 255, 0.9)',
                        titleColor: '#1f2937',
                        bodyColor: '#1f2937',
                        borderColor: '#e5e7eb',
                        borderWidth: 1,
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: false,
                        grid: {
                            borderDash: [2, 2],
                            color: '#f3f4f6'
                        },
                         title: {
                            display: true,
                            text: 'Calories'
                        }
                    }
                },
                 interaction: {
                    intersect: false,
                    mode: 'nearest'
                }
            }
        });
    }
    // Create Nutrient Trend Chart (Multi-line with Dual Axis)
    createNutrientTrendChart(containerId = 'nutrientTrendChart') {
        const ctx = document.getElementById(containerId);
        if (!ctx) return;
        
        const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        
        this.charts.nutrientTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Calories',
                        data: [2100, 2250, 1950, 2300, 2100, 2450, 2000],
                        borderColor: '#4361ee', // Primary
                        backgroundColor: 'rgba(67, 97, 238, 0.1)',
                        borderWidth: 2,
                        yAxisID: 'y',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Protein',
                        data: [130, 145, 125, 150, 140, 160, 135],
                        borderColor: '#10b981', // Success
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        yAxisID: 'y1',
                        borderDash: [5, 5],
                        tension: 0.4
                    },
                    {
                        label: 'Carbs',
                        data: [250, 270, 230, 280, 260, 300, 240],
                        borderColor: '#3b82f6', // Info
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        yAxisID: 'y1',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        position: 'top',
                        align: 'end',
                        labels: {
                            usePointStyle: true,
                            boxWidth: 8,
                            font: { family: "'Poppins', sans-serif" }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(255, 255, 255, 0.9)',
                        titleColor: '#1f2937',
                        bodyColor: '#1f2937',
                        borderColor: '#e5e7eb',
                        borderWidth: 1,
                        padding: 10
                    }
                },
                scales: {
                    x: {
                        grid: { display: false }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: { display: true, text: 'Calories' },
                        grid: { borderDash: [2, 2], color: '#f3f4f6' }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: { display: true, text: 'Grams (Protein/Carbs)' },
                        grid: { drawOnChartArea: false }
                    }
                }
            }
        });
    }
}

// Instantiate and export
const nutritionCharts = new NutritionCharts();
window.NutritionCharts = nutritionCharts; 

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    nutritionCharts.initializeAllCharts();
});
