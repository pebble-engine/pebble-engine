"use client";

import { X, CheckCircle2, Circle } from "lucide-react";
import Link from "next/link";
import { type } from "@/lib/type";

type Props = {
  slug: string;
  published: boolean;
  onDismiss: () => void;
  onPublish: () => void;
};

export function PostBuildChecklist({ slug, published, onDismiss, onPublish }: Props) {
  const previewDone = true;
  const publishDone = published;

  return (
    <div className="fixed bottom-6 right-6 z-40 max-w-sm w-[calc(100%-2rem)] md:w-96 rounded-2xl border border-border bg-card shadow-lg p-5 space-y-4">
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className={`${type.heading.s} text-foreground`}>You&apos;re almost live</p>
          <p className={`${type.body.s} text-muted-foreground mt-0.5`}>
            Three quick steps to share your site.
          </p>
        </div>
        <button type="button" onClick={onDismiss} className="text-muted-foreground hover:text-foreground p-1" aria-label="Dismiss">
          <X className="w-4 h-4" />
        </button>
      </div>
      <ol className="space-y-3">
        <li className="flex items-center gap-2 text-sm">
          {previewDone ? <CheckCircle2 className="w-4 h-4 text-primary shrink-0" /> : <Circle className="w-4 h-4 shrink-0" />}
          <span>Preview your site in the editor</span>
        </li>
        <li className="flex items-center gap-2 text-sm">
          {publishDone ? <CheckCircle2 className="w-4 h-4 text-primary shrink-0" /> : <Circle className="w-4 h-4 shrink-0" />}
          {publishDone ? (
            <span>Published — nice work!</span>
          ) : (
            <button type="button" onClick={onPublish} className="underline underline-offset-2 font-medium">
              Publish to get your link
            </button>
          )}
        </li>
        <li className="flex items-center gap-2 text-sm">
          {publishDone ? <CheckCircle2 className="w-4 h-4 text-primary shrink-0" /> : <Circle className="w-4 h-4 shrink-0" />}
          {publishDone ? (
            <Link href={`/workspace/${encodeURIComponent(slug)}#phase=publish`} className="underline underline-offset-2">
              Copy your share link
            </Link>
          ) : (
            <span className="text-muted-foreground">Copy link after publish</span>
          )}
        </li>
      </ol>
    </div>
  );
}
