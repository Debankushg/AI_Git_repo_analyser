export default function Avatar({ src, name, className = "h-7 w-7" }: { src?: string | null; name: string; className?: string }) {
  if (src) return <img src={src} alt={name} loading="lazy" className={`${className} shrink-0 rounded-full ring-1 ring-gold/60`} />;
  return (
    <span className={`${className} gold-fill grid shrink-0 place-items-center rounded-full text-[11px] font-bold text-[#2b1d03]`} aria-hidden>
      {name.charAt(0).toUpperCase()}
    </span>
  );
}
