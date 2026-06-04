const MODELS = [
  {
    name: "YOLOv8n — Face Detection",
    desc: "Real-time face detection and landmark extraction per frame",
    size: "6.2 MB",
    status: "online",
  },
  {
    name: "EfficientNet-B0 — Deepfake Classifier",
    desc: "Frame-level deepfake classification, real vs manipulated",
    size: "20.4 MB",
    status: "online",
  },
  {
    name: "ELA — JPEG Forensics",
    desc: "Error Level Analysis for image tampering and splicing detection",
    size: "Built-in",
    status: "online",
  },
  {
    name: "Grad-CAM — Heatmap Generator",
    desc: "Explainable AI heatmaps showing manipulated regions",
    size: "Built-in",
    status: "online",
  },
]

export default function ModelsPage() {
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="font-display text-2xl font-bold text-surface-50">Model Status</h1>
        <p className="text-surface-400 text-sm mt-1">Active detection models and their health</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {[
          { label: "Models Online",    val: "4 / 4",  color: "text-brand-400" },
          { label: "Avg Inference",    val: "~2.1s",  color: "text-surface-100" },
          { label: "Queue Depth",      val: "0",      color: "text-surface-100" },
        ].map(({ label, val, color }) => (
          <div key={label} className="card p-4">
            <div className="text-xs text-surface-500 uppercase tracking-widest mb-1">{label}</div>
            <div className={`font-display text-3xl font-bold ${color}`}>{val}</div>
          </div>
        ))}
      </div>

      {/* Models */}
      <div className="space-y-3">
        {MODELS.map((m) => (
          <div key={m.name} className="card p-5 flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl bg-brand-500/10 flex items-center justify-center text-xl flex-shrink-0">
              🧠
            </div>
            <div className="flex-1">
              <div className="font-medium text-surface-100 text-sm">{m.name}</div>
              <div className="text-xs text-surface-500 mt-0.5">{m.desc}</div>
            </div>
            <div className="text-xs text-surface-500 font-mono">{m.size}</div>
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-brand-400 animate-pulse-slow" />
              <span className="text-xs text-brand-400 font-medium">Online</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
