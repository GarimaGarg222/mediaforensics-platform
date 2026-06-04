const SIGNAL_LABELS = {
  face_swap:              "Face Swap",
  gan_artifacts:          "GAN Artifacts",
  temporal_inconsistency: "Temporal Inconsistency",
  blink_anomaly:          "Blink Anomaly",
  jpeg_artifacts:         "JPEG Artifacts",
}

function VerdictBadge({ verdict }) {
  const map = {
    fake:       { cls: "verdict-fake",       icon: "⚠", label: "Deepfake Detected" },
    suspicious: { cls: "verdict-suspicious", icon: "◉", label: "Suspicious Content" },
    authentic:  { cls: "verdict-authentic",  icon: "✓", label: "Authentic Media"    },
  }
  const v = map[verdict] || map.authentic
  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium ${v.cls}`}>
      {v.icon} {v.label}
    </span>
  )
}

function SignalBar({ label, value }) {
  const pct   = Math.round(value * 100)
  const color = pct > 70 ? "bg-danger" : pct > 40 ? "bg-warn" : "bg-brand-500"
  const text  = pct > 70 ? "text-red-400" : pct > 40 ? "text-amber-400" : "text-brand-400"
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-surface-400 w-36 flex-shrink-0">{label}</span>
      <div className="flex-1 h-1.5 bg-surface-800 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all duration-700`} style={{ width: `${pct}%` }} />
      </div>
      <span className={`text-xs font-mono font-medium w-8 text-right ${text}`}>{pct}%</span>
    </div>
  )
}

export default function ResultView({ result, onReset }) {
  const { result: r, media } = result
  const scoreColor = r.verdict === "fake" ? "text-red-400" : r.verdict === "suspicious" ? "text-amber-400" : "text-brand-400"

  return (
    <div className="space-y-4 animate-fade-up">
      {/* Header */}
      <div className="flex items-center justify-between">
        <span className="text-sm text-surface-400 font-mono">{media?.filename}</span>
        <div className="flex gap-2">
          <button onClick={onReset} className="btn-ghost">↑ New Analysis</button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Score card */}
        <div className="card p-6">
          <div className="text-xs text-surface-500 uppercase tracking-widest mb-3">Authenticity Score</div>
          <div className={`font-display text-6xl font-bold leading-none mb-1 ${scoreColor}`}>
            {r.authenticity_score}
            <span className="text-2xl text-surface-500">%</span>
          </div>
          <div className="text-xs text-surface-500 mb-4">Confidence: {Math.round(r.confidence * 100)}%</div>
          <VerdictBadge verdict={r.verdict} />

          <div className="mt-6 space-y-3">
            <div className="text-xs text-surface-500 uppercase tracking-widest mb-2">Detection Signals</div>
            {Object.entries(r.signals).map(([k, v]) => (
              <SignalBar key={k} label={SIGNAL_LABELS[k] || k} value={v} />
            ))}
          </div>
        </div>

        {/* Heatmap */}
        <div className="card p-6">
          <div className="text-xs text-surface-500 uppercase tracking-widest mb-3">Forensic Heatmap</div>
          {r.heatmap_url ? (
            <img
              src={`http://localhost:8000${r.heatmap_url}`}
              alt="Forensic heatmap"
              className="w-full rounded-xl object-cover aspect-video bg-surface-800"
            />
          ) : (
            <div className="aspect-video bg-surface-800 rounded-xl flex items-center justify-center">
              <span className="text-surface-600 text-sm">Heatmap not available</span>
            </div>
          )}
          <div className="flex gap-3 mt-3 text-[11px] text-surface-500">
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-blue-500 inline-block"/>Low</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-amber-500 inline-block"/>Medium</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-red-500 inline-block"/>High</span>
          </div>
        </div>
      </div>

      {/* Frame timeline */}
      {r.frame_results?.length > 0 && (
        <div className="card p-6">
          <div className="text-xs text-surface-500 uppercase tracking-widest mb-3">
            Frame Analysis
            <span className="ml-2 text-red-400">{r.frames_flagged} flagged</span>
            <span className="ml-1 text-surface-600">/ {r.frames_analyzed} total</span>
          </div>
          <div className="flex gap-1 flex-wrap">
            {r.frame_results.map((f, i) => (
              <div
                key={i}
                title={`Frame ${f.frame_index}: ${f.is_manipulated ? "Manipulated" : "Clean"} (${Math.round(f.confidence * 100)}%)`}
                className={`w-6 h-4 rounded-sm cursor-pointer transition-opacity hover:opacity-70
                  ${f.is_manipulated ? "bg-red-500/70 border border-red-500" : "bg-surface-700"}`}
              />
            ))}
          </div>
        </div>
      )}

      {/* Metadata */}
      <div className="card p-6">
        <div className="text-xs text-surface-500 uppercase tracking-widest mb-3">Media Metadata</div>
        <div className="grid grid-cols-3 gap-3 text-sm">
          {[
            ["Filename",   media?.filename],
            ["Size",       media?.file_size_bytes ? `${(media.file_size_bytes/1024/1024).toFixed(1)} MB` : "—"],
            ["Type",       media?.mime_type],
            ["Resolution", media?.width ? `${media.width}×${media.height}` : "—"],
            ["Duration",   media?.duration_sec ? `${media.duration_sec}s` : "—"],
            ["FPS",        media?.fps || "—"],
          ].map(([label, val]) => (
            <div key={label}>
              <div className="text-xs text-surface-500">{label}</div>
              <div className="text-surface-200 font-mono text-xs mt-0.5 truncate">{val || "—"}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
