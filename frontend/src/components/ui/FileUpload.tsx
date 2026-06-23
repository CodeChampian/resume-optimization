import { useRef, useState } from 'react'
import { cn } from '@/lib/utils'

interface FileUploadProps {
  accept?: string
  onFile: (file: File) => void
  loading?: boolean
  className?: string
}

export function FileUpload({ accept = '.tex', onFile, loading, className }: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragOver, setDragOver] = useState(false)

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) onFile(file)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) onFile(file)
  }

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      className={cn(
        'flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-6 text-sm transition-colors',
        dragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400',
        className,
      )}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleChange}
        className="hidden"
      />
      {loading ? (
        <span className="text-gray-500">Uploading...</span>
      ) : (
        <>
          <span className="font-medium text-gray-700">Drop .tex file here</span>
          <span className="mt-1 text-gray-500">or click to browse</span>
        </>
      )}
    </div>
  )
}
