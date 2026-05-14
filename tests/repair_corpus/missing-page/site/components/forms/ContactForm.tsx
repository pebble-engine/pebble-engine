"use client";
import { useActionState } from "react";
import { submitContactForm } from "@/app/actions/contact";

export function ContactForm() {
  const [_, action] = useActionState(submitContactForm, null);
  return <form action={action} />;
}
