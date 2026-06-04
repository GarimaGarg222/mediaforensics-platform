import { useState, useRef, useCallback } from "react"
import { api } from "../api/client"

export function useAnalysis() {
  const [jobId,    setJobId]    = useState(null)
  const [status,   setStatus]   = useState("idle")   // idle | uploading | pending | processing | completed | failed
  const [progress, setProgress] = useState(0)
  const [result,   setResult]   = useState(null)
  const [error,    setError]    = useState(null)
  const pollRef = useRef(null)

  const stopPolling = () => {
    if (pollRef.current) {
      clearInterval(pollRef.current)
      pollRef.current = null
    }
  }

  const pollForResult = useCallback((id) => {
    pollRef.current = setInterval(async () => {
      try {
        const res = await api.getResult(id)
        const job = res.data

        setProgress(job.progress_pct || 0)
        setStatus(job.status)

        if (job.status === "completed") {
          setResult(job)
          stopPolling()
        } else if (job.status === "failed") {
          setError(job.error_message || "Analysis failed")
          stopPolling()
        }
      } catch (e) {
        setError("Could not reach server")
        stopPolling()
      }
    }, 2000)
  }, [])

  const analyze = useCallback(async (file) => {
    try {
      setStatus("uploading")
      setError(null)
      setResult(null)
      setProgress(0)
      stopPolling()

      const formData = new FormData()
      formData.append("file", file)

      const res = await api.analyze(formData)
      const { job_id } = res.data

      setJobId(job_id)
      setStatus("pending")
      pollForResult(job_id)

    } catch (e) {
      setError(e.response?.data?.detail || "Upload failed")
      setStatus("failed")
    }
  }, [pollForResult])

  const reset = useCallback(() => {
    stopPolling()
    setJobId(null)
    setStatus("idle")
    setProgress(0)
    setResult(null)
    setError(null)
  }, [])

  return { jobId, status, progress, result, error, analyze, reset }
}
