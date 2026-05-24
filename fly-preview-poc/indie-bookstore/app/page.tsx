import { Hero } from "@/components/sections/Hero";
import { QaServices1 } from "@/components/sections/QaServices1";
import { QaServices2 } from "@/components/sections/QaServices2";
import { QaProcess } from "@/components/sections/QaProcess";
import { QaAbout } from "@/components/sections/QaAbout";
import { QaPricingFaq } from "@/components/sections/QaPricingFaq";
import { ContactFormWarm } from "@/components/sections/ContactFormWarm";
import { SmoothScroll } from "@/components/motion/SmoothScroll";

export default function Home() {
  return (
    <SmoothScroll>
      <Hero />
      <QaServices1 />
      <QaServices2 />
      <QaProcess />
      <QaAbout />
      <QaPricingFaq />
      <ContactFormWarm />
    </SmoothScroll>
  );
}