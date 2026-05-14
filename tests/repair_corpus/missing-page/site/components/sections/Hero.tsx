export function Hero() {
  return (
    <section className="relative min-h-[100dvh] bg-black">
      <video autoPlay muted loop playsInline className="absolute inset-0 w-full h-full object-cover" src="/videos/hero.mp4" poster="/images/hero-poster.jpg" />
    </section>
  );
}
