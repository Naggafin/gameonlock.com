let eventSource = null;
let ports = [];
let sseUrl = null;
let reconnectTimeout = null;
let isBlocked = false;

function broadcast(data) {
    ports.forEach(port => port.postMessage(data));
}

function connectSSE() {
    if (!sseUrl || isBlocked) return;

    if (eventSource) {
        eventSource.close();
    }

    eventSource = new EventSource(sseUrl);

    eventSource.onmessage = (e) => {
        broadcast({ type: 'message', data: e.data });
    };

    eventSource.onerror = async () => {
        eventSource.close();
        eventSource = null;

        // Check for 403
        try {
            const response = await fetch(sseUrl, {
                method: 'HEAD',
                credentials: 'same-origin'
            });

            if (response.status === 403) {
                isBlocked = true;
                broadcast({ type: 'forbidden' });
                return;
            }
        } catch (err) {
            console.warn('SSE HEAD check failed:', err);
        }

        // Try reconnect after delay
        reconnectTimeout = setTimeout(connectSSE, 5000);
    };
}

self.addEventListener('connect', (e) => {
    const port = e.ports[0];
    ports.push(port);

    port.onmessage = (event) => {
        const { type, url } = event.data;

        if (type === 'init') {
            if (!sseUrl) sseUrl = url;
            if (!eventSource && !isBlocked) connectSSE();
        }

        if (type === 'close') {
            eventSource?.close();
            eventSource = null;
        }
    };

    port.start();

    // Optionally, inform new client about block state
    if (isBlocked) {
        port.postMessage({ type: 'forbidden' });
    }
});