import type { ReactNode } from "react";

interface PanelProps {
  title: string;
  icon?: ReactNode;
  badge?: ReactNode;
  children: ReactNode;
  className?: string;
}

export default function Panel({ title, icon, badge, children, className = "" }: PanelProps) {
  return (
    <section className={`flex min-w-0 max-h-[34rem] min-h-[16rem] flex-col gold-border rounded-2xl shadow-gold lg:max-h-none lg:min-h-0 ${className}`}>
      <header className="flex items-center gap-2 border-b border-line px-4 py-3">
        {icon && <span className="text-gold drop-shadow-[0_0_4px_rgb(var(--gold)/0.45)]">{icon}</span>}
        <h2 className="text-sm font-semibold tracking-tight">{title}</h2>
        {badge && <span className="ml-auto">{badge}</span>}
      </header>
      <div className="min-h-0 flex-1 overflow-y-auto p-4">{children}</div>
    </section>
  );
}
