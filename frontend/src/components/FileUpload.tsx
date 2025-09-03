'use client'

import { useState, useRef } from 'react'
import axios from 'axios'

interface FileUploadProps {
  onUploadSuccess: () => void
}

interface UploadResponse {
  message: string
  processed_tracks: number
  total_tracks: number
}

export default function FileUpload({ onUploadSuccess }: FileUploadProps) {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (!file.name.endsWith('.csv')) {
      setError('Please upload a CSV file')
      return
    }

    setIsUploading(true)
    setError(null)
    setUploadResult(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post<UploadResponse>(
        'http://localhost:8000/ingest',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )

      setUploadResult(response.data)
      onUploadSuccess()
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 
        'Failed to upload file. Make sure the backend is running.'
      )
    } finally {
      setIsUploading(false)
    }
  }

  const triggerFileInput = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <div
        onClick={triggerFileInput}
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-primary-500 hover:bg-primary-50 transition-colors"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileUpload}
          className="hidden"
          disabled={isUploading}
        />
        
        <div className="space-y-2">
          <div className="text-4xl">📁</div>
          <p className="text-lg font-medium text-gray-900">
            {isUploading ? 'Processing...' : 'Click to upload CSV file'}
          </p>
          <p className="text-sm text-gray-500">
            CSV files with artist,song format only
          </p>
        </div>
      </div>

      {/* Loading State */}
      {isUploading && (
        <div className="flex items-center justify-center space-x-2 text-primary-600">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
          <span>Analyzing your music taste...</span>
        </div>
      )}

      {/* Success Message */}
      {uploadResult && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <span className="text-green-600">✅</span>
            <div>
              <p className="font-medium text-green-900">{uploadResult.message}</p>
              <p className="text-sm text-green-700">
                Successfully processed {uploadResult.processed_tracks} out of {uploadResult.total_tracks} tracks
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <span className="text-red-600">❌</span>
            <p className="text-red-900">{error}</p>
          </div>
        </div>
      )}
    </div>
  )
}
