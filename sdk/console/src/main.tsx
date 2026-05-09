//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import React from 'react';
import ReactDOM from 'react-dom/client';

import './app.css';
import App from './App';

const root = document.getElementById('app-root');

if (!root) {
	throw new Error('Missing #app-root');
}

ReactDOM.createRoot(root).render(
	<React.StrictMode>
		<App />
	</React.StrictMode>
);

