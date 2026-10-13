import { describeError } from "../../utils/errorUtils";
import { AlertIcon, ClockIcon, RefreshIcon, WifiOffIcon, XIcon } from "./Icons";

interface Props {
  error: string;
  onRetry?: () => void;
  onDismiss?: () => void;
  className?: string;
}

const KIND = {
  "rate-limit": { Icon: ClockIcon, tone: "warn", anim: "" },
  network: { Icon: WifiOffIcon, tone: "danger", anim: "animate-shake" },
  "not-found": { Icon: AlertIcon, tone: "warn", anim: "" },
  server: { Icon: AlertIcon, tone: "danger", anim: "animate-shake" },
} as const;

const TONE = {
  warn: { box: "border-warn/40 bg-warn/10", bar: "bg-warn", icon: "bg-warn/15 text-warn", title: "text-warn" },
  danger: { box: "border-danger/40 bg-danger/10", bar: "bg-danger", icon: "bg-danger/15 text-danger", title: "text-danger" },
};

export default function ErrorAlert({ error, onRetry, onDismiss, className = "" }: Props) {
  const info = describeError(error);
  const { Icon, tone, anim } = KIND[info.kind];
  const t = TONE[tone];

  return (
    <div role="alert" className={`animate-fade-up ${className}`}>
      <div className={`relative flex gap-3 overflow-hidden rounded-xl border p-3 pl-4 shadow-card ${t.box} ${anim}`}>
        <span className={`absolute inset-y-0 left-0 w-1 ${t.bar}`} />
        <span className={`grid h-9 w-9 shrink-0 place-items-center rounded-full ${t.icon}`}>
          <Icon className="h-[18px] w-[18px]" />
        </span>
        <div className="min-w-0 flex-1">
          <p className={`text-sm font-semibold ${t.title}`}>{info.title}</p>
          <p className="mt-0.5 break-words text-xs text-fg/80">{info.message}</p>
          {onRetry && (
            <button onClick={onRetry} className="mt-2 inline-flex items-center gap-1 rounded-md border border-current/30 px-2.5 py-1 text-xs font-medium text-fg transition hover:bg-fg/5">
              <RefreshIcon className="h-3.5 w-3.5" /> Try again
            </button>
          )}
        </div>
        {onDismiss && (
          <button onClick={onDismiss} aria-label="Dismiss" className="h-6 w-6 shrink-0 rounded-md text-muted transition hover:bg-fg/10 hover:text-fg">
            <XIcon className="mx-auto h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
}
