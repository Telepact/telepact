//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

import { useEffect, useMemo, useRef, useState, type CSSProperties, type ReactNode } from 'react';

type Position = 'top' | 'bottom' | 'left' | 'right';

export default function Tooltip(props: { text?: string; position?: Position; children: ReactNode }) {
	const text = props.text ?? '';
	const position = props.position ?? 'bottom';

	const [show, setShow] = useState(false);
	const [tooltipStyle, setTooltipStyle] = useState<CSSProperties>({});

	const tooltipEl = useRef<HTMLSpanElement | null>(null);
	const triggerEl = useRef<HTMLDivElement | null>(null);

	const hide = () => setShow(false);

	const computePosition = () => {
		if (!tooltipEl.current || !triggerEl.current) return;
		const rect = triggerEl.current.getBoundingClientRect();
		const tooltipRect = tooltipEl.current.getBoundingClientRect();
		let top = 0;
		let left = 0;

		switch (position) {
			case 'bottom':
				top = rect.bottom + window.scrollY + 8;
				left = rect.left + window.scrollX + rect.width / 2 - tooltipRect.width / 2;
				break;
			case 'left':
				top = rect.top + window.scrollY + rect.height / 2 - tooltipRect.height / 2;
				left = rect.left + window.scrollX - tooltipRect.width - 8;
				break;
			case 'right':
				top = rect.top + window.scrollY + rect.height / 2 - tooltipRect.height / 2;
				left = rect.right + window.scrollX + 8;
				break;
			default: // top
				top = rect.top + window.scrollY - tooltipRect.height - 8;
				left = rect.left + window.scrollX + rect.width / 2 - tooltipRect.width / 2;
		}

		setTooltipStyle({ top, left });
	};

	const handleEnter = () => {
		setShow(true);
		setTimeout(computePosition, 1);
	};

	useEffect(() => {
		window.addEventListener('scroll', hide, true);
		return () => {
			window.removeEventListener('scroll', hide, true);
		};
	}, []);

	const shouldRender = useMemo(() => show && text !== '', [show, text]);

	return (
		<div
			ref={triggerEl}
			className="relative"
			onMouseEnter={handleEnter}
			onMouseLeave={hide}
			onFocus={handleEnter}
			onBlur={hide}
		>
			{props.children}
			{shouldRender ? (
				<span
					ref={tooltipEl}
					className="fixed z-50 rounded bg-gray-900 px-3 py-2 text-sm text-white shadow-lg opacity-90 pointer-events-none transition-opacity duration-100 dark:bg-gray-900 dark:text-white"
					style={tooltipStyle}
					role="tooltip"
					aria-live="polite"
				>
					{text}
				</span>
			) : null}
		</div>
	);
}
