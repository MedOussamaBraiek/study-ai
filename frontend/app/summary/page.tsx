"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

const SummaryPage = () => {
  const router = useRouter();
  const [summary, setSummary] = useState("");

  useEffect(() => {
    const stored = localStorage.getItem("summary");
    if (!stored) router.push("/");
    // eslint-disable-next-line react-hooks/set-state-in-effect
    else setSummary(stored);
  }, []);

  const formatted = summary
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n\*/g, "<br/>•")
    .replace(/\n/g, "<br/>");

  return (
    <div className="min-h-screen bg-gray-100 p-10">
      <button
        onClick={() => router.push("/")}
        className="absolute top-5 left-5 bg-white text-black px-4 py-2 rounded-xl shadow cursor-pointer"
      >
        ← Back
      </button>
      <div className="max-w-3xl mx-auto bg-white rounded-2xl shadow-lg p-8 mt-10">
        <h1 className="text-2xl font-bold mb-6 text-gray-500">
          📄 PDF Summary
        </h1>
        <div
          className="text-gray-700 leading-relaxed"
          dangerouslySetInnerHTML={{ __html: formatted }}
        />
      </div>
    </div>
  );
};

export default SummaryPage;
