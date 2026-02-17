// Main Application JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
    
    // Authentication handling
    setupAuthForms();
    
    // Dashboard functionality
    if (window.location.pathname === '/dashboard') {
        initializeDashboard();
    } else if (window.location.pathname === '/recommendations') {
        initializeRecommendationsPage();
    } else if (window.location.pathname === '/meal-plans') {
        initializeMealPlansPage();
    }
    
    // Food logging
    setupFoodLogging();
    
    // Chart initialization
    // initializeCharts(); // Handled by charts.js
});

function initializeRecommendationsPage() {
    setupRecommendationButtons();
    
    // Main "Find Food" button
    const findBtn = document.getElementById('getRecommendationsBtn');
    if (findBtn) {
        findBtn.addEventListener('click', () => {
             const mealType = document.getElementById('recommendationMealType').value;
             getRecommendations(mealType);
        });
    }

    const refreshBtn = document.getElementById('refreshRecommendations');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
             const mealType = document.getElementById('recommendationMealType').value;
             getRecommendations(mealType);
        });
    }

    // Add listeners for filters if needed
    const filters = ['recommendationMealType', 'recommendationCategory', 'recommendationCuisine', 'recommendationSort'];
    filters.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('change', () => {
                // Logic to refresh recommendations based on filters
                // For now, simplistically trigger getRecommendations with meal type
                const mealType = document.getElementById('recommendationMealType').value;
                getRecommendations(mealType);
            });
        }
    });
    
    // Initial load
    getRecommendations('all');
    loadFavorites();
    loadRecentlyViewed();
}

async function loadFavorites() {
    try {
        const response = await fetch('/get_favorites');
        if (response.ok) {
            const data = await response.json();
            updateFavoritesList(data.favorites);
        }
    } catch (error) {
        console.error('Error loading favorites:', error);
    }
}

function updateFavoritesList(favorites) {
    const container = document.getElementById('favoriteFoods');
    if (!container) return;

    if (!favorites || favorites.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4 text-muted">
                <small>No favorites saved yet</small>
            </div>`;
        return;
    }

    let html = '';
    favorites.forEach(foodName => {
        html += `
            <div class="list-group-item bg-transparent border-0 px-0 py-2 d-flex justify-content-between align-items-center">
                <div class="d-flex align-items-center">
                    <div class="bg-danger bg-opacity-10 text-danger rounded p-2 me-3">
                        <i class="fas fa-heart"></i>
                    </div>
                    <div>
                        <h6 class="mb-0 text-dark small fw-bold">${foodName}</h6>
                    </div>
                </div>
            </div>`;
    });
    container.innerHTML = html;
}

function loadRecentlyViewed() {
    const container = document.getElementById('recentlyViewed');
    if (!container) return;

    try {
        const viewed = JSON.parse(localStorage.getItem('recentlyViewed')) || [];
        
        if (viewed.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4 text-muted">
                    <small>No items viewed yet</small>
                </div>`;
            return;
        }

        let html = '';
        viewed.slice(0, 5).forEach(item => { // Show last 5
            html += `
                <div class="list-group-item bg-transparent border-0 px-0 py-2 d-flex justify-content-between align-items-center">
                    <div class="d-flex align-items-center">
                        <div class="bg-primary bg-opacity-10 text-primary rounded p-2 me-3">
                            <i class="fas fa-eye"></i>
                        </div>
                        <div>
                            <h6 class="mb-0 text-dark small fw-bold">${item.name}</h6>
                            <small class="text-muted" style="font-size: 0.7rem;">${Math.round(item.calories)} kcal</small>
                        </div>
                    </div>
                    <span class="badge bg-light text-dark border ms-2">${item.category || 'Meal'}</span>
                </div>`;
        });
        container.innerHTML = html;
        
    } catch (e) {
        console.error('Error parsing recently viewed:', e);
    }
}

function addToRecentlyViewed(foodData) {
    try {
        let viewed = JSON.parse(localStorage.getItem('recentlyViewed')) || [];
        
        // Remove duplicate if exists (to move it to top)
        viewed = viewed.filter(item => item.name !== foodData.name);
        
        // Add to beginning
        viewed.unshift({
            name: foodData.name,
            calories: foodData.calories,
            category: foodData.category
        });
        
        // Limit to 10 items in storage
        if (viewed.length > 10) viewed = viewed.slice(0, 10);
        
        localStorage.setItem('recentlyViewed', JSON.stringify(viewed));
        
        // Refresh UI if on recommendations page
        loadRecentlyViewed();
        
    } catch (e) {
        console.error('Error updating recently viewed:', e);
    }
}

function initializeMealPlansPage() {
    setupMealPlanGeneration();
    if (typeof loadSavedMealPlan === 'function') loadSavedMealPlan();
    
    const saveBtn = document.getElementById('saveCurrentPlan');
    if (saveBtn) saveBtn.addEventListener('click', saveMealPlan);
    
    const exportBtn = document.getElementById('exportGroceryList');
    if (exportBtn) exportBtn.addEventListener('click', exportGroceryList);
}

// Authentication functions
function setupAuthForms() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
}

async function handleLogin(e) {
    e.preventDefault();
    
    const formData = {
        username: document.getElementById('loginUsername').value,
        password: document.getElementById('loginPassword').value
    };
    
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Login successful!', 'success');
            setTimeout(() => {
                window.location.href = data.redirect || '/dashboard';
            }, 1000);
        } else {
            showNotification(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const formData = {
        username: document.getElementById('registerUsername').value,
        email: document.getElementById('registerEmail').value,
        password: document.getElementById('registerPassword').value,
        age: parseInt(document.getElementById('registerAge').value),
        gender: document.getElementById('registerGender').value,
        weight: parseFloat(document.getElementById('registerWeight').value),
        height: parseFloat(document.getElementById('registerHeight').value),
        activity_level: document.getElementById('registerActivity').value,
        dietary_goal: document.getElementById('registerGoal').value,
        health_conditions: getSelectedCheckboxes('healthConditions'),
        preferred_cuisines: getSelectedCheckboxes('preferredCuisines'),
        allergies: getSelectedCheckboxes('allergies'),
        disliked_foods: document.getElementById('dislikedFoods').value.split(',').map(f => f.trim()).filter(f => f),
        favorite_foods: document.getElementById('favoriteFoods').value.split(',').map(f => f.trim()).filter(f => f)
    };
    
    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Registration successful!', 'success');
            setTimeout(() => {
                window.location.href = data.redirect || '/dashboard';
            }, 1000);
        } else {
            showNotification(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

// Dashboard functions
function initializeDashboard() {
    // Load user stats
    loadUserStats();
    
    // Setup recommendation buttons
    setupRecommendationButtons();
    
    // Setup meal plan generation
    setupMealPlanGeneration();
    
    // Setup profile update
    setupProfileUpdate();
}

async function loadUserStats() {
    try {
        // Use server-provided stats if available, otherwise fallback
        let statsData = window.userNutritionStats || {
            daily_calories: 2200,
            daily_protein: 82,
            daily_carbs: 275,
            daily_fat: 49,
            bmi: 24.5
        };

        // Simulate daily intake progress (since we don't have real intake data yet)
        const intakeData = {
            today_intake: 1850,
            protein_intake: 75,
            carbs_intake: 220,
            fat_intake: 45
        };

        updateDashboardStats({ ...statsData, ...intakeData });
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

function updateDashboardStats(stats) {
    // Update Daily Target Values (Top Cards)
    const dailyCaloriesEl = document.getElementById('dailyCalories');
    const dailyProteinEl = document.getElementById('dailyProtein');
    const dailyCarbsEl = document.getElementById('dailyCarbs');
    const dailyFatEl = document.getElementById('dailyFat');

    if (dailyCaloriesEl) dailyCaloriesEl.textContent = stats.daily_calories;
    if (dailyProteinEl) dailyProteinEl.textContent = stats.daily_protein;
    if (dailyCarbsEl) dailyCarbsEl.textContent = stats.daily_carbs;
    if (dailyFatEl) dailyFatEl.textContent = stats.daily_fat;

    // Update calorie progress (New Design)
    const caloriePercentage = (stats.today_intake / stats.daily_calories) * 100;
    const calProgressBar = document.getElementById('calProgressBar');
    const calProgressVal = document.getElementById('calProgressVal');
    
    if (calProgressBar) {
        calProgressBar.style.width = `${Math.min(caloriePercentage, 100)}%`;
    }
    if (calProgressVal) {
        calProgressVal.textContent = `${Math.round(caloriePercentage)}%`;
    }
    
    // Update BMI
    const bmiVal = document.getElementById('bmiValue');
    if (bmiVal) bmiVal.textContent = stats.bmi;
    updateBMIIndicator(stats.bmi);
}

function updateProgressBar(elementId, percentage, current, total) {
    const element = document.getElementById(elementId);
    if (element) {
        const progressBar = element.querySelector('.progress-bar');
        progressBar.style.width = `${Math.min(percentage, 100)}%`;
        progressBar.textContent = `${Math.round(current)} / ${Math.round(total)}`;
        
        // Set color based on percentage
        if (percentage > 100) {
            progressBar.classList.remove('bg-success', 'bg-warning');
            progressBar.classList.add('bg-danger');
        } else if (percentage > 80) {
            progressBar.classList.remove('bg-success', 'bg-danger');
            progressBar.classList.add('bg-warning');
        } else {
            progressBar.classList.remove('bg-warning', 'bg-danger');
            progressBar.classList.add('bg-success');
        }
    }
}

function updateBMIIndicator(bmi) {
    const indicator = document.getElementById('bmiIndicator');
    let status = 'normal';
    let color = 'success';
    
    if (bmi < 18.5) {
        status = 'underweight';
        color = 'warning';
    } else if (bmi >= 25 && bmi < 30) {
        status = 'overweight';
        color = 'warning';
    } else if (bmi >= 30) {
        status = 'obese';
        color = 'danger';
    }
    
    indicator.className = `badge bg-${color}`;
    indicator.textContent = status.toUpperCase();
}

// Recommendation functions
function setupRecommendationButtons() {
    const buttons = document.querySelectorAll('.get-recommendations');
    buttons.forEach(button => {
        button.addEventListener('click', async function() {
            const mealType = this.dataset.mealType;
            await getRecommendations(mealType);
        });
    });
}

async function getRecommendations(mealType = 'all') {
    try {
        const containerId = document.getElementById('recommendationArea') ? 'recommendationArea' : 'recommendationsContainer';
        showLoading(containerId, 'Finding the perfect meals for you...');
        
        // Gather extended filters
        const categoryEl = document.getElementById('recommendationCategory');
        const cuisineEl = document.getElementById('recommendationCuisine');
        const sortEl = document.getElementById('recommendationSort');
        
        const payload = { 
            meal_type: mealType,
            category: (categoryEl && categoryEl.value !== 'all') ? categoryEl.value : null,
            cuisine: (cuisineEl && cuisineEl.value !== 'all') ? cuisineEl.value : null,
            sort_by: sortEl ? sortEl.value : 'score'
        };

        const response = await fetch('/get_recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayRecommendations(data.recommendations);
        } else {
            showNotification('Failed to get recommendations', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendationArea') || document.getElementById('recommendationsContainer');
    if (!container) return;
    
    if (recommendations.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No recommendations available. Try updating your preferences.</div>';
        return;
    }
    
    let html = '<div class="row">';
    
    recommendations.forEach(food => {
        // Safe stringify for data attribute
        const foodDataSafe = JSON.stringify(food).replace(/'/g, "&#39;");
        
        html += `
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100 shadow-sm hover-lift">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h5 class="card-title mb-0">${food.name}</h5>
                        <span class="badge bg-success rounded-pill">${food.score.toFixed(1)}</span>
                    </div>
                    
                    <div class="mb-3">
                        <span class="badge bg-light text-dark border">${food.category}</span>
                        <span class="badge bg-light text-dark border">${food.meal_suitability}</span>
                    </div>
                    
                    <div class="nutrition-grid mb-3">
                        <div class="text-center p-2 bg-light rounded">
                            <div class="small text-muted fw-bold">CAL</div>
                            <div class="fw-bold text-primary">${Math.round(food.calories)}</div>
                        </div>
                        <div class="text-center p-2 bg-light rounded">
                            <div class="small text-muted fw-bold">PRO</div>
                            <div class="fw-bold text-success">${Math.round(food.protein)}g</div>
                        </div>
                        <div class="text-center p-2 bg-light rounded">
                            <div class="small text-muted fw-bold">CARB</div>
                            <div class="fw-bold text-warning">${Math.round(food.carbs)}g</div>
                        </div>
                        <div class="text-center p-2 bg-light rounded">
                            <div class="small text-muted fw-bold">FAT</div>
                            <div class="fw-bold text-danger">${Math.round(food.fat)}g</div>
                        </div>
                    </div>
                    
                    <div class="d-grid gap-2 d-flex justify-content-between">
                        <button class="btn btn-sm btn-outline-info flex-grow-1 info-food" 
                                data-food='${foodDataSafe}'>
                            <i class="fas fa-info-circle me-1"></i> Info
                        </button>
                        <button class="btn btn-sm ${food.is_favorite ? 'btn-danger text-white' : 'btn-outline-danger'} flex-grow-1 save-food" 
                                data-name="${food.name.replace(/"/g, '&quot;')}" onclick="toggleFavorite(this)">
                            <i class="${food.is_favorite ? 'fas' : 'far'} fa-heart me-1"></i> Save
                        </button>
                        <button class="btn btn-sm btn-primary flex-grow-1 log-food" 
                                data-food='${foodDataSafe}'>
                            <i class="fas fa-plus me-1"></i> Log
                        </button>
                    </div>
                </div>
            </div>
        </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
    
    // Attach event listeners
    document.querySelectorAll('.log-food').forEach(button => {
        button.addEventListener('click', function() {
            const foodData = JSON.parse(this.dataset.food);
            showLogFoodModal(foodData);
        });
    });
    
    document.querySelectorAll('.info-food').forEach(button => {
        button.addEventListener('click', function() {
            const foodData = JSON.parse(this.dataset.food);
            showFoodInfoModal(foodData);
        });
    });
}

// Food logging functions
function setupFoodLogging() {
    // This function sets up food logging functionality
}

async function showLogFoodModal(foodData) {
    // Create and show modal for logging food
    const modalHtml = `
    <div class="modal fade" id="logFoodModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Log Food: ${foodData.name}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="logFoodForm">
                        <div class="mb-3">
                            <label class="form-label">Meal Type</label>
                            <select class="form-select" id="mealType" required>
                                <option value="breakfast">Breakfast</option>
                                <option value="lunch">Lunch</option>
                                <option value="dinner">Dinner</option>
                                <option value="snack">Snack</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Serving Size</label>
                            <input type="text" class="form-control" id="servingSize" value="1 serving" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Notes (optional)</label>
                            <textarea class="form-control" id="foodNotes" rows="2"></textarea>
                        </div>
                    </form>
                    <div class="alert alert-info">
                        <strong>Nutrition Info:</strong><br>
                        Calories: ${foodData.calories} | Protein: ${foodData.protein}g | 
                        Carbs: ${foodData.carbs}g | Fat: ${foodData.fat}g
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" id="confirmLogFoodBtn">Log Food</button>
                </div>
            </div>
        </div>
    </div>
    `;
    
    // Remove existing modal if present
    const existingModal = document.getElementById('logFoodModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Attach event listener to confirm button
    document.getElementById('confirmLogFoodBtn').addEventListener('click', () => submitFoodLog(foodData));
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('logFoodModal'));
    modal.show();
}

async function submitFoodLog(foodData) {
    try {
        const mealType = document.getElementById('mealType').value;
        
        const logData = {
            food_name: foodData.name,
            calories: foodData.calories,
            protein: foodData.protein,
            carbs: foodData.carbs,
            fat: foodData.fat,
            meal_type: mealType
        };
        
        const response = await fetch('/log_food', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(logData)
        });
        
        if (response.ok) {
            showNotification('Food logged successfully!', 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('logFoodModal'));
            modal.hide();
            
            // Refresh stats
            loadUserStats();
        } else {
            showNotification('Failed to log food', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

function showFoodInfoModal(foodData) {
    // Add to specific recent views logic
    addToRecentlyViewed(foodData);

    const modalHtml = `
    <div class="modal fade" id="foodInfoModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">${foodData.name} Details</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="text-center mb-3">
                        <span class="badge bg-primary me-2">${foodData.category}</span>
                        <span class="badge bg-secondary">${foodData.meal_suitability}</span>
                    </div>
                    
                    <h6 class="border-bottom pb-2">Nutritional Information (per serving)</h6>
                    <div class="row text-center mb-3">
                        <div class="col-3">
                            <div class="h4 text-primary mb-0">${Math.round(foodData.calories)}</div>
                            <small class="text-muted">Calories</small>
                        </div>
                        <div class="col-3">
                            <div class="h4 text-success mb-0">${Math.round(foodData.protein)}g</div>
                            <small class="text-muted">Protein</small>
                        </div>
                        <div class="col-3">
                            <div class="h4 text-warning mb-0">${Math.round(foodData.carbs)}g</div>
                            <small class="text-muted">Carbs</small>
                        </div>
                        <div class="col-3">
                            <div class="h4 text-danger mb-0">${Math.round(foodData.fat)}g</div>
                            <small class="text-muted">Fat</small>
                        </div>
                    </div>
                    
                    <div class="alert alert-light border">
                        <p class="mb-0"><strong>Health Score:</strong> ${(foodData.health_score || foodData.score || 0).toFixed(1)}/10</p>
                    </div>
                    
                    ${foodData.description ? `<p class="mt-3">${foodData.description}</p>` : ''}
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary" onclick="triggerLogFoodFromInfo()">
                        Log This Food
                    </button>
                </div>
            </div>
        </div>
    </div>
    `;

    const existingModal = document.getElementById('foodInfoModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Store data for the button
    window.currentFoodInfoIdx = foodData;
    
    const modal = new bootstrap.Modal(document.getElementById('foodInfoModal'));
    modal.show();
}

// Helper to bridge the gap without messy inline JSON
window.triggerLogFoodFromInfo = function() {
    const modalEl = document.getElementById('foodInfoModal');
    const modal = bootstrap.Modal.getInstance(modalEl);
    modal.hide();
    if (window.currentFoodInfoIdx) {
        showLogFoodModal(window.currentFoodInfoIdx);
    }
};

window.toggleFavorite = async function(btnElement) {
    const foodName = btnElement.dataset.name;
    const icon = btnElement.querySelector('i');
    
    // Optimistic UI update
    const isSaved = icon.classList.contains('fas'); // filled heart
    
    if (isSaved) {
        icon.classList.remove('fas', 'text-danger');
        icon.classList.add('far');
        btnElement.classList.remove('btn-danger', 'text-white');
        btnElement.classList.add('btn-outline-danger');
    } else {
        icon.classList.remove('far');
        icon.classList.add('fas', 'text-danger'); // Add text-danger to icon, or btn-danger to button
        // Actually, if we use btn-danger, text is white.
        // Let's stick to btn-outline style mostly to avoid clash with Log button
        btnElement.classList.remove('btn-outline-danger');
        btnElement.classList.add('btn-danger', 'text-white');
        icon.classList.remove('text-danger'); // remove text-danger if button is solid red
    }
    
    try {
        const response = await fetch('/toggle_favorite', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ food_name: foodName })
        });
        
        const data = await response.json();
        if (!response.ok) {
            showNotification('Failed to update favorites', 'error');
            // Revert would go here
        } else {
            showNotification(data.message, 'success');
            // Refresh favorites list if we are on the recommendations page
            loadFavorites();
        }
    } catch (error) {
        showNotification('Network error', 'error');
    }
};

// Meal plan functions
function setupMealPlanGeneration() {
    const generateBtn = document.getElementById('generateMealPlan') || document.getElementById('generateNewPlan');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateMealPlan);
    }
}

async function generateMealPlan() {
    try {
        // Check for custom duration input, default to 7
        const durationEl = document.getElementById('planDuration');
        const days = durationEl ? parseInt(durationEl.value) : 7;

        // Get optional inputs if they exist (dashboard might not have them)
        const calorieEl = document.getElementById('calorieTarget');
        const dietEl = document.getElementById('dietType');
        
        const payload = { days: days };
        if (calorieEl) payload.calorie_target = parseInt(calorieEl.value);
        if (dietEl) payload.diet_type = dietEl.value;
        
        // Handle both container IDs for loading
        const containerId = document.getElementById('mealPlanArea') ? 'mealPlanArea' : 'mealPlanContainer';
        showLoading(containerId, 'Generating your personalized meal plan...');
        
        const response = await fetch('/generate_meal_plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayMealPlan(data.meal_plan);
            if (data.nutrition_summary) {
                updateNutritionSummary(data.nutrition_summary);
            }
            // Generate grocery list
            generateGroceryList(data.meal_plan);
        } else {
            showNotification('Failed to generate meal plan', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

function updateNutritionSummary(summary) {
    const container = document.getElementById('nutritionSummary');
    if (!container) return;
    
    container.innerHTML = `
        <div class="row text-center">
            <div class="col-6 mb-3">
                <div class="h3 text-primary mb-0">${Math.round(summary.avg_calories)}</div>
                <small class="text-muted">Avg Calories</small>
            </div>
            <div class="col-6 mb-3">
                <div class="h3 text-success mb-0">${Math.round(summary.avg_protein)}g</div>
                <small class="text-muted">Avg Protein</small>
            </div>
            <div class="col-6">
                <div class="h3 text-warning mb-0">${Math.round(summary.avg_carbs)}g</div>
                <small class="text-muted">Avg Carbs</small>
            </div>
            <div class="col-6">
                <div class="h3 text-danger mb-0">${Math.round(summary.avg_fat)}g</div>
                <small class="text-muted">Avg Fat</small>
            </div>
        </div>
        <hr>
        <div class="text-center">
            <small class="text-muted">Total Calories for Period</small>
            <div class="h4 text-dark">${Math.round(summary.total_calories)}</div>
        </div>
    `;
}

function displayMealPlan(mealPlan) {
    const container = document.getElementById('mealPlanArea') || document.getElementById('mealPlanContainer');
    if (!container) return;
    
    let html = '<div class="row">';
    const dayPlansData = {}; // Store plan data for event listeners
    
    Object.keys(mealPlan).forEach(day => {
        const dayPlan = mealPlan[day];
        dayPlansData[day] = dayPlan;
        
        let dayCalories = 0, dayProtein = 0, dayCarbs = 0, dayFat = 0;
        
        // Calculate totals for the day card
        Object.values(dayPlan).forEach(m => {
            dayCalories += m.calories || 0;
            dayProtein += m.protein || 0;
            dayCarbs += m.carbs || 0;
            dayFat += m.fat || 0;
        });
        
        html += `
        <div class="col-lg-6 mb-4">
            <div class="card h-100 shadow-sm">
                <div class="card-header bg-white d-flex justify-content-between align-items-center py-3">
                    <h5 class="mb-0 text-primary fw-bold">${day}</h5>
                    <span class="badge bg-light text-dark border">${Math.round(dayCalories)} kcal</span>
                </div>
                <div class="card-body">
                    <div class="meals-list">
        `;
        
        ['breakfast', 'lunch', 'dinner', 'snack'].forEach(type => {
            if(dayPlan[type]) {
                const meal = dayPlan[type];
                html += `
                <div class="meal-item border-bottom pb-2 mb-2 last-no-border">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <small class="text-uppercase text-muted fw-bold" style="font-size: 0.7rem;">${type}</small>
                        <small class="text-muted">${Math.round(meal.calories)} cal</small>
                    </div>
                    <div class="fw-bold text-dark mb-1">${meal.name}</div>
                    <div class="d-flex gap-2 small">
                        <span class="text-success">P: ${Math.round(meal.protein)}g</span>
                        <span class="text-warning">C: ${Math.round(meal.carbs)}g</span>
                        <span class="text-danger">F: ${Math.round(meal.fat)}g</span>
                    </div>
                </div>
                `;
            }
        });
        
        html += `
                    </div>
                </div>
                <div class="card-footer bg-light d-flex justify-content-between">
                     <button class="btn btn-sm btn-outline-info view-day-details" data-day="${day}">
                        <i class="fas fa-list me-1"></i> Details
                    </button>
                    <button class="btn btn-sm btn-outline-primary save-day-plan" data-day="${day}">
                        <i class="fas fa-save me-1"></i> Save Day
                    </button>
                </div>
            </div>
        </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
    
    // Attach event listeners
    container.querySelectorAll('.save-day-plan').forEach(button => {
        button.addEventListener('click', function() {
            const day = this.dataset.day;
            saveDayPlan(day, dayPlansData[day]);
        });
    });
    
    container.querySelectorAll('.view-day-details').forEach(button => {
        button.addEventListener('click', function() {
            const day = this.dataset.day;
            showDayDetailsModal(day, dayPlansData[day]);
        });
    });
}

function showDayDetailsModal(day, plan) {
    // Construct simplified list for modal
    let detailsHtml = '<div class="list-group">';
    ['breakfast', 'lunch', 'dinner', 'snack'].forEach(type => {
        if(plan[type]) {
             const m = plan[type];
             detailsHtml += `
                <div class="list-group-item">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1 text-capitalize">${type}</h6>
                        <small>${Math.round(m.calories)} kcal</small>
                    </div>
                    <p class="mb-1 fw-bold">${m.name}</p>
                    <div class="small text-muted">
                        Protein: ${Math.round(m.protein)}g | Carbs: ${Math.round(m.carbs)}g | Fat: ${Math.round(m.fat)}g
                    </div>
                    ${m.description ? `<small class="text-muted mt-1 d-block">${m.description}</small>` : ''}
                </div>
             `;
        }
    });
    detailsHtml += '</div>';

    const modalHtml = `
    <div class="modal fade" id="dayDetailsModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">${day} Breakdown</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    ${detailsHtml}
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    </div>
    `;
    
    const existing = document.getElementById('dayDetailsModal');
    if (existing) existing.remove();
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('dayDetailsModal'));
    modal.show();
}

async function saveDayPlan(day, plan) {
    try {
        if (!confirm(`Are you sure you want to log all meals for ${day}?`)) {
            return;
        }

        const response = await fetch('/save_day_plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                day: day,
                plan: plan
            })
        });
        
        if (response.ok) {
            showNotification(`All meals for ${day} logged successfully!`, 'success');
            loadUserStats(); // Refresh stats
        } else {
            showNotification('Failed to save meal plan', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

function generateGroceryList(mealPlan) {
    const container = document.getElementById('groceryList');
    if (!container || !mealPlan) return;
    
    // Simulate grocery list generation
    const groceries = [
        { name: 'Chicken Breast', quantity: '500g', category: 'Protein' },
        { name: 'Brown Rice', quantity: '1kg', category: 'Grains' },
        { name: 'Broccoli', quantity: '3 heads', category: 'Vegetables' },
        { name: 'Eggs', quantity: '12 pieces', category: 'Dairy' },
        { name: 'Olive Oil', quantity: '500ml', category: 'Oils' },
        { name: 'Mixed Berries', quantity: '500g', category: 'Fruits' },
        { name: 'Greek Yogurt', quantity: '1kg', category: 'Dairy' },
        { name: 'Almonds', quantity: '200g', category: 'Nuts' }
    ];
    
    // Group by category
    const grouped = {};
    groceries.forEach(item => {
        if (!grouped[item.category]) {
            grouped[item.category] = [];
        }
        grouped[item.category].push(item);
    });
    
    let html = '<div class="grocery-list">';
    
    Object.keys(grouped).forEach(category => {
        html += `<h6 class="mt-3 text-primary border-bottom pb-1">${category}</h6><ul class="list-unstyled">`;
        grouped[category].forEach(item => {
            const id = `grocery-${item.name.replace(/\s+/g, '-')}`;
            html += `
            <li class="d-flex justify-content-between align-items-center mb-2">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="${id}">
                    <label class="form-check-label" for="${id}">
                        ${item.name}
                    </label>
                </div>
                <span class="badge bg-light text-dark border">${item.quantity}</span>
            </li>
            `;
        });
        html += '</ul>';
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// Stub functions for non-existent endpoints (prevent console errors)
async function saveMealPlan() {
    showNotification('Save Meal Plan feature coming soon!', 'info');
}

async function loadSavedMealPlan() {
    // console.log('Load saved meal plan not implemented yet');
}

function exportGroceryList() {
    const listItems = document.querySelectorAll('.grocery-list li');
    if (listItems.length === 0) {
        showNotification('Generate a meal plan first', 'warning');
        return;
    }
    
    let text = 'Grocery List\n\n';
    document.querySelectorAll('.grocery-list h6').forEach(heading => {
        text += `${heading.textContent}\n`;
        let sibling = heading.nextElementSibling;
        if (sibling && sibling.tagName === 'UL') {
            sibling.querySelectorAll('li').forEach(li => {
                const name = li.querySelector('label').textContent.trim();
                const qty = li.querySelector('.badge').textContent.trim();
                text += `- ${name} (${qty})\n`;
            });
        }
        text += '\n';
    });
    
    const blob = new Blob([text], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'grocery-list.txt';
    a.click();
}

function createMacroChart(summary) {
    const ctx = document.getElementById('macroChart');
    if (!ctx) return;
    
    if (window.macroChartInstance) {
        window.macroChartInstance.destroy();
    }

    const protein = summary ? summary.avg_protein : 30;
    const carbs = summary ? summary.avg_carbs : 50;
    const fat = summary ? summary.avg_fat : 20;

    window.macroChartInstance = new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: ['Protein', 'Carbs', 'Fat'],
            datasets: [{
                data: [protein, carbs, fat],
                backgroundColor: [
                    '#198754', // success
                    '#ffc107', // warning
                    '#dc3545'  // danger
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                         usePointStyle: true,
                         padding: 20
                    }
                }
            },
            cutout: '70%'
        }
    });
}

// Profile update functions
function setupProfileUpdate() {
    const updateBtn = document.getElementById('updateProfileBtn');
    if (updateBtn) {
        updateBtn.addEventListener('click', updateProfile);
    }
}

async function updateProfile() {
    const formData = {
        weight: parseFloat(document.getElementById('currentWeight').value),
        height: parseFloat(document.getElementById('currentHeight').value),
        activity_level: document.getElementById('currentActivity').value,
        dietary_goal: document.getElementById('currentGoal').value
    };
    
    try {
        const response = await fetch('/update_profile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            showNotification('Profile updated successfully!', 'success');
            // Refresh stats
            loadUserStats();
        } else {
            showNotification('Failed to update profile', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    }
}

// Utility functions
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notif => notif.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification alert alert-${type === 'error' ? 'danger' : type}`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    
    // Add styles for notification
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function showLoading(elementId, message = 'Loading...') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3">${message}</p>
        </div>
        `;
    }
}

function getSelectedCheckboxes(name) {
    const checkboxes = document.querySelectorAll(`input[name="${name}"]:checked`);
    return Array.from(checkboxes).map(cb => cb.value);
}

// Chart functions
function initializeCharts() {
    // This would initialize charts on the dashboard
    // For now, we'll create a simple nutrition chart
    const ctx = document.getElementById('nutritionChart');
    if (ctx) {
        createNutritionChart(ctx);
    }
}

function createNutritionChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    // Sample data - in a real app, this would come from the backend
    const data = {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [
            {
                label: 'Calories',
                data: [2100, 2200, 1900, 2300, 2000, 2500, 1800],
                borderColor: '#E74C3C',
                backgroundColor: 'rgba(231, 76, 60, 0.1)',
                tension: 0.4
            },
            {
                label: 'Protein (g)',
                data: [75, 80, 70, 85, 75, 90, 65],
                borderColor: '#4CAF50',
                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                tension: 0.4
            }
        ]
    };
    
    new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Weekly Nutrition Intake'
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}