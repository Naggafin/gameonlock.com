export default function createSharedSSE(url, { onMessage, onForbidden } = {}) {
    const worker = new SharedWorker('./sse-worker.js');
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