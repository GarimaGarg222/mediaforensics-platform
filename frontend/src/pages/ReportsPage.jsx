export default function ReportsPage() {
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="font-display text-2xl font-bold text-surface-50">Forensic Reports</h1>
        <p className="text-surface-400 text-sm mt-1">Downloadable PDF reports for completed analyses</p>
      </div>

      <div className="card p-6 mb-4">
        <div className="text-sm text-surface-300 mb-2 font-medium">About Forensic Reports</div>
        <p className="text-sm text-surface-400 leading-relaxed">
          Each completed analysis generates a forensic PDF report including authenticity scores,
          heatmap overlays, frame-by-frame breakdowns, metadata analysis, and chain-of-custody
          logs suitable for legal or journalistic use. Reports are generated on Day 5.
        </p>
      </div>

      <div className="card p-8 text-center">
        <div className="text-4xl mb-3">📋</div>
        <div className="text-surface-300 font-medium mb-1">PDF Report Generation</div>
        <div className="text-surface-500 text-sm">Coming in Day 5 — ReportLab integration</div>
      </div>
    </div>
  )
}
