/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useEffect, useState } from "react";
import { gsap } from "gsap";
import api from "@/lib/api";
import confetti from "canvas-confetti";
import { useRouter } from "next/navigation";

export default function QuizPage() {
  const [sessionId, setSessionId] = useState("");
  const [question, setQuestion] = useState<any>(null);
  const [selected, setSelected] = useState("");
  const [feedback, setFeedback] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [showNext, setShowNext] = useState(false);
  const [progress, setProgress] = useState(0);

  const [finished, setFinished] = useState(false);

  const [xp, setXp] = useState(0);
  const [gainedXp, setGainedXp] = useState(0);

  const router = useRouter();

  useEffect(() => {
    let mounted = true;

    const initializeSession = async () => {
      const res = await api.post("/start-session", {});
      if (mounted) {
        setSessionId(res.data.session_id);
        setQuestion(res.data.question);
      }
    };

    initializeSession();

    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (finished) {
      confetti({
        particleCount: 150,
        spread: 70,
      });
    }
  }, [finished]);

  useEffect(() => {
    if (question) {
      gsap.fromTo(
        ".card",
        { x: 50, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.4 },
      );
    }
  }, [question]);

  const submitAnswer = async () => {
    if (!selected) return;

    setLoading(true);

    const res = await api.post("/answer", {
      session_id: sessionId,
      user_answer: selected,
    });

    if (res.data.done) {
      setFinished(true);
    }

    setProgress((prev) => prev + 20);

    setFeedback(res.data);
    setLoading(false);
    setShowNext(true);

    const gained =
      res.data?.evaluation?.score >= 8
        ? 10
        : res.data?.evaluation?.score >= 5
          ? 5
          : 0;

    setXp((prev) => prev + gained);
    setGainedXp(gained);
  };

  if (!question)
    return (
      <div className="flex items-center justify-center h-screen bg-white">
        <div className="flex flex-col items-center gap-4">
          <div className="h-16 w-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-lg font-semibold text-gray-700">
            Analyzing your document...
          </p>
        </div>
      </div>
    );

  if (finished) {
    return (
      <div className="h-screen flex flex-col items-center justify-center bg-linear-to-br from-green-100 to-blue-100 text-gray-500">
        <h1 className="text-3xl font-bold mb-2">🎉 Test Completed!</h1>

        <p className="text-xl my-4">
          Final Score: {feedback?.final_score ?? 0}
        </p>
        <p className="text-lg mb-6">XP Earned: {xp}</p>

        <div className="bg-white p-4 rounded-xl shadow w-96">
          <h2 className="font-bold mb-2">Weak Topics</h2>

          {Object.keys(feedback?.weak_topics || {}).length > 0 ? (
            Object.entries(feedback.weak_topics).map(([k, v]) => (
              <p key={k}>
                {k}: {String(v)} mistakes
              </p>
            ))
          ) : (
            <p>No weak topics 🎯</p>
          )}
        </div>

        <button
          onClick={() => window.location.reload()}
          className="mt-6 bg-green-500 text-white px-6 py-2 rounded-xl"
        >
          Practice Again
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100 gap-6">
      <button
        onClick={() => router.push("/")}
        className="absolute top-5 left-5 bg-white text-black px-4 py-2 rounded-xl shadow cursor-pointer"
      >
        ← Back
      </button>

      <div className="absolute top-10 right-10 text-green-500 font-bold animate-bounce">
        +{gainedXp} XP 🚀
      </div>

      <div className="card bg-white text-gray-500 p-8 rounded-3xl shadow-2xl border border-gray-100 max-w-xl w-full">
        {" "}
        <div className="w-full bg-gray-200 h-3 rounded-full overflow-hidden mb-7">
          <div
            className="bg-green-500 h-3 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
        <h2 className="text-lg font-bold mb-4 text-center">
          {question.question}
        </h2>
        <div className="flex flex-col gap-3">
          {question.options?.length > 0 ? (
            question.options.map((opt: string, i: number) => (
              <button
                key={i}
                onClick={() => setSelected(opt)}
                disabled={showNext}
                className={`px-4 py-2 rounded-xl border-2 transition-all
                  ${
                    selected === opt
                      ? "bg-blue-500 text-white border-blue-500 "
                      : "bg-white hover:bg-blue-50 border-gray-200"
                  }`}
              >
                {opt}
              </button>
            ))
          ) : (
            <input
              placeholder="Type your answer..."
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
              className="border p-2 rounded text-black"
            />
          )}
        </div>
        {!showNext && (
          <button
            onClick={submitAnswer}
            disabled={loading}
            className="mt-5 w-full bg-green-500 text-white py-2 rounded-xl"
          >
            {loading ? (
              <div className="w-full flex justify-center items-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Checking...
              </div>
            ) : (
              "Submit"
            )}
          </button>
        )}
        {feedback && (
          <div className="mt-4 text-center">
            <p
              className={`font-bold text-lg ${
                (feedback?.evaluation?.score ?? 0) >= 8
                  ? "text-green-600"
                  : "text-red-500"
              }`}
            >
              Score: {feedback?.evaluation?.score ?? 0}
            </p>
            <p>{feedback?.evaluation?.feedback ?? "No feedback available"}</p>

            {feedback?.explanation && (
              <p className="text-yellow-600 mt-2">{feedback?.explanation}</p>
            )}
          </div>
        )}
        {showNext && !feedback?.done && (
          <button
            onClick={() => {
              setQuestion(feedback.next_question!);
              setFeedback(null);
              setSelected("");
              setShowNext(false);
            }}
            className="bg-blue-500 w-full text-white px-6 py-2 rounded mt-4"
          >
            Next Question →
          </button>
        )}
      </div>
    </div>
  );
}
