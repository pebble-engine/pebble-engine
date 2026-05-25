import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { RoomTabs } from "@/components/sections/RoomTabs";
import { EventForm } from "@/components/forms/EventForm";

export default function EventsPage() {
  return (
    <>
      <Navbar />
      <main className="flex-1 min-h-screen pt-24 px-6 bg-bone">
        <div className="max-w-4xl mx-auto mb-12 text-center">
          <h1 className="font-[family-name:var(--font-display)] text-5xl md:text-7xl italic mb-6">
            Private Dining
          </h1>
          <p className="text-charcoal/70 max-w-2xl mx-auto leading-relaxed">
            Three distinct spaces, each calibrated for intimacy, acoustics, and unobstructed service.
          </p>
        </div>
        <div className="max-w-5xl mx-auto pb-24">
          <RoomTabs />
          <div className="py-12 border-t border-charcoal/10 mt-16">
            <div className="max-w-2xl mx-auto">
              <h2 className="font-[family-name:var(--font-display)] text-4xl mb-8 text-center">
                Begin Planning
              </h2>
              <EventForm />
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
