import { Hero } from "@/components/sections/Hero";
import { Intro } from "@/components/sections/Intro";
import { Listings } from "@/components/sections/Listings";
import { Principal } from "@/components/sections/Principal";
import { Contact } from "@/components/sections/Contact";

export default function HomePage() {
  return (
    <>
      <Hero />
      <Intro />
      <Listings />
      <Principal />
      <Contact />
    </>
  );
}
