import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { BookingForm } from "@/components/forms/BookingForm";
import { BookingSidebar } from "@/components/sections/BookingSidebar";

export default function BookingPage() {
  return (
    <>
      <Navbar />
      <main className="flex-1 min-h-screen pt-28 px-6 bg-white">
        <div className="max-w-6xl mx-auto py-12">
          <h1 className="font-[family-name:var(--font-display)] text-5xl font-bold text-navy mb-4 text-center">
            Book your visit
          </h1>
          <p className="text-slate-600 text-lg text-center mb-12 max-w-2xl mx-auto">
            Pick a time. We&apos;ll handle the rest.
          </p>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start pb-24">
            <BookingForm />
            <BookingSidebar />
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
