export function Navbar({ businessName }: { businessName: string }) {
  return (
    <div className="absolute inset-x-0 top-0 z-50 flex items-start px-6 pt-6">
      <nav className="liquid-glass rounded-xl px-4 py-2 flex items-center justify-between text-white">
        <span className="font-semibold">{businessName}</span>
      </nav>
    </div>
  );
}
