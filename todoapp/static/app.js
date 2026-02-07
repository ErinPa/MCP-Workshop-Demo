// API Base URL
const API_BASE = '/api';

// State
let currentFilters = {
    priority: '',
    completed: ''
};

// DOM Elements
const addTodoForm = document.getElementById('addTodoForm');
const todosList = document.getElementById('todosList');
const todoCount = document.getElementById('todoCount');
const editModal = document.getElementById('editModal');
const editTodoForm = document.getElementById('editTodoForm');
const closeModal = document.querySelector('.close');
const cancelEdit = document.getElementById('cancelEdit');
const filterPriority = document.getElementById('filterPriority');
const filterCompleted = document.getElementById('filterCompleted');
const applyFilters = document.getElementById('applyFilters');
const resetFilters = document.getElementById('resetFilters');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadTodos();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    addTodoForm.addEventListener('submit', handleAddTodo);
    editTodoForm.addEventListener('submit', handleEditTodo);
    closeModal.addEventListener('click', () => editModal.style.display = 'none');
    cancelEdit.addEventListener('click', () => editModal.style.display = 'none');
    applyFilters.addEventListener('click', handleApplyFilters);
    resetFilters.addEventListener('click', handleResetFilters);
    
    // Close modal on outside click
    window.addEventListener('click', (e) => {
        if (e.target === editModal) {
            editModal.style.display = 'none';
        }
    });
}

// API Calls
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API call failed');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        alert(`Error: ${error.message}`);
        throw error;
    }
}

// Load and Display Todos
async function loadTodos() {
    try {
        // Build query params
        const params = new URLSearchParams();
        if (currentFilters.priority) params.append('priority', currentFilters.priority);
        if (currentFilters.completed !== '') params.append('completed', currentFilters.completed);
        
        const queryString = params.toString();
        const endpoint = `/todos${queryString ? '?' + queryString : ''}`;
        
        const data = await apiCall(endpoint);
        displayTodos(data.todos, data.total);
    } catch (error) {
        todosList.innerHTML = '<div class="loading">Error loading todos</div>';
    }
}

function displayTodos(todos, total) {
    todoCount.textContent = `${total} todo${total !== 1 ? 's' : ''}`;
    
    if (todos.length === 0) {
        todosList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <h3>No todos found</h3>
                <p>Create your first todo to get started!</p>
            </div>
        `;
        return;
    }
    
    todosList.innerHTML = todos.map(todo => createTodoHTML(todo)).join('');
}

function createTodoHTML(todo) {
    const createdDate = new Date(todo.created_at).toLocaleString();
    const completedDate = todo.completed_at ? new Date(todo.completed_at).toLocaleString() : null;
    
    return `
        <div class="todo-item ${todo.completed ? 'completed' : ''} priority-${todo.priority}">
            <div class="todo-header">
                <div class="todo-title-section">
                    <div class="todo-title">${escapeHtml(todo.title)}</div>
                    <span class="todo-priority ${todo.priority}">${todo.priority}</span>
                </div>
            </div>
            ${todo.description ? `<div class="todo-description">${escapeHtml(todo.description)}</div>` : ''}
            <div class="todo-meta">
                <div>Created: ${createdDate}</div>
                ${completedDate ? `<div>Completed: ${completedDate}</div>` : ''}
            </div>
            <div class="todo-actions">
                ${!todo.completed ? `
                    <button class="btn btn-success" onclick="completeTodo(${todo.id})">
                        ✓ Complete
                    </button>
                    <button class="btn btn-warning" onclick="openEditModal(${todo.id})">
                        ✏️ Edit
                    </button>
                ` : ''}
                <button class="btn btn-danger" onclick="deleteTodo(${todo.id})">
                    🗑️ Delete
                </button>
            </div>
        </div>
    `;
}

// Add Todo
async function handleAddTodo(e) {
    e.preventDefault();
    
    const formData = new FormData(addTodoForm);
    const todoData = {
        title: formData.get('title'),
        description: formData.get('description') || null,
        priority: formData.get('priority')
    };
    
    try {
        await apiCall('/todos', {
            method: 'POST',
            body: JSON.stringify(todoData)
        });
        
        addTodoForm.reset();
        await loadTodos();
    } catch (error) {
        // Error already handled in apiCall
    }
}

// Edit Todo
async function openEditModal(todoId) {
    try {
        const todo = await apiCall(`/todos/${todoId}`);
        
        document.getElementById('editTodoId').value = todo.id;
        document.getElementById('editTitle').value = todo.title;
        document.getElementById('editDescription').value = todo.description || '';
        document.getElementById('editPriority').value = todo.priority;
        
        editModal.style.display = 'block';
    } catch (error) {
        // Error already handled in apiCall
    }
}

async function handleEditTodo(e) {
    e.preventDefault();
    
    const todoId = document.getElementById('editTodoId').value;
    const formData = new FormData(editTodoForm);
    const todoData = {
        title: formData.get('title'),
        description: formData.get('description') || null,
        priority: formData.get('priority')
    };
    
    try {
        await apiCall(`/todos/${todoId}`, {
            method: 'PUT',
            body: JSON.stringify(todoData)
        });
        
        editModal.style.display = 'none';
        await loadTodos();
    } catch (error) {
        // Error already handled in apiCall
    }
}

// Complete Todo
async function completeTodo(todoId) {
    try {
        await apiCall(`/todos/${todoId}/complete`, {
            method: 'PATCH'
        });
        
        await loadTodos();
    } catch (error) {
        // Error already handled in apiCall
    }
}

// Delete Todo
async function deleteTodo(todoId) {
    if (!confirm('Are you sure you want to delete this todo?')) {
        return;
    }
    
    try {
        await apiCall(`/todos/${todoId}`, {
            method: 'DELETE'
        });
        
        await loadTodos();
    } catch (error) {
        // Error already handled in apiCall
    }
}

// Filters
function handleApplyFilters() {
    currentFilters.priority = filterPriority.value;
    currentFilters.completed = filterCompleted.value;
    loadTodos();
}

function handleResetFilters() {
    filterPriority.value = '';
    filterCompleted.value = '';
    currentFilters = { priority: '', completed: '' };
    loadTodos();
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
