import { useState, useEffect } from "react"
import { api } from "../api/client"

export default function ReportsPage() {
  const [jobs,    setJobs]    = useState([])
  const [loading, setLoading] = useState(true)
  const [downloading, setDownloading] = useState({})

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await api.getHistory({ limit: 50 })
        const completed = res.data.results.filter(j => j.status === "completed")
        setJobs(completed)
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [])

  const downloadReport = async (jobId, filename) => {
    setDownloading(prev => ({ ...prev, [jobId]: true }))
    try {
      const res = await api.downloadReport(jobId)
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const a   = document.createElement("a")
      a.href    = url
      a.download = `forensic-report-${jobId.slice(0,8)}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (e) {
      alert("Report not ready yet. Try again in a moment.")
    } finally {
      setDownloading(prev => ({ ...prev, [jobId]: false }))
    }
  }

  const verdictStyle = {
    fake:       "verdict-fake",
    suspicious: "verdict-suspicious",
    authentic:  "verdict-authentic",
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="font-display text-2xl font-bold text-surface-50">Forensic Reports</h1>
        <p className="text-surface-400 text-sm mt-1">Download PDF reports for completed analyses</p>
      </div>

      <div className="card p-5 mb-6 flex gap-4">
        <div className="text-2xl">📋</div>
        <div>
          <div className="text-sm font-medium text-surface-200 mb-1">About Forensic Reports</div>
          <p className="text-sm text-surface-400 leading-relaxed">
            Each report includes authenticity scores, forensic heatmap overlays, frame-by-frame 
            analysis, metadata, and chain-of-custody logs — suitable for journalistic or legal use.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="card p-8 text-center text-surface-500">Loading...</div>
      ) : jobs.length === 0 ? (
        <div className="card p-8 text-center">
          <div className="text-3xl mb-3">📂</div>
          <div className="text-surface-400 text-sm">No completed analyses yet</div>
        </div>
      ) : (
        <div className="card divide-y divide-surface-800">
          {jobs.map((job) => (
            <div key={job.job_id} className="flex items-center gap-4 px-5 py-4">
              <div className="text-xl">📄</div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-surface-200 truncate">
                  {job.media?.filename || "Unknown file"}
                </div>
                <div className="text-xs text-surface-500 mt-0.5">
                  {new Date(job.created_at).toLocaleString()} · Job {job.job_id.slice(0,8)}
                </div>
              </div>
              {job.result?.verdict && (
                <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${verdictStyle[job.result.verdict]}`}>
                  {job.result.verdict.toUpperCase()}
                </span>
              )}
              <button
                onClick={() => downloadReport(job.job_id, job.media?.filename)}
                disabled={downloading[job.job_id]}
                className="btn-ghost text-xs py-1.5"
              >
                {downloading[job.job_id] ? "⏳ Generating..." : "⬇ Download PDF"}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
