"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createProject } from "@/lib/api";
import type { Upload } from "@/lib/types";
import BriefForm from "@/components/wizard/BriefForm";
import MediaUpload from "@/components/wizard/MediaUpload";
import SoundtrackChoice from "@/components/wizard/SoundtrackChoice";
import ReviewConfirm from "@/components/wizard/ReviewConfirm";

const STEPS = ["Brief", "Media", "Soundtrack", "Review"];

export default function NewProjectPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [projectId, setProjectId] = useState("");
  const [title, setTitle] = useState("");
  const [brief, setBrief] = useState("");
  const [uploads, setUploads] = useState<Upload[]>([]);
  const [soundtrackMode, setSoundtrackMode] = useState("ai_generate");

  const handleBriefSubmit = async (t: string, b: string) => {
    setTitle(t);
    setBrief(b);
    const project = await createProject(t, b);
    setProjectId(project.id);
    setStep(1);
  };

  const handleMediaContinue = () => {
    setStep(2);
  };

  const handleSoundtrackContinue = () => {
    setStep(3);
  };

  const handleStarted = () => {
    router.push(`/project?id=${projectId}`);
  };

  return (
    <div className="max-w-2xl mx-auto px-6 py-12">
      {/* Step indicator */}
      <div className="flex items-center gap-2 mb-10">
        {STEPS.map((s, i) => (
          <div key={s} className="flex items-center gap-2">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                i === step
                  ? "bg-[#6B5B4E] text-white"
                  : i < step
                    ? "bg-[#6B5B4E]/20 text-[#6B5B4E]"
                    : "bg-[#E8E0D6] text-[#B0A396]"
              }`}
            >
              {i < step ? "\u2713" : i + 1}
            </div>
            <span
              className={`text-sm ${
                i === step ? "text-[#1a1a1a] font-medium" : "text-[#B0A396]"
              }`}
            >
              {s}
            </span>
            {i < STEPS.length - 1 && (
              <div className="w-8 h-px bg-[#E8E0D6] mx-1" />
            )}
          </div>
        ))}
      </div>

      {/* Step content */}
      {step === 0 && <BriefForm onSubmit={handleBriefSubmit} />}
      {step === 1 && (
        <MediaUpload
          projectId={projectId}
          uploads={uploads}
          setUploads={setUploads}
          onContinue={handleMediaContinue}
        />
      )}
      {step === 2 && (
        <SoundtrackChoice
          projectId={projectId}
          onContinue={handleSoundtrackContinue}
        />
      )}
      {step === 3 && (
        <ReviewConfirm
          projectId={projectId}
          title={title}
          brief={brief}
          uploads={uploads}
          soundtrackMode={soundtrackMode}
          onStarted={handleStarted}
        />
      )}
    </div>
  );
}
