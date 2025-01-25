'use strict';

function addMultipleListeners(el, types, listener, options, useCapture) {
	types.forEach(type => el.addEventListener(type, listener, options, useCapture));
}

function handleDynamicContent(e) {
	const root = (e.type === 'htmx:afterSwap') ? e.detail.target : document;

	// Make all 'require-js' elements visible
	root.querySelectorAll('.require-js').forEach(elem => elem.classList.remove('require-js'));

	// Set indeterminate checkboxes
	root.querySelectorAll('input[type="checkbox"].form-checkbox-indeterminate').forEach(elem => elem.indeterminate = true);
}

function applyAutoCloseTo(elem) {
	const autoCloseTime = 10000;
	let autoCloseTimeout;

	const startAutoClose = () => {
		autoCloseTimeout = setTimeout(() => {
			elem.remove();
		}, autoCloseTime);
	};

	const stopAutoClose = () => {
		clearTimeout(autoCloseTimeout);
	};

	elem.addEventListener('mouseenter', stopAutoClose);
	elem.addEventListener('mouseleave', startAutoClose);

	startAutoClose();
}


// Add primary event listeners after DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
	document.body.addEventListener('showMessage', e => window.alert(e.detail.value));
	document.body.addEventListener('htmx:beforeSend', () => document.body.style.cursor = 'wait');

	addMultipleListeners(document, ['htmx:afterSwap', 'htmx:responseError', 'htmx:abort', 'htmx:timeout'], () => {
		document.body.style.cursor = 'auto';
		document.querySelectorAll('.alert-item').forEach((alert) => {
			applyAutoCloseTo(alert);
		});
	});

	// Initial handling of dynamic content
	handleDynamicContent({
		type: 'DOMContentLoaded'
	});

	// Add event listener for htmx:afterSwap
	document.addEventListener('htmx:afterSwap', handleDynamicContent);
});
