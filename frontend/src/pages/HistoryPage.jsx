import { useState, useEffect } from "react"
import { api } from "../api/client"

const verdictStyle = {
  fake:       "verdict-fake",
  suspicious: "verdict-suspicious",
  authentic:  "verdict-authentic",
}

export default function HistoryPage() {
  const [jobs,    setJobs]    = useState([])
  const [loading, setLoading] = useState(true)
  const [stats,   setStats]   = useState({})
  const [filter,  setFilter]  = useState("")

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await api.getHistory({ limit: 50, verdict: filter || undefined })
        setJobs(res.data.results)
        setStats(res.data.stats || {})
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [filter])

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="font-display text-2xl font-bold text-surface-50">Analysis History</h1>
        <p className="text-surface-400 text-sm mt-1">All past media analyses</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          { label: "Total",      val: stats.total,      color: "text-surface-100" },
          { label: "Fake",       val: stats.fake,       color: "text-red-400"     },
          { label: "Suspicious", val: stats.suspicious, color: "text-amber-400"   },
          { label: "Authentic",  val: stats.authentic,  color: "text-brand-400"   },
        ].map(({ label, val, color }) => (
          <div key={label} className="card p-4">
            <div className="text-xs text-surface-500 uppercase tracking-widest mb-1">{label}</div>
            <div className={`font-display text-3xl font-bold ${color}`}>{val ?? "—"}</div>
          </div>
        ))}
      </div>

      {/* Filter */}
      <div className="flex gap-2 mb-4">
        {["", "fake", "suspicious", "authentic"].map((v) => (
          <button
            key={v}
            onClick={() => setFilter(v)}
            className={`text-xs px-3 py-1.5 rounded-full border transition-all
              ${filter === v
                ? "bg-brand-500/10 border-brand-500/30 text-brand-400"
                : "border-surface-700 text-surface-400 hover:border-surface-500"}`}
          >
            {v === "" ? "All" : v.charAt(0).toUpperCase() + v.slice(1)}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-surface-500">Loading...</div>
        ) : jobs.length === 0 ? (
          <div className="p-8 text-center text-surface-500">
            No analyses yet — upload your first file!
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-800">
                {["File", "Type", "Verdict", "Score", "Date"].map((h) => (
                  <th key={h} className="text-left px-4 py-3 text-xs text-surface-500 uppercase tracking-wider font-medium">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-800">
              {jobs.map((job) => (
                <tr key={job.job_id} className="hover:bg-surface-800/50 transition-colors">
                  <td className="px-4 py-3 font-mono text-xs text-surface-300 max-w-[200px] truncate">
                    {job.media?.filename || "—"}
                  </td>
                  <td className="px-4 py-3 text-surface-400 text-xs">
                    {job.media?.mime_type?.split("/")[0] || "—"}
                  </td>
                  <td className="px-4 py-3">
                    {job.result?.verdict ? (
                      <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${verdictStyle[job.result.verdict]}`}>
                        {job.result.verdict.toUpperCase()}
                      </span>
                    ) : (
                      <span className="text-xs text-surface-600 capitalize">{job.status}</span>
                    )}
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-surface-300">
                    {job.result?.authenticity_score != null
                      ? `${job.result.authenticity_score}%`
                      : "—"}
                  </td>
                  <td className="px-4 py-3 text-xs text-surface-500">
                    {new Date(job.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
