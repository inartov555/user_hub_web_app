import { Link } from "react-router-dom";

export default function Brand({ title }: { title: string }) {
  return (
    <Link
      data-tag="brandInfo"
      to="/"
      className="mr-[30px] inline-flex items-center gap-2 rounded-2xl
                 px-3 py-1.5 text-sm sm:text-base font-semibold tracking-wide
                 bg-gradient-to-r from-brand-50 to-purple-50
                 border border-brand-200/70 text-slate-900 shadow-soft
                 hover:from-brand-100 hover:to-purple-100 hover:shadow-card
                 transition-colors"
      aria-label={title}
    >
      <span className="inline-flex h-7 w-7 items-center justify-center
                       rounded-xl bg-brand-600 text-white text-xs font-bold
                       shadow ring-1 ring-white/60 select-none">
        v1.1
      </span>
      <span id="brandText" className="drop-shadow-[0_1px_0_rgba(255,255,255,0.6)]">
        {title}
      </span>
    </Link>
  );
}
