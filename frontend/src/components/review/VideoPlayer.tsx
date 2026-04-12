"use client";

import { fileUrl } from "@/lib/api";

interface Props {
  filePath: string;
  title?: string;
}

export default function VideoPlayer({ filePath, title }: Props) {
  const url = fileUrl(filePath);

  return (
    <div className="rounded-xl overflow-hidden bg-white border border-[#E8E0D6] shadow-sm">
      {title && (
        <div className="px-4 py-2 bg-[#FAF6F1] border-b border-[#E8E0D6]">
          <p className="text-sm font-medium text-[#1a1a1a]">{title}</p>
        </div>
      )}
      <video src={url} controls className="w-full aspect-video" />
    </div>
  );
}
