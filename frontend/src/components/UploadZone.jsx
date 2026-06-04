import { useCallback, useState } from "react"

const ACCEPTED = ["image/jpeg","image/png","image/webp","image/gif","video/mp4","video/quicktime","video/avi","video/x-matroska"]

export default function UploadZone({ onFile }) {
  const [dragging, setDragging] = useState(false)

  const handleFile = useCallback((file) => {
    if (!file) return
    if (!ACCEPTED.includes(file.type)) {
      alert("Unsupported file type. Use JPG, PNG, MP4, MOV, etc.")
      return
    }
    onFile(file)
  }, [onFile])

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    handleFile(file)
  }, [handleFile])

  const onInputChange = (e) => handleFile(e.target.files[0])

  return (
    <div
      onDrop={onDrop}
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onClick={() => document.getElementById("file-input").click()}
      className={`
        relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer
        transition-all duration-200 group overflow-hidden
        ${dragging
          ? "border-brand-400 bg-brand-500/5"
          : "border-surface-700 hover:border-surface-500 bg-surface-900/50 hover:bg-surface-900"
        }
      `}
    >
      {/* Scan animation */}
      {dragging && (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute w-full h-0.5 bg-gradient-to-r from-transparent via-brand-400 to-transparent animate-scan opacity-60" />
        </div>
      )}

      <input
        id="file-input"
        type="file"
        accept=".jpg,.jpeg,.png,.webp,.gif,.mp4,.mov,.avi,.mkv"
        className="hidden"
        onChange={onInputChange}
      />

      <div className="text-4xl mb-4">
        {dragging ? "📂" : "☁"}
      </div>

      <div className="font-display text-lg font-bold text-surface-100 mb-1">
        {dragging ? "Drop to analyze" : "Drop media file here"}
      </div>
      <div className="text-sm text-surface-400 mb-6">
        or click to browse — images & video supported
      </div>

      <div className="flex gap-2 justify-center flex-wrap">
        {["JPG","PNG","WEBP","MP4","MOV","AVI"].map(f => (
          <span key={f} className="text-[11px] px-2.5 py-1 rounded-full bg-surface-800 text-surface-400 border border-surface-700">
            {f}
          </span>
        ))}
      </div>

      <div className="mt-4 text-[11px] text-surface-600">Max 500MB</div>
    </div>
  )
}
