export function Hero() {
  return (
    <section className="relative min-h-[100dvh] md:min-h-screen lg:min-h-[100dvh] overflow-hidden bg-black">
      <video autoPlay muted loop playsInline preload="metadata" className="absolute inset-0 w-full h-full object-cover" src="/videos/hero.mp4" poster="/images/hero-poster.jpg" />
      <a href="/contact" className="bg-white text-black px-6 py-3 rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white">Get Started</a>
    </section>
  );
}
