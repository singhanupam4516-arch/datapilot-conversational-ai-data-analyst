/**
 * Small hand-written inline SVG icons, replacing an icon library dependency.
 * Every icon takes `size` (pixels, default 16) and `className`; strokes use
 * `currentColor` so color is controlled from outside via CSS.
 */

function base(size) {
  return {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 2,
    strokeLinecap: "round",
    strokeLinejoin: "round",
  };
}

export function UploadIcon({ size = 16, className }) {
  return (
    <svg {...base(size)} className={className}>
      <path d="M12 3v12" />
      <path d="M7 8l5-5 5 5" />
      <path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" />
    </svg>
  );
}

export function UploadCloudIcon({ size = 16, className }) {
  return (
    <svg {...base(size)} className={className}>
      <path d="M7.5 17.5a4.5 4.5 0 0 1-1-8.9 5.5 5.5 0 0 1 10.7-1.9A4.5 4.5 0 0 1 17 17.5" />
      <path d="M12 12v7" />
      <path d="M9 15l3-3 3 3" />
    </svg>
  );
}

export function BarChartIcon({ size = 16, className }) {
  return (
    <svg {...base(size)} className={className}>
      <line x1="12" y1="20" x2="12" y2="10" />
      <line x1="18" y1="20" x2="18" y2="4" />
      <line x1="6" y1="20" x2="6" y2="16" />
    </svg>
  );
}

export function MessageSquareIcon({ size = 16, className }) {
  return (
    <svg {...base(size)} className={className}>
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  );
}

export function DatabaseIcon({ size = 16, className }) {
  return (
    <svg {...base(size)} className={className}>
      <ellipse cx="12" cy="5" rx="8" ry="3" />
      <path d="M4 5v14c0 1.66 3.58 3 8 3s8-1.34 8-3V5" />
      <path d="M4 12c0 1.66 3.58 3 8 3s8-1.34 8-3" />
    </svg>
  );
}

export function SendIcon({ size = 16, className }) {
  return (
    <svg {...base(size)} className={className}>
      <path d="M22 2L11 13" />
      <path d="M22 2l-7 20-4-9-9-4z" />
    </svg>
  );
}

export function LoaderIcon({ size = 16, className }) {
  return (
    <svg {...base(size)} className={className}>
      <line x1="12" y1="2" x2="12" y2="6" />
      <line x1="12" y1="18" x2="12" y2="22" />
      <line x1="4.9" y1="4.9" x2="7.8" y2="7.8" />
      <line x1="16.2" y1="16.2" x2="19.1" y2="19.1" />
      <line x1="2" y1="12" x2="6" y2="12" />
      <line x1="18" y1="12" x2="22" y2="12" />
      <line x1="4.9" y1="19.1" x2="7.8" y2="16.2" />
      <line x1="16.2" y1="7.8" x2="19.1" y2="4.9" />
    </svg>
  );
}

export function SparklesIcon({ size = 16, className }) {
  return (
    <svg {...base(size)} className={className}>
      <path d="M12 3l1.6 4.8L18 9l-4.4 1.2L12 15l-1.6-4.8L6 9l4.4-1.2z" />
      <path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z" />
    </svg>
  );
}

export function UserIcon({ size = 16, className }) {
  return (
    <svg {...base(size)} className={className}>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21c0-4 3.6-7 8-7s8 3 8 7" />
    </svg>
  );
}

export function FileSpreadsheetIcon({ size = 16, className }) {
  return (
    <svg {...base(size)} className={className}>
      <path d="M6 2h9l5 5v13a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z" />
      <path d="M8 13h8" />
      <path d="M8 17h8" />
      <path d="M10 9h4" />
    </svg>
  );
}

export function ChevronRightIcon({ size = 16, className }) {
  return (
    <svg {...base(size)} className={className}>
      <path d="M9 6l6 6-6 6" />
    </svg>
  );
}

export function ChevronDownIcon({ size = 16, className }) {
  return (
    <svg {...base(size)} className={className}>
      <path d="M6 9l6 6 6-6" />
    </svg>
  );
}

export function CodeIcon({ size = 16, className }) {
  return (
    <svg {...base(size)} className={className}>
      <path d="M8 6L2 12l6 6" />
      <path d="M16 6l6 6-6 6" />
    </svg>
  );
}
