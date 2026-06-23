import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="border-b border-zinc-800 bg-zinc-950 sticky top-0 z-50">
      <div className="container mx-auto flex h-16 items-center px-4">
        <Link href="/" className="flex items-center gap-2.5 shrink-0">
          <div className="h-8 w-8 rounded-lg bg-violet-600 flex items-center justify-center text-white font-bold text-sm shadow">
            S
          </div>
          <span className="font-bold text-lg tracking-tight text-zinc-100">Scout</span>
        </Link>
        <div className="ml-auto flex items-center space-x-1 text-sm font-medium">
          <Link href="/results" className="px-3 py-2 rounded-md transition-colors hover:text-zinc-100 hover:bg-zinc-800 text-zinc-400">
            Results
          </Link>
          <Link href="/architecture" className="px-3 py-2 rounded-md transition-colors hover:text-zinc-100 hover:bg-zinc-800 text-zinc-400">
            Architecture
          </Link>
          <Link href="/about" className="px-3 py-2 rounded-md transition-colors hover:text-zinc-100 hover:bg-zinc-800 text-zinc-400">
            About
          </Link>
          <Link href="/rank" className="ml-2 inline-flex items-center rounded-lg bg-violet-600 text-white hover:bg-violet-700 px-4 py-2 transition-colors font-semibold">
            Run Demo →
          </Link>
        </div>
      </div>
    </nav>
  );
}
