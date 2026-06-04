import UploadZone from "../components/UploadZone"
import AnalyzingView from "../components/AnalyzingView"
import ResultView from "../components/ResultView"
import { useAnalysis } from "../hooks/useAnalysis"

const RECENT = [
  { name: "interview_clip_04.mp4", verdict: "fake",       score: 6  },
  { name: "profile_suspect.jpg",   verdict: "suspicious", score: 39 },
  { name: "press_release.png",     verdict: "authentic",  score: 97 },
]

const verdictStyle = {
  fake:       "verdict-fake",
  suspicious: "verdict-suspicious",
  authentic:  "verdict-authentic",
}

export default function AnalyzePage() {
  const { status, progress, result, error, analyze, reset } = useAnalysis()
  const [selectedFile, setSelectedFile] = useState(null)

  const handleFile = (file) => {
    setSelectedFile(file)
    analyze(file)
  }

  const handleReset = () => {
    setSelectedFile(null)
    reset()
  }

  const isIdle      = status === "idle"
  const isAnalyzing = ["uploading","pending","processing"].includes(status)
  const isDone      = status === "completed"
  const isFailed    = status === "failed"

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="font-display text-2xl font-bold text-surface-50">Analyze Media</h1>
        <p className="text-surface-400 text-sm mt-1">Upload an image or video to detect deepfakes and manipulation</p>
      </div>

      {isIdle && (
        <>
          <UploadZone onFile={handleFile} />
          {/* Recent */}
          <div className="mt-8">
            <div className="text-xs text-surface-500 uppercase tracking-widest mb-3">Recent Activity</div>
            <div className="card divide-y divide-surface-800">
              {RECENT.map((item) => (
                <div key={item.name} className="flex items-center gap-3 px-4 py-3">
                  <span className="text-surface-500">📄</span>
                  <span className="flex-1 text-sm text-surface-300 font-mono truncate">{item.name}</span>
                  <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${verdictStyle[item.verdict]}`}>
                    {item.verdict.toUpperCase()} · {item.score}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {isAnalyzing && (
        <AnalyzingView
          fileName={selectedFile?.name}
          progress={progress}
          status={status}
        />
      )}

      {isFailed && (
        <div className="card p-6 text-center">
          <div className="text-4xl mb-3">⚠</div>
          <div className="text-surface-200 font-medium mb-1">Analysis Failed</div>
          <div className="text-surface-400 text-sm mb-4">{error}</div>
          <button onClick={handleReset} className="btn-primary mx-auto">Try Again</button>
        </div>
      )}

      {isDone && result && (
        <ResultView result={result} onReset={handleReset} />
      )}
    </div>
  )
}

import { useState } from "react"
