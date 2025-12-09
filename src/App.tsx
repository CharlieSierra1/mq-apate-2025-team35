import { useState } from "react";
import "./App.css";

type Status = "idle" | "processing" | "done" | "error";

export default function App() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState("");
  const [results, setResults] = useState<any[] | null>(null);
  const [meta, setMeta] = useState<any | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFiles(e.target.files);
    setResults(null);
    setMeta(null);
    setStatus("idle");
    setMessage("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!files || files.length === 0) {
      setStatus("error");
      setMessage("❌ Please select a CSV file.");
      return;
    }

    setStatus("processing");
    setMessage("⏳ Uploading & processing…");

    const formData = new FormData();
    formData.append("files", files[0]);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/process", {
        method: "POST",
        body: formData,
      });

      const json = await res.json();
      console.log("RESULT:", json);

      if (!res.ok) throw new Error(json.error || "Server error");

      setMeta(json.meta);
      setResults(json.data);
      setStatus("done");
      setMessage("🎉 Processing complete!");
    } catch (err: any) {
      setStatus("error");
      setMessage("❌ " + (err?.message || "Something went wrong."));
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white p-8">
      {/* HEADER */}
      <header className="text-center mb-10">
        <h1 className="text-5xl font-extrabold mb-3 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent drop-shadow-lg">
          Email Intelligence Dashboard
        </h1>
        <p className="text-gray-300 text-lg max-w-2xl mx-auto">
          Upload your dataset and automatically uncover clusters, patterns, scam
          archetypes, and behavioural signals using <strong>AI + ML</strong>.
        </p>
      </header>

      {/* Upload Card */}
      <div className="flex justify-center mb-8">
        <form
          onSubmit={handleSubmit}
          className="backdrop-blur-lg bg-white/10 border border-white/20 shadow-2xl p-8 rounded-2xl w-full max-w-xl transition"
        >
          <label className="block mb-6">
            <span className="text-gray-200 font-semibold">Upload CSV File</span>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="mt-3 w-full text-white bg-gray-700 rounded-lg p-3 border border-gray-600 focus:ring-2 focus:ring-purple-500"
            />
          </label>

          <button
            type="submit"
            disabled={!files || status === "processing"}
            className={`w-full py-3 text-lg rounded-xl font-semibold transition-all ${
              status === "processing"
                ? "bg-yellow-500 cursor-wait"
                : "bg-purple-500 hover:bg-purple-400"
            }`}
          >
            {status === "processing" ? "Processing…" : "Run Analysis"}
          </button>
        </form>
      </div>

      {/* Status Message */}
      {message && (
        <p
          className={`text-center text-lg px-5 py-3 rounded-xl max-w-xl mx-auto mb-10 ${
            status === "error"
              ? "bg-red-600"
              : status === "processing"
              ? "bg-yellow-600"
              : "bg-green-600"
          }`}
        >
          {message}
        </p>
      )}

      {/* RESULTS */}
      {status === "done" && results && (
        <div className="w-full max-w-7xl mx-auto mt-6">
          {/* SUMMARY CARD */}
          <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-6 mb-10 shadow-xl">
            <h2 className="text-3xl font-bold mb-4">📊 Analysis Summary</h2>
            <div className="flex gap-10 text-lg text-gray-200">
              <p>
                Total Emails: <span className="font-semibold">{meta.rows}</span>
              </p>
              <p>
                Total Clusters:{" "}
                <span className="font-semibold">{meta.clusters}</span>
              </p>
            </div>
          </div>

          {/* GRID OF EMAIL CARDS */}
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
            {results.map((email) => (
              <div
                key={email.id}
                className="bg-white/10 backdrop-blur-xl border border-white/20 p-6 rounded-2xl shadow-xl hover:scale-[1.02] transition-all"
              >
                <div className="flex justify-between mb-4">
                  <span className="px-4 py-1 rounded-full text-sm font-bold bg-blue-600/80">
                    Cluster {email.cluster}
                  </span>

                  <span
                    className={`px-4 py-1 rounded-full text-sm font-bold ${
                      email.cf_risk > 70
                        ? "bg-red-600/80"
                        : email.cf_risk > 40
                        ? "bg-yellow-600/80"
                        : "bg-green-600/80"
                    }`}
                  >
                    Risk {email.cf_risk}
                  </span>
                </div>

                <h3 className="text-xl font-bold mb-2">
                  {email.subject || "(No Subject)"}
                </h3>

                <p className="text-sm mb-2 text-purple-300 font-semibold">
                  🧠 {email.cf_archetype}
                </p>

                <p className="text-gray-300 text-sm mb-4">
                  {(email.body || "").slice(0, 180)}…
                </p>

                {email.cf_is_scam && (
                  <span className="inline-block mt-2 px-3 py-1 bg-red-800/70 text-red-200 rounded-full text-sm font-bold">
                    ⚠️ Scam (Confidence {email.cf_conf}%)
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </main>
  );
}
