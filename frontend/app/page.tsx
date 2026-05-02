"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { gsap } from "gsap";
import Image from "next/image";

export default function HomePage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
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
