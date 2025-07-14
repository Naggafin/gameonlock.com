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

// Add primary event listeners after DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
	document.body.addEventListener('htmx:beforeSend', () => document.body.style.cursor = 'wait');

	addMultipleListeners(document, ['htmx:afterSwap', 'htmx:responseError', 'htmx:abort', 'htmx:timeout'], () => {
		document.body.style.cursor = 'auto';
	});

	// Initial handling of dynamic content
	handleDynamicContent({
		type: 'DOMContentLoaded'
	});

	// Add event listener for htmx:afterSwap
	document.addEventListener('htmx:afterSwap', handleDynamicContent);
});
