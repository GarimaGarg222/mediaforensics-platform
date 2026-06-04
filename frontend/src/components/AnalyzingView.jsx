const STEPS = [
  "Frame extraction & sampling",
  "Facial landmark detection (YOLO)",
  "Deepfake classification (EfficientNet)",
  "GAN fingerprint analysis",
  "ELA & JPEG artifact forensics",
  "Forensic heatmap generation",
]

export default function AnalyzingView({ fileName, progress, status }) {
  const stepsDone = Math.floor((progress / 100) * STEPS.length)

  return (
    <div className="card p-6 animate-fade-up">
      {/* File info */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-surface-800 flex items-center justify-center text-xl">
          📄
        </div>
        <div>
          <div className="font-medium text-surface-100 text-sm">{fileName}</div>
          <div className="text-xs text-surface-500 mt-0.5 capitalize">{status}...</div>
        </div>
      </div>

      {/* Progress bar */}
      <div className="h-1 bg-surface-800 rounded-full mb-1 overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-brand-600 to-brand-400 rounded-full transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>
      <div className="text-right text-xs text-surface-500 mb-6">{progress}%</div>

      {/* Steps */}
      <div className="space-y-3">
        {STEPS.map((step, i) => {
          const done    = i < stepsDone
          const current = i === stepsDone
          return (
            <div key={i} className="flex items-center gap-3">
              <div className={`
                w-5 h-5 rounded-full flex items-center justify-center text-[10px] flex-shrink-0
                ${done    ? "bg-brand-500 text-white" : ""}
                ${current ? "bg-surface-700 border border-brand-500/50" : ""}
                ${!done && !current ? "bg-surface-800" : ""}
              `}>
                {done ? "✓" : current ? (
                  <span className="w-2 h-2 rounded-full bg-brand-400 animate-pulse block" />
                ) : ""}
              </div>
              <span className={`text-sm ${done ? "text-surface-300" : current ? "text-brand-400" : "text-surface-600"}`}>
                {step}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
