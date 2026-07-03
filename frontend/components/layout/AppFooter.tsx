import Link from 'next/link';
import { Instagram, Linkedin, Twitter } from 'lucide-react';

export function AppFooter() {
  return (
    <footer className="mt-auto border-t border-border bg-card/50 backdrop-blur-sm shrink-0">
      <div className="px-6 py-4 flex flex-col sm:flex-row items-center justify-between gap-3">

        {/* Left: Watermark */}
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold text-primary tracking-wide">CREATED BY BMS</span>
          <span className="text-border">·</span>
          <span className="text-[10px] text-muted-foreground">PVCPilot AI © 2026</span>
        </div>

        {/* Center: Tagline */}
        <p className="text-[10px] text-muted-foreground text-center hidden md:block">
          Multi-Agent Manufacturing Intelligence · Powered by Google Gemini 2.5 Pro
        </p>

        {/* Right: Social Icons */}
        <div className="flex items-center gap-3">
          <Link
            href="https://instagram.com/b.mohan2678"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Instagram"
            className="text-muted-foreground hover:text-pink-500 transition-colors"
          >
            <Instagram className="h-4 w-4" />
          </Link>
          <Link
            href="https://linkedin.com/in/mohanshankar-botcha-06668a379"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="LinkedIn"
            className="text-muted-foreground hover:text-blue-500 transition-colors"
          >
            <Linkedin className="h-4 w-4" />
          </Link>
          <Link
            href="https://twitter.com"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Twitter / X"
            className="text-muted-foreground hover:text-sky-400 transition-colors"
          >
            <Twitter className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </footer>
  );
}
export default AppFooter;
