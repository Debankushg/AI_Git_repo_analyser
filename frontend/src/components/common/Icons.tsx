import type { ReactNode } from "react";

interface IconProps {
  className?: string;
}

const base = (children: ReactNode, className = "h-4 w-4") => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden>
    {children}
  </svg>
);

export const SunIcon = (p: IconProps) => base(<><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></>, p.className);
export const MoonIcon = (p: IconProps) => base(<path d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z" />, p.className);
export const FolderIcon = (p: IconProps) => base(<path d="M3 7a2 2 0 012-2h4l2 2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" />, p.className);
export const FileIcon = (p: IconProps) => base(<><path d="M14 3H7a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8z" /><path d="M14 3v5h5" /></>, p.className);
export const SendIcon = (p: IconProps) => base(<path d="M22 2L11 13M22 2l-7 20-4-9-9-4z" />, p.className);
export const SparkIcon = (p: IconProps) => base(<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9zM19 16l.8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8z" />, p.className);
export const BugIcon = (p: IconProps) => base(<><circle cx="12" cy="12" r="9" /><path d="M12 8v5M12 16h.01" /></>, p.className);
export const PullIcon = (p: IconProps) => base(<><circle cx="6" cy="6" r="2" /><circle cx="6" cy="18" r="2" /><circle cx="18" cy="18" r="2" /><path d="M6 8v8M18 16V9a3 3 0 00-3-3h-3m0 0l2-2m-2 2l2 2" /></>, p.className);
export const ShieldIcon = (p: IconProps) => base(<><path d="M12 3l8 3v6c0 4.5-3.2 8-8 9-4.8-1-8-4.5-8-9V6z" /><path d="M9 12l2 2 4-4" /></>, p.className);
export const ArrowLeftIcon = (p: IconProps) => base(<path d="M19 12H5m6-6l-6 6 6 6" />, p.className);
export const AlertIcon = (p: IconProps) => base(<><path d="M12 3L2 20h20z" /><path d="M12 10v4M12 17h.01" /></>, p.className);
export const ClockIcon = (p: IconProps) => base(<><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>, p.className);
export const WifiOffIcon = (p: IconProps) => base(<><path d="M2 2l20 20M8.5 16.4a5 5 0 017 0M5 12.9a10 10 0 015-2.6M2 8.8a15 15 0 014-2.8M12 20h.01" /></>, p.className);
export const RefreshIcon = (p: IconProps) => base(<path d="M21 12a9 9 0 01-15.5 6.2M3 12A9 9 0 0118.5 5.800M21 4v5h-5M3 20v-5h5" />, p.className);
export const XIcon = (p: IconProps) => base(<path d="M18 6L6 18M6 6l12 12" />, p.className);
export const CommitIcon = (p: IconProps) => base(<><circle cx="12" cy="12" r="3.5" /><path d="M3 12h5.5M15.5 12H21" /></>, p.className);
export const ApiIcon = (p: IconProps) => base(<path d="M8 6l-5 6 5 6M16 6l5 6-5 6M14 4l-4 16" />, p.className);
export const LinkIcon = (p: IconProps) => base(<path d="M10 13a5 5 0 007 0l3-3a5 5 0 00-7-7l-1 1M14 11a5 5 0 00-7 0l-3 3a5 5 0 007 7l1-1" />, p.className);
export const StarIcon = (p: IconProps) => base(<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.900 1-6.100L3.200 9.500l6.100-.9z" />, p.className);
export const ForkIcon = (p: IconProps) => base(<><circle cx="6" cy="5" r="2" /><circle cx="18" cy="5" r="2" /><circle cx="12" cy="19" r="2" /><path d="M6 7v2a3 3 0 003 3h6a3 3 0 003-3V7M12 12v5" /></>, p.className);
export const BranchIcon = (p: IconProps) => base(<><circle cx="6" cy="5" r="2" /><circle cx="6" cy="19" r="2" /><circle cx="18" cy="8" r="2" /><path d="M6 7v10M18 10c0 4-6 3-12 7" /></>, p.className);
export const LockIcon = (p: IconProps) => base(<><rect x="5" y="11" width="14" height="10" rx="2" /><path d="M8 11V7a4 4 0 018 0v4" /></>, p.className);
