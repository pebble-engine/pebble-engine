import Link from "next/link";
export function Footer() {
  return (
    <footer className="border-t border-white/10 bg-black text-white/80">
      <Link href="/faq">FAQ</Link>
      <Link href="/privacy">Privacy</Link>
      <Link href="/terms">Terms</Link>
    </footer>
  );
}
