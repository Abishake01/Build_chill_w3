// LazAI Intelligence Hub - Enhanced JavaScript
class LazAIApp {
  constructor() {
    this.currentFileId = 2346;
    this.queryHistory = [];
    this.analytics = {
      totalQueries: 0,
      responseTimes: [],
      queryCategories: {}
    };
    this.chart = null;
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.initializeChart();
    this.loadQueryHistory();
    this.updateAnalytics();
  }

  setupEventListeners() {
    // Chat functionality
    const chatInput = document.getElementById('chatInput');
    const sendMessage = document.getElementById('sendMessage');
    
    chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.sendChatMessage();
      }
    });
    
    sendMessage.addEventListener('click', () => this.sendChatMessage());

    // File management
    document.getElementById('addFile').addEventListener('click', () => {
      document.getElementById('fileModal').classList.add('show');
    });

    document.getElementById('closeModal').addEventListener('click', () => {
      document.getElementById('fileModal').classList.remove('show');
    });

    document.getElementById('cancelUpload').addEventListener('click', () => {
      document.getElementById('fileModal').classList.remove('show');
    });

    document.getElementById('confirmUpload').addEventListener('click', () => {
      this.handleFileUpload();
    });

    // Quick actions
    document.querySelectorAll('.quick-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const query = e.currentTarget.dataset.query;
        this.sendQuery(query);
      });
    });

    // Suggestion buttons
    document.querySelectorAll('.suggestion-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const query = e.currentTarget.dataset.query;
        document.getElementById('chatInput').value = query;
        this.sendChatMessage();
      });
    });

    // Chat controls
    document.getElementById('clearChat').addEventListener('click', () => {
      this.clearChat();
    });

    document.getElementById('exportChat').addEventListener('click', () => {
      this.exportChat();
    });

    // File selection
    document.querySelectorAll('.file-item').forEach(item => {
      item.addEventListener('click', (e) => {
        document.querySelectorAll('.file-item').forEach(f => f.classList.remove('active'));
        e.currentTarget.classList.add('active');
        this.currentFileId = e.currentTarget.dataset.fileId;
      });
    });

    // Query history
    document.querySelectorAll('.query-item').forEach(item => {
      item.addEventListener('click', (e) => {
        const query = e.currentTarget.textContent.trim();
        this.sendQuery(query);
      });
    });

    // Analytics refresh
    document.getElementById('refreshAnalytics').addEventListener('click', () => {
      this.updateAnalytics();
    });

    // Theme toggle
    document.getElementById('toggleTheme').addEventListener('click', () => {
      this.toggleTheme();
    });

    // New chat
    document.getElementById('newChat').addEventListener('click', () => {
      this.clearChat();
    });
  }

  async sendChatMessage() {
    const input = document.getElementById('chatInput');
    const query = input.value.trim();
    
    if (!query) return;

    // Add user message to chat
    this.addMessage(query, 'user');
    input.value = '';

    // Show loading
    this.showLoading();

    try {
      const startTime = Date.now();
      const response = await this.queryData(query);
      const responseTime = Date.now() - startTime;

      // Add AI response to chat
      this.addMessage(this.formatResponse(response), 'ai');
      
      // Update analytics
      this.updateQueryStats(responseTime);
      this.addToQueryHistory(query);
      
    } catch (error) {
      this.addMessage(`Error: ${error.message}`, 'ai');
    } finally {
      this.hideLoading();
    }
  }

  async sendQuery(query) {
    document.getElementById('chatInput').value = query;
    await this.sendChatMessage();
  }

  async queryData(query) {
    const payload = {
      file_id: this.currentFileId,
      query: query,
      limit: 3
    };

    try {
      const response = await fetch('/query/rag', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      
      // Check if it's an error response
      if (result.error) {
        throw new Error(result.error.message);
      }
      
      // Update analytics with successful query
      this.updateQueryAnalytics(query, 'rag', true);
      return result;
    } catch (error) {
      // Fallback to demo endpoint if RAG fails
      console.log('RAG query failed, trying demo endpoint:', error.message);
      this.updateQueryAnalytics(query, 'rag', false);
      return await this.queryDemoData(query);
    }
  }

  async queryDemoData(query) {
    const payload = {
      query: query
    };

    const response = await fetch('/demo/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  }

  addMessage(content, type) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = type === 'ai' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.innerHTML = `<p>${content}</p>`;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  formatResponse(response) {
    if (response.error) {
      return `❌ ${response.error.message}`;
    }
    
    if (response.data && response.data.length > 0) {
      return `📊 **Query Results:**\n\n${response.data.map((item, index) => 
        `${index + 1}. ${item}`
      ).join('\n\n')}`;
    }
    
    return 'No relevant data found for your query.';
  }

  showLoading() {
    document.getElementById('loadingOverlay').classList.add('show');
  }

  hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('show');
  }

  updateQueryStats(responseTime) {
    this.analytics.totalQueries++;
    this.analytics.responseTimes.push(responseTime);
    
    // Keep only last 100 response times
    if (this.analytics.responseTimes.length > 100) {
      this.analytics.responseTimes = this.analytics.responseTimes.slice(-100);
    }
    
    this.updateAnalytics();
  }

  updateQueryAnalytics(query, type, success) {
    // Categorize query based on keywords
    const queryLower = query.toLowerCase();
    let category = 'General';
    
    if (queryLower.includes('skill') || queryLower.includes('expertise') || queryLower.includes('know')) {
      category = 'Skills & Expertise';
    } else if (queryLower.includes('tech') || queryLower.includes('framework') || queryLower.includes('language')) {
      category = 'Technologies';
    } else if (queryLower.includes('interest') || queryLower.includes('passion') || queryLower.includes('love')) {
      category = 'Interests';
    }
    
    // Update analytics
    if (!this.analytics.queryCategories[category]) {
      this.analytics.queryCategories[category] = 0;
    }
    this.analytics.queryCategories[category]++;
    
    // Track success/failure
    if (!this.analytics.querySuccess) {
      this.analytics.querySuccess = { success: 0, failure: 0 };
    }
    
    if (success) {
      this.analytics.querySuccess.success++;
    } else {
      this.analytics.querySuccess.failure++;
    }
    
    this.updateAnalytics();
  }

  updateAnalytics() {
    // Update metrics
    document.getElementById('totalQueries').textContent = this.analytics.totalQueries;
    
    const avgResponseTime = this.analytics.responseTimes.length > 0 
      ? Math.round(this.analytics.responseTimes.reduce((a, b) => a + b, 0) / this.analytics.responseTimes.length)
      : 0;
    document.getElementById('avgResponseTime').textContent = `${avgResponseTime}ms`;
    
    // Update chart
    this.updateChart();
  }

  initializeChart() {
    const ctx = document.getElementById('queryChart').getContext('2d');
    this.chart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Skills & Expertise', 'Technologies', 'Interests', 'General'],
        datasets: [{
          data: [0, 0, 0, 0],
          backgroundColor: [
            '#4f7cff',
            '#10b981',
            '#f59e0b',
            '#6366f1'
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
              color: '#a3acc5',
              font: {
                size: 12
              }
            }
          }
        }
      }
    });
  }

  updateChart() {
    if (this.chart) {
      // Use real analytics data if available, otherwise use defaults
      const categories = this.analytics.queryCategories;
      const total = Object.values(categories).reduce((sum, count) => sum + count, 0);
      
      if (total > 0) {
        // Use real data
        this.chart.data.datasets[0].data = [
          categories['Skills & Expertise'] || 0,
          categories['Technologies'] || 0,
          categories['Interests'] || 0,
          categories['General'] || 0
        ];
      } else {
        // Use default distribution
        this.chart.data.datasets[0].data = [
          Math.floor(this.analytics.totalQueries * 0.4),
          Math.floor(this.analytics.totalQueries * 0.3),
          Math.floor(this.analytics.totalQueries * 0.2),
          Math.floor(this.analytics.totalQueries * 0.1)
        ];
      }
      
      this.chart.update();
    }
  }

  addToQueryHistory(query) {
    this.queryHistory.unshift(query);
    if (this.queryHistory.length > 10) {
      this.queryHistory = this.queryHistory.slice(0, 10);
    }
    this.updateQueryHistoryUI();
  }

  updateQueryHistoryUI() {
    const historyContainer = document.getElementById('queryHistory');
    historyContainer.innerHTML = this.queryHistory.map(query => `
      <div class="query-item">
        <i class="fas fa-search"></i>
        <span>${query}</span>
      </div>
    `).join('');
    
    // Re-attach event listeners
    historyContainer.querySelectorAll('.query-item').forEach(item => {
      item.addEventListener('click', (e) => {
        const query = e.currentTarget.textContent.trim();
        this.sendQuery(query);
      });
    });
  }

  loadQueryHistory() {
    const saved = localStorage.getItem('lazai_query_history');
    if (saved) {
      this.queryHistory = JSON.parse(saved);
      this.updateQueryHistoryUI();
    }
  }

  saveQueryHistory() {
    localStorage.setItem('lazai_query_history', JSON.stringify(this.queryHistory));
  }

  clearChat() {
    const messagesContainer = document.getElementById('chatMessages');
    messagesContainer.innerHTML = `
      <div class="message ai-message">
        <div class="message-avatar">
          <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
          <p>Hello! I'm your LazAI Data Assistant. I can help you analyze and query your encrypted data. What would you like to know?</p>
        </div>
      </div>
    `;
  }

  exportChat() {
    const messages = document.querySelectorAll('.message');
    const chatData = Array.from(messages).map(msg => {
      const isUser = msg.classList.contains('user-message');
      const content = msg.querySelector('.message-content p').textContent;
      return {
        type: isUser ? 'user' : 'ai',
        content: content,
        timestamp: new Date().toISOString()
      };
    });
    
    const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `lazai-chat-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  async handleFileUpload() {
    const fileUpload = document.getElementById('fileUpload');
    const textInput = document.getElementById('textInput');
    const urlInput = document.getElementById('urlInput');
    
    let content = '';
    let collection = 'user_uploaded';
    
    if (fileUpload.files.length > 0) {
      const file = fileUpload.files[0];
      content = await this.readFileAsText(file);
      collection = `file_${file.name.replace(/\.[^/.]+$/, '')}`;
    } else if (textInput.value.trim()) {
      content = textInput.value.trim();
      collection = 'pasted_text';
    } else if (urlInput.value.trim()) {
      // Handle URL upload
      this.addMessage('URL upload not yet implemented. Please use file upload or paste text.', 'ai');
      return;
    } else {
      this.addMessage('Please select a file, paste text, or enter a URL.', 'ai');
      return;
    }
    
    if (!content) {
      this.addMessage('No content provided.', 'ai');
      return;
    }
    
    // Use local query endpoint for uploaded content
    try {
      this.showLoading();
      const response = await fetch('/query/local', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: content,
          query: 'Summarize the main points',
          collection: collection
        })
      });
      
      const result = await response.json();
      this.addMessage(`✅ File uploaded successfully! Collection: ${collection}`, 'ai');
      
      // Add to file manager
      this.addFileToManager(collection, 'Uploaded File');
      
    } catch (error) {
      this.addMessage(`Error uploading file: ${error.message}`, 'ai');
    } finally {
      this.hideLoading();
      document.getElementById('fileModal').classList.remove('show');
    }
  }

  readFileAsText(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = e => resolve(e.target.result);
      reader.onerror = e => reject(e);
      reader.readAsText(file);
    });
  }

  addFileToManager(name, type) {
    const fileManager = document.querySelector('.file-manager');
    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';
    fileItem.dataset.fileId = Date.now();
    fileItem.innerHTML = `
      <i class="fas fa-file-alt"></i>
      <span>${name} (${type})</span>
    `;
    
    fileItem.addEventListener('click', (e) => {
      document.querySelectorAll('.file-item').forEach(f => f.classList.remove('active'));
      e.currentTarget.classList.add('active');
      this.currentFileId = e.currentTarget.dataset.fileId;
    });
    
    fileManager.insertBefore(fileItem, document.getElementById('addFile'));
  }

  toggleTheme() {
    // Simple theme toggle - could be expanded
    document.body.classList.toggle('light-theme');
    const themeIcon = document.querySelector('#toggleTheme i');
    themeIcon.classList.toggle('fa-moon');
    themeIcon.classList.toggle('fa-sun');
  }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.lazaiApp = new LazAIApp();
});

// Save query history on page unload
window.addEventListener('beforeunload', () => {
  if (window.lazaiApp) {
    window.lazaiApp.saveQueryHistory();
  }
});
