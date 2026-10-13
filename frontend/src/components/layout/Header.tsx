import type { ReactNode } from "react";
import ThemeToggle from "../common/ThemeToggle";

export default function Header({ children }: { children?: ReactNode }) {
  return (
    <header className="sticky top-0 z-10 flex flex-wrap items-center gap-3 border-b border-gold/40 bg-card/80 px-4 py-3 backdrop-blur sm:px-6">
      <div className="flex items-center gap-2.5">
        <div className="grid h-9 w-9 place-items-center rounded-xl gold-fill text-[#3b2a05] shadow-gold ring-1 ring-gold/40">
          <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden><circle cx="6" cy="6" r="2.2" /><circle cx="6" cy="18" r="2.2" /><circle cx="18" cy="12" r="2.2" /><path d="M6 8.2v7.6M8 6.8c6 .6 8 2.200 8 3.200" /></svg>
        </div>
        <div className="leading-tight">
          <h1 className="gold-text text-[15px] font-extrabold uppercase tracking-[0.14em]">GitHub Repo Assistant</h1>
          <p className="hidden text-[11px] text-muted sm:block">AI for any git codebase</p>
        </div>
      </div>
      <div className="ml-auto flex items-center gap-2">
        {children}
        <ThemeToggle />
      </div>
    </header>
  );
}
