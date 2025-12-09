import { useState, useMemo } from "react";
import "./App.css";
import "tailwindcss";

type Status = "idle" | "processing" | "done" | "error";

export default function App() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState("");
  const [results, setResults] = useState<any[] | null>(null);
  const [meta, setMeta] = useState<any | null>(null);

  // Filters
  const [filterCluster, setFilterCluster] = useState<string>("all");
  const [filterArchetype, setFilterArchetype] = useState<string>("all");
  const [showScamsOnly, setShowScamsOnly] = useState<boolean>(false);
  const [riskLimit, setRiskLimit] = useState<number>(100);

  // Pagination
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(12);

  // Modal
  const [selectedEmail, setSelectedEmail] = useState<any | null>(null);

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
      if (!res.ok) throw new Error(json.error || "Server error");

      setMeta(json.meta);
      setResults(json.data);
      setStatus("done");
      setMessage("🎉 Processing complete!");
      setPage(1);
    } catch (err: any) {
      console.error(err);
      setStatus("error");
      setMessage("❌ " + (err?.message || "Something went wrong."));
    }
  };

  // Filtered data
  const filtered = useMemo(() => {
    if (!results) return [];
    return results.filter((email) => {
      if (filterCluster !== "all" && email.cluster !== Number(filterCluster))
        return false;
      if (filterArchetype !== "all" && email.cf_archetype !== filterArchetype)
        return false;
      if (showScamsOnly && !email.cf_is_scam) return false;
      if (email.cf_risk > riskLimit) return false;
      return true;
    });
  }, [results, filterCluster, filterArchetype, showScamsOnly, riskLimit]);

  // Pagination logic
  const totalPages = Math.ceil(filtered.length / pageSize);
  const pageData = filtered.slice((page - 1) * pageSize, page * pageSize);

  return (
    <main
      className="min-h-screen w-full 
      bg-gradient-to-br from-[#0f0c29] via-[#302b63] to-[#24243e]
      text-white p-8"
    >
      {/* HEADER */}
      <h1 className="text-5xl font-extrabold mb-3 text-center drop-shadow-lg">
        🔍 Scam Email Intelligence Dashboard
      </h1>
      <p className="text-gray-300 text-center mb-10 text-lg">
        AI-powered clustering, scam detection & analyst tooling.
      </p>

      {/* UPLOAD SECTION */}
      <div
        className="max-w-xl mx-auto 
        bg-white/10 backdrop-blur-xl 
        border border-white/20 
        p-8 rounded-2xl shadow-2xl"
      >
        <form onSubmit={handleSubmit}>
          <label className="block mb-4">
            <span className="text-gray-200 text-lg">Upload CSV File</span>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="mt-3 w-full bg-white/10 p-3 rounded-lg border border-white/20
                       focus:ring-2 focus:ring-purple-400 outline-none transition"
            />
          </label>

          <button
            className={`w-full py-3 rounded-xl font-bold text-lg transition 
              bg-gradient-to-r from-green-400 to-green-600
              shadow-lg hover:shadow-green-500/50
              ${
                status === "processing"
                  ? "opacity-50 cursor-wait"
                  : "hover:scale-[1.02]"
              }`}
            disabled={!files || status === "processing"}
          >
            {status === "processing" ? "Processing…" : "Run Analysis"}
          </button>
        </form>

        {message && (
          <p
            className={`mt-4 text-center p-3 rounded-xl text-lg font-semibold shadow
            ${
              status === "error"
                ? "bg-red-600/80"
                : status === "processing"
                ? "bg-yellow-600/80"
                : "bg-green-600/80"
            }`}
          >
            {message}
          </p>
        )}
      </div>

      {/* RESULTS */}
      {status === "done" && results && (
        <div className="mt-14 max-w-7xl mx-auto">
          {/* SUMMARY BOX */}
          <div
            className="bg-white/10 backdrop-blur-xl border border-white/20 
                        p-6 rounded-2xl shadow-xl mb-10"
          >
            <h2 className="text-3xl font-bold mb-3">📊 Analysis Summary</h2>
            <p className="text-lg">
              Total Emails: <strong>{meta.rows}</strong>
            </p>
            <p className="text-lg">
              Total Clusters: <strong>{meta.clusters}</strong>
            </p>
          </div>

          {/* FILTER PANEL */}
          <div
            className="bg-white/10 backdrop-blur-xl border border-white/20
                        p-6 rounded-2xl shadow-xl mb-8 grid md:grid-cols-5 gap-6"
          >
            {/* Cluster Filter */}
            <div>
              <label className="text-gray-200 font-semibold">Cluster</label>
              <select
                className="w-full mt-2 bg-white/10 p-2 rounded-lg border border-white/20 outline-none"
                value={filterCluster}
                onChange={(e) => {
                  setFilterCluster(e.target.value);
                  setPage(1);
                }}
              >
                <option value="all">All</option>
                {[...new Set(results.map((e) => e.cluster))].map((c) => (
                  <option key={c} value={c}>
                    Cluster {c}
                  </option>
                ))}
              </select>
            </div>

            {/* Archetype Filter */}
            <div>
              <label className="text-gray-200 font-semibold">Archetype</label>
              <select
                className="w-full mt-2 bg-white/10 p-2 rounded-lg border border-white/20 outline-none"
                value={filterArchetype}
                onChange={(e) => {
                  setFilterArchetype(e.target.value);
                  setPage(1);
                }}
              >
                <option value="all">All</option>
                {[...new Set(results.map((e) => e.cf_archetype))].map((a) => (
                  <option key={a} value={a}>
                    {a}
                  </option>
                ))}
              </select>
            </div>

            {/* Risk Slider */}
            <div>
              <label className="text-gray-200 font-semibold">
                Max Risk Score
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={riskLimit}
                onChange={(e) => {
                  setRiskLimit(Number(e.target.value));
                  setPage(1);
                }}
                className="w-full mt-3 accent-purple-400"
              />
              <div className="text-center text-gray-300">{riskLimit}</div>
            </div>

            {/* Scam Toggle */}
            <div className="flex items-center gap-2 mt-9">
              <input
                type="checkbox"
                checked={showScamsOnly}
                onChange={(e) => {
                  setShowScamsOnly(e.target.checked);
                  setPage(1);
                }}
                className="w-5 h-5 accent-red-500"
              />
              <span className="text-gray-200 font-semibold">Scams only</span>
            </div>

            {/* Page Size */}
            <div>
              <label className="text-gray-200 font-semibold">Page Size</label>
              <select
                className="w-full mt-2 bg-white/10 p-2 rounded-lg border border-white/20 outline-none"
                value={pageSize}
                onChange={(e) => {
                  setPageSize(Number(e.target.value));
                  setPage(1);
                }}
              >
                <option value={6}>6</option>
                <option value={12}>12</option>
                <option value={24}>24</option>
              </select>
            </div>
          </div>

          {/* EMAIL CARDS GRID */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {pageData.map((email) => (
              <div
                key={email.id}
                onClick={() => setSelectedEmail(email)}
                className="cursor-pointer bg-white/10 backdrop-blur-xl border border-white/10
                        p-6 rounded-2xl shadow-lg hover:shadow-purple-500/50
                        hover:-translate-y-1 transition"
              >
                <div className="flex justify-between mb-4">
                  <span
                    className="px-3 py-1 rounded-lg text-sm font-bold
                      bg-gradient-to-r from-blue-500 to-purple-600 shadow"
                  >
                    Cluster {email.cluster}
                  </span>

                  <span
                    className={`px-3 py-1 rounded-lg text-sm font-bold shadow 
                      ${
                        email.cf_risk > 70
                          ? "bg-red-600"
                          : email.cf_risk > 40
                          ? "bg-yellow-600"
                          : "bg-green-600"
                      }`}
                  >
                    Risk {email.cf_risk}
                  </span>
                </div>

                <h3 className="text-xl font-bold mb-2 truncate">
                  {email.subject || "(No Subject)"}
                </h3>

                <p className="text-sm text-purple-300 mb-3">
                  🧠 <strong>{email.cf_archetype}</strong>
                </p>

                <p className="text-gray-300 text-sm mb-4 line-clamp-4">
                  {(email.body || "").slice(0, 300)}…
                </p>

                {email.cf_is_scam && (
                  <p className="text-red-400 font-bold">
                    ⚠️ Scam Detected — Confidence {email.cf_conf}%
                  </p>
                )}
              </div>
            ))}
          </div>

          {/* PAGINATION */}
          <div className="flex justify-center items-center gap-6 mt-12">
            <button
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
              className="px-6 py-2 rounded-xl bg-white/10 
                        border border-white/20 
                        hover:bg-white/20 transition disabled:opacity-40"
            >
              ⬅ Previous
            </button>

            <span className="text-lg">
              Page <strong>{page}</strong> / <strong>{totalPages}</strong>
            </span>

            <button
              disabled={page === totalPages}
              onClick={() => setPage(page + 1)}
              className="px-6 py-2 rounded-xl bg-white/10 
                        border border-white/20 
                        hover:bg-white/20 transition disabled:opacity-40"
            >
              Next ➡
            </button>
          </div>
        </div>
      )}

      {/* MODAL - FULL EMAIL DETAILS */}
      {selectedEmail && (
        <div
          className="fixed inset-0 bg-black/70 backdrop-blur-xl flex justify-center items-center z-50 p-6"
          onClick={() => setSelectedEmail(null)}
        >
          <div
            className="bg-white/10 border border-white/20 p-8 rounded-2xl 
            max-w-3xl w-full shadow-2xl overflow-y-auto max-h-[85vh]"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="text-3xl font-bold mb-4">{selectedEmail.subject}</h2>

            <div className="flex flex-wrap gap-3 mb-6">
              <span className="px-3 py-1 rounded bg-blue-600 text-sm">
                Cluster {selectedEmail.cluster}
              </span>
              <span
                className={`px-3 py-1 rounded text-sm font-bold ${
                  selectedEmail.cf_risk > 70
                    ? "bg-red-600"
                    : selectedEmail.cf_risk > 40
                    ? "bg-yellow-600"
                    : "bg-green-600"
                }`}
              >
                Risk {selectedEmail.cf_risk}
              </span>
              <span className="px-3 py-1 rounded bg-purple-600 text-sm">
                {selectedEmail.cf_archetype}
              </span>
            </div>

            {selectedEmail.cf_is_scam && (
              <p className="text-red-400 font-bold text-lg mb-4">
                ⚠️ Scam Detected — Confidence {selectedEmail.cf_conf}%
              </p>
            )}

            <p className="text-gray-300 mb-2">
              <strong>Sender:</strong> {selectedEmail.sender}
            </p>
            <p className="text-gray-300 mb-4">
              <strong>Receiver:</strong> {selectedEmail.receiver}
            </p>

            <div className="bg-black/20 border border-white/10 p-4 rounded-xl max-h-[50vh] overflow-y-auto">
              <pre className="whitespace-pre-wrap text-gray-200 text-sm">
                {selectedEmail.body}
              </pre>
            </div>

            <button
              className="mt-6 w-full py-3 rounded-xl bg-red-600 hover:bg-red-500 font-bold"
              onClick={() => setSelectedEmail(null)}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </main>
  );
}
