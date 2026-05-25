"use client";

import { useState } from "react";
import Image from "next/image";
import { ROOMS } from "@/content/site";

export function RoomTabs() {
  const [activeId, setActiveId] = useState(ROOMS[0].id);
  const active = ROOMS.find((r) => r.id === activeId) ?? ROOMS[0];

  return (
    <>
      <div className="flex justify-center gap-8 mb-12 flex-wrap">
        {ROOMS.map((room) => {
          const isActive = room.id === activeId;
          return (
            <button
              key={room.id}
              type="button"
              onClick={() => setActiveId(room.id)}
              className={`text-xl font-[family-name:var(--font-display)] tracking-wide py-2 border-b-2 transition-all ${
                isActive ? "border-burgundy text-burgundy" : "border-transparent text-charcoal/50 hover:text-charcoal"
              }`}
            >
              {room.title}
            </button>
          );
        })}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
        <div className="relative aspect-[4/3] bg-charcoal/10 rounded-sm overflow-hidden">
          <Image
            src={active.image}
            alt={active.title}
            fill
            sizes="(max-width: 768px) 100vw, 600px"
            className="object-cover"
          />
        </div>
        <div className="space-y-6">
          <h2 className="font-[family-name:var(--font-display)] text-4xl">{active.title}</h2>
          <ul className="space-y-3 text-base text-charcoal/70">
            <li className="flex justify-between border-b border-charcoal/10 pb-2">
              <span>Capacity</span>
              <span className="text-charcoal font-medium">{active.capacity}</span>
            </li>
          </ul>
        </div>
      </div>
    </>
  );
}
