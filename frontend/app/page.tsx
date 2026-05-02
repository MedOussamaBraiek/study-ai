"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { gsap } from "gsap";
import Image from "next/image";

export default function HomePage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const [mode, setMode] = useState<"study" | "interview">("study");
  const [numQuestions, setNumQuestions] = useState(5);

  const router = useRouter();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);

      gsap.from(".file-name", {
        y: 10,
        opacity: 0,
        duration: 0.3,
      });
    }
  };

  const handleUpload = async () => {
    if (!file) return alert("Please select a PDF");

    localStorage.setItem("quizMode", mode);
    localStorage.setItem("quizNumQuestions", String(numQuestions));

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);

      await api.post("/pdf/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      gsap.to(".container", {
        opacity: 0,
        duration: 0.5,
        onComplete: () => router.push("/quiz"),
      });
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-screen min-h-screen flex flex-col items-center justify-center bg-linear-to-br from-blue-400 to-purple-500 text-white">
      <Image src="/quizzy-logo.png" width={300} height={300} alt="logo" />

      {/* <h1 className="text-5xl font-bold ">Quizzy AI</h1> */}

      <p className="text-center font-semibold tracking-wider sm:max-w-lg max-w-[90%] opacity-90 mb-10 text-amber-100 sm:text-xl text-[18px]">
        Turn your PDFs into interactive quizzes. Learn faster with AI-powered
        questions, instant feedback, and smart repetition.
      </p>

      <label className="cursor-pointer bg-white text-black px-6 py-4 rounded-xl shadow-lg hover:scale-105 transition">
        📄 Choose PDF
        <input
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
          hidden
        />
      </label>

      {file && (
        <p className="file-name mt-3 text-sm underline font-semibold tracking-wide">
          {file.name}
        </p>
      )}

      <div className="flex gap-3 mt-6">
        {["study", "interview"].map((m) => (
          <button
            key={m}
            onClick={() => setMode(m as "study" | "interview")}
            className={`px-5 py-2 rounded-xl font-semibold transition capitalize
        ${mode === m ? "bg-white text-blue-600" : "bg-white/20 text-white"}`}
          >
            {m === "study" ? "Study mode" : "Exam mode"}
          </button>
        ))}
      </div>

      <div className="mt-4 flex items-center gap-4 text-white">
        <span className="text-sm font-medium">Questions: {numQuestions}</span>
        <input
          type="range"
          min={3}
          max={10}
          value={numQuestions}
          onChange={(e) => setNumQuestions(Number(e.target.value))}
          className="w-40"
        />
      </div>

      <button
        onClick={handleUpload}
        disabled={loading}
        className="mt-6 bg-green-500 hover:bg-green-600 px-8 py-3 rounded-xl font-semibold shadow-lg transition"
      >
        {loading ? (
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            Processing...
          </div>
        ) : (
          "Start Learning"
        )}
      </button>
    </div>
  );
}
