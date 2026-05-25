import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { ReservationForm } from "@/components/forms/ReservationForm";

export default function ReservationsPage() {
  return (
    <>
      <Navbar />
      <main className="flex-1 min-h-screen pt-32 px-6 bg-bone/70">
        <div className="max-w-2xl mx-auto text-center">
          <h1 className="font-[family-name:var(--font-display)] text-5xl md:text-7xl italic mb-6">
            Secure Your Table
          </h1>
          <p className="text-charcoal/60 max-w-xl mx-auto">
            We accept reservations up to [30] days in advance. For parties larger than [8], please call us.
          </p>
        </div>
        <ReservationForm />
        <div className="pb-24" />
      </main>
      <Footer />
    </>
  );
}
