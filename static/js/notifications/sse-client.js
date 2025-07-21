function getSharedWorkerPath() {
    const config = document.querySelector('[data-sse-worker]');
    const path = config?.dataset?.sseWorker || JSON.parse(config?.textContent || '{}')?.sseWorkerPath;
    if (!path) throw new Error("Missing SSE worker path");
    return path;
}


export default function createSharedSSE(url, { onMessage, onForbidden } = {}) {
    const worker = new SharedWorker(getSharedWorkerPath());
    worker.port.start();

    worker.port.postMessage({ type: 'init', url });

    worker.port.onmessage = (e) => {
        const { type, data } = e.data;

        if (type === 'message' && onMessage) {
            onMessage(data);
        }

        if (type === 'forbidden' && onForbidden) {
            onForbidden();
        }
    };

    return {
        close() {
            worker.port.postMessage({ type: 'close' });
        }
    };
}