"use client";

import { fileUrl } from "@/lib/api";

interface Props {
  filePath: string;
  title?: string;
}

export default function VideoPlayer({ filePath, title }: Props) {
  const url = fileUrl(filePath);

  return (
    <div className="rounded-xl overflow-hidden border border-white/10">
      {title && (
        <div className="px-4 py-2 bg-white/5 border-b border-white/10">
          <p className="text-sm font-medium">{title}</p>
        </div>
      )}
      <video src={url} controls className="w-full aspect-video" />
    </div>
  );
}
