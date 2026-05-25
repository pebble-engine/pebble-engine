import Image from "next/image";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Reveal } from "@/components/ui/Reveal";
import { JOURNAL_POSTS } from "@/content/site";

export default function JournalPage() {
  return (
    <>
      <Navbar />
      <main className="flex-1 min-h-screen pt-24 px-6 bg-bone">
        <header className="pb-16 max-w-4xl mx-auto text-center">
          <h1 className="font-[family-name:var(--font-display)] text-5xl md:text-7xl italic mb-6">
            From the Kitchen
          </h1>
          <p className="text-charcoal/70 max-w-2xl mx-auto leading-relaxed">
            Seasonal reflections, supplier notes, and the quiet evolution of a menu.
          </p>
        </header>
        <section className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 pb-24">
          {JOURNAL_POSTS.map((post, i) => (
            <Reveal key={i} delay={i * 0.08}>
              <article className="border border-charcoal/10 rounded-sm overflow-hidden bg-bone hover:-translate-y-1 hover:shadow-md transition-all duration-300">
                <div className="relative w-full aspect-[4/3]">
                  <Image
                    src={post.image}
                    alt={post.title}
                    fill
                    sizes="(max-width: 768px) 100vw, 400px"
                    className="object-cover"
                  />
                </div>
                <div className="p-6">
                  <time className="text-xs uppercase tracking-widest text-warmgold">{post.date}</time>
                  <h3 className="font-[family-name:var(--font-display)] text-2xl mt-2 mb-3">{post.title}</h3>
                  <p className="text-sm text-charcoal/70 leading-relaxed">{post.body}</p>
                </div>
              </article>
            </Reveal>
          ))}
        </section>
        <section className="py-24 px-6 bg-charcoal/5 border-t border-charcoal/10 -mx-6">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="font-[family-name:var(--font-display)] text-4xl mb-4">Receive Seasonal Updates</h2>
            <p className="text-charcoal/60 mb-8">One email per month. Menu changes, harvest notes, and reservation windows.</p>
            <form className="flex flex-col sm:flex-row gap-2 max-w-md mx-auto" action="#">
              <input
                type="email"
                placeholder="Email address"
                required
                className="flex-1 bg-transparent py-3 px-3 border-b border-charcoal/30 outline-none focus:border-burgundy"
              />
              <button type="submit" className="bg-burgundy text-bone px-6 py-3 font-medium hover:bg-charcoal transition-colors">
                Subscribe
              </button>
            </form>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
