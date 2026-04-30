"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { gsap } from "gsap";

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
      <h1 className="text-4xl font-bold mb-8">Quizzy</h1>

      <label className="cursor-pointer bg-white text-black px-6 py-4 rounded-xl shadow-lg hover:scale-105 transition">
        📄 Choose PDF
        <input
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
          hidden
        />
      </label>

      {file && <p className="file-name mt-3 text-sm">{file.name}</p>}

      <button
        onClick={handleUpload}
        disabled={loading}
        className="mt-6 bg-green-500 hover:bg-green-600 px-8 py-3 rounded-xl font-semibold shadow-lg transition"
      >
        {loading ? "Uploading..." : "Start Learning"}
      </button>
    </div>
  );
}
