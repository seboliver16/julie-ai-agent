// Poll for updates every 5 seconds
const POLL_INTERVAL = 5000;

// Function to format timestamp
function formatTimestamp(timestamp) {
    return new Date(timestamp * 1000).toLocaleString();
}

// Function to create action card HTML
function createActionCard(action) {
    return `
        <div class="action-card">
            <span class="timestamp">${formatTimestamp(action.timestamp)}</span>
            <h3>${action.action_type}</h3>
            <pre class="details">${JSON.stringify(action.details, null, 2)}</pre>
        </div>
    `;
}

// Function to poll for updates
async function pollUpdates() {
    try {
        const response = await fetch(`/api/monitor/updates?since=${lastActionId}`);
        const newActions = await response.json();
        
        if (newActions.length > 0) {
            const feed = document.getElementById('actions-feed');
            newActions.forEach(action => {
                feed.insertAdjacentHTML('afterbegin', createActionCard(action));
            });
            window.lastActionId = newActions[newActions.length - 1].id;
        }
    } catch (error) {
        console.error('Error polling for updates:', error);
    }
}

// Start polling if we're on the monitor page
if (document.getElementById('actions-feed')) {
    setInterval(pollUpdates, POLL_INTERVAL);
}
