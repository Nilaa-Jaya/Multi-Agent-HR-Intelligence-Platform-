// SmartSupport AI - Frontend Application

class SmartSupportApp {
    constructor() {
        this.conversationId = null;
        this.sessionQueries = 0;
        this.totalResponseTime = 0;

        this.initializeElements();
        this.attachEventListeners();
        this.checkSystemHealth();
    }

    initializeElements() {
        // Form elements
        this.chatForm = document.getElementById('chatForm');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.charCount = document.getElementById('charCount');

        // Containers
        this.messagesContainer = document.getElementById('messagesContainer');
        this.analysisContent = document.getElementById('analysisContent');
        this.kbResults = document.getElementById('kbResults');
        this.loadingOverlay = document.getElementById('loadingOverlay');

        // Buttons
        this.exportBtn = document.getElementById('exportBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.toggleSidebarBtn = document.getElementById('toggleSidebar');

        // Stats
        this.totalQueriesEl = document.getElementById('totalQueries');
        this.avgTimeEl = document.getElementById('avgTime');
        this.sessionQueriesEl = document.getElementById('sessionQueries');

        // User settings
        this.userIdInput = document.getElementById('userId');
    }

    attachEventListeners() {
        // Form submission
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        // Input handling
        this.messageInput.addEventListener('input', (e) => {
            this.updateCharCount();
            this.autoResize(e.target);
        });

        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Button clicks
        this.exportBtn.addEventListener('click', () => this.exportConversation());
        this.clearBtn.addEventListener('click', () => this.clearChat());
        this.toggleSidebarBtn.addEventListener('click', () => this.toggleSidebar());
    }

    updateCharCount() {
        const count = this.messageInput.value.length;
        this.charCount.textContent = count;

        if (count > 1800) {
            this.charCount.style.color = 'var(--danger-color)';
        } else {
            this.charCount.style.color = 'var(--text-muted)';
        }
    }

    autoResize(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();

        if (!message) return;

        // Disable input
        this.setInputEnabled(false);

        // Add user message to chat
        this.addMessage('user', message);

        // Clear input
        this.messageInput.value = '';
        this.updateCharCount();
        this.messageInput.style.height = 'auto';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send to API
            const response = await this.callAPI(message);

            // Remove typing indicator
            this.removeTypingIndicator();

            // Add assistant response
            this.addMessage('assistant', response.response, response);

            // Update analysis panel
            this.updateAnalysisPanel(response);

            // Update KB results
            this.updateKBResults(response.metadata.kb_results);

            // Update stats
            this.updateStats(response.metadata.processing_time);

        } catch (error) {
            this.removeTypingIndicator();
            this.showError('Failed to process your request. Please try again.');
            console.error('Error:', error);
        } finally {
            this.setInputEnabled(true);
            this.messageInput.focus();
        }
    }

    async callAPI(message) {
        const response = await fetch('/api/v1/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                user_id: this.userIdInput.value || 'web_user',
                conversation_id: this.conversationId
            })
        });

        if (!response.ok) {
            throw new Error('API request failed');
        }

        const data = await response.json();

        // Store conversation ID
        if (!this.conversationId) {
            this.conversationId = data.conversation_id;
        }

        return data;
    }

    addMessage(type, text, metadata = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = type === 'assistant'
            ? '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>'
            : '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>';

        const content = document.createElement('div');
        content.className = 'message-content';

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.innerHTML = `<p>${this.escapeHtml(text)}</p>`;

        content.appendChild(textDiv);

        // Add metadata badges for assistant messages
        if (type === 'assistant' && metadata) {
            const metadataDiv = document.createElement('div');
            metadataDiv.className = 'message-metadata';

            metadataDiv.innerHTML = `
                <span class="badge badge-category-${metadata.category.toLowerCase()}">${metadata.category}</span>
                <span class="badge badge-sentiment-${metadata.sentiment.toLowerCase()}">${metadata.sentiment}</span>
                <span class="badge badge-priority">Priority: ${metadata.priority}/10</span>
                ${metadata.metadata.escalated ? '<span class="badge badge-escalated">Escalated</span>' : ''}
            `;

            content.appendChild(metadataDiv);
        }

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);

        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'message assistant-message typing-indicator-message';
        indicator.id = 'typingIndicator';
        indicator.innerHTML = `
            <div class="message-avatar">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
            </div>
            <div class="message-content">
                <div class="message-text">
                    <div class="typing-indicator">
                        <span class="typing-dot"></span>
                        <span class="typing-dot"></span>
                        <span class="typing-dot"></span>
                    </div>
                </div>
            </div>
        `;
        this.messagesContainer.appendChild(indicator);
        this.scrollToBottom();
    }

    removeTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }

    updateAnalysisPanel(response) {
        const { category, sentiment, priority, metadata } = response;

        this.analysisContent.innerHTML = `
            <div class="analysis-item">
                <span class="analysis-label">Category</span>
                <div class="analysis-value">
                    <span class="badge badge-category-${category.toLowerCase()}">${category}</span>
                </div>
            </div>
            <div class="analysis-item">
                <span class="analysis-label">Sentiment</span>
                <div class="analysis-value">
                    <span class="badge badge-sentiment-${sentiment.toLowerCase()}">${sentiment}</span>
                </div>
            </div>
            <div class="analysis-item">
                <span class="analysis-label">Priority Score</span>
                <div class="analysis-value">
                    <span class="badge badge-priority">${priority} / 10</span>
                </div>
            </div>
            <div class="analysis-item">
                <span class="analysis-label">Processing Time</span>
                <div class="analysis-value">${metadata.processing_time.toFixed(2)}s</div>
            </div>
            ${metadata.escalated ? `
                <div class="analysis-item">
                    <span class="analysis-label">Escalation</span>
                    <div class="analysis-value">
                        <span class="badge badge-escalated">Escalated</span>
                        <p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">
                            ${metadata.escalation_reason}
                        </p>
                    </div>
                </div>
            ` : ''}
        `;
    }

    updateKBResults(results) {
        if (!results || results.length === 0) {
            this.kbResults.innerHTML = '<p class="placeholder-text">No KB articles found</p>';
            return;
        }

        this.kbResults.innerHTML = results.map((result, index) => {
            const scoreClass = result.score >= 0.8 ? 'score-high' :
                              result.score >= 0.6 ? 'score-medium' : 'score-low';

            return `
                <div class="kb-result" data-index="${index}">
                    <div class="kb-result-header">
                        <div class="kb-result-title">${this.escapeHtml(result.title)}</div>
                        <div class="kb-result-score ${scoreClass}">${(result.score * 100).toFixed(1)}%</div>
                    </div>
                    <div class="kb-result-category">${result.category}</div>
                    <div class="kb-result-content">${this.escapeHtml(result.content)}</div>
                </div>
            `;
        }).join('');

        // Add click handlers to expand/collapse
        this.kbResults.querySelectorAll('.kb-result').forEach(el => {
            el.addEventListener('click', () => {
                el.classList.toggle('expanded');
            });
        });
    }

    updateStats(processingTime) {
        this.sessionQueries++;
        this.totalResponseTime += processingTime;

        this.sessionQueriesEl.textContent = this.sessionQueries;
        this.avgTimeEl.textContent = (this.totalResponseTime / this.sessionQueries).toFixed(2) + 's';
    }

    async checkSystemHealth() {
        try {
            const response = await fetch('/api/v1/health');
            const data = await response.json();

            const statusEl = document.getElementById('systemStatus');
            if (data.status === 'healthy') {
                statusEl.textContent = 'System Online';
                statusEl.previousElementSibling.classList.add('online');
            } else {
                statusEl.textContent = 'System Offline';
                statusEl.previousElementSibling.classList.remove('online');
            }
        } catch (error) {
            console.error('Health check failed:', error);
        }
    }

    exportConversation() {
        const messages = Array.from(this.messagesContainer.querySelectorAll('.message')).map(msg => {
            const isAssistant = msg.classList.contains('assistant-message');
            return {
                role: isAssistant ? 'assistant' : 'user',
                content: msg.querySelector('.message-text p').textContent
            };
        });

        const data = {
            conversation_id: this.conversationId,
            user_id: this.userIdInput.value,
            messages: messages,
            timestamp: new Date().toISOString()
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `conversation_${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    clearChat() {
        if (confirm('Are you sure you want to clear the conversation?')) {
            // Remove all messages except welcome message
            const messages = this.messagesContainer.querySelectorAll('.message');
            messages.forEach((msg, index) => {
                if (index > 0) msg.remove();
            });

            // Reset conversation ID
            this.conversationId = null;

            // Clear analysis panel
            this.analysisContent.innerHTML = `
                <div class="analysis-placeholder">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 16V8a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2z"></path>
                        <polyline points="7 11 12 16 17 11"></polyline>
                        <line x1="12" y1="16" x2="12" y2="8"></line>
                    </svg>
                    <p>Send a message to see analysis</p>
                </div>
            `;

            // Clear KB results
            this.kbResults.innerHTML = '<p class="placeholder-text">KB articles will appear here</p>';
        }
    }

    toggleSidebar() {
        document.querySelector('.sidebar').classList.toggle('open');
    }

    setInputEnabled(enabled) {
        this.messageInput.disabled = !enabled;
        this.sendBtn.disabled = !enabled;
    }

    showError(message) {
        this.addMessage('assistant', `Error: ${message}`);
    }

    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new SmartSupportApp();
});
