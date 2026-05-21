import { Hero } from "@/components/sections/Hero";
import { Features } from "@/components/sections/Features";
import { About } from "@/components/sections/About";
import { Menu } from "@/components/sections/Menu";
import { Contact } from "@/components/sections/Contact";

export default function HomePage() {
  return (
    <>
      <Hero />
      <Features />
      <About />
      <Menu />
      <Contact />
    </>
  );
}
