// Toggle elements
function toggleElement(elementId) {
    const element = document.getElementById(elementId);
    if (element.style.display === "none") {
        element.style.display = "block";
    } else {
        element.style.display = "none";
    }
}

// Chat functionality
document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && chatInput.value.trim() !== '') {
                sendMessage(chatInput.value);
                chatInput.value = '';
            }
        });
    }
    
    function sendMessage(message) {
        // This would communicate with Streamlit backend
        const msgDiv = document.createElement('div');
        msgDiv.className = 'user-message';
        msgDiv.textContent = message;
        chatMessages.appendChild(msgDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // In a real app, you would send this to Streamlit
        // parent.postMessage({type: 'CHAT_MESSAGE', content: message}, '*');
    }
});

// Tooltip initialization
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(tip => {
        tip.addEventListener('mouseenter', showTooltip);
        tip.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = this.getAttribute('data-tooltip');
    document.body.appendChild(tooltip);
    
    const rect = this.getBoundingClientRect();
    tooltip.style.left = `${rect.left + rect.width/2 - tooltip.offsetWidth/2}px`;
    tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
}

function hideTooltip() {
    const tooltip = document.querySelector('.tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}