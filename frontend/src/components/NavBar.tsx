'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  { label: 'Dashboard', href: '/', shortcut: '⌘1' },
  { label: 'Research', href: '/research', shortcut: '⌘2' },
  { label: 'Screener', href: '/screener', shortcut: '⌘3' },
  { label: 'Signals', href: '/signals', shortcut: '⌘4' },
  { label: 'Portfolio', href: '/portfolio', shortcut: '⌘5' },
];

export default function NavBar() {
  const pathname = usePathname();

  return (
    <nav className="glass-nav mx-3 mt-3 flex items-center gap-2 px-2 py-1.5">
      {/* Logo */}
      <div className="flex items-center gap-2 rounded-xl bg-white/[0.03] px-3 py-1.5">
        <span className="bg-gradient-to-r from-green-400 via-cyan-400 to-purple-400 bg-clip-text text-lg font-bold text-transparent">
          ◆
        </span>
        <span className="text-sm font-bold text-[#f0f6fc]">
          Equity <span className="bg-gradient-to-r from-green-400 to-cyan-400 bg-clip-text text-transparent">Lens</span>
        </span>
      </div>

      {/* Nav items */}
      <div className="flex gap-0.5 text-xs text-white/40">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`rounded-lg px-3 py-2 transition-all duration-200 ${
                isActive
                  ? 'bg-green-500/10 text-green-400'
                  : 'hover:bg-white/[0.03] hover:text-white/70'
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </div>

      {/* Right side */}
      <div className="ml-auto flex items-center gap-3">
        <span className="rounded-lg border border-white/[0.06] px-2 py-1 text-xs text-white/30">
          ⌘K
        </span>
        <span className="h-1.5 w-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.6)]" />
        <span className="font-mono text-xs text-white/30">LIVE</span>
        <span className="font-mono text-xs text-white/40">45ms</span>
      </div>
    </nav>
  );
}
