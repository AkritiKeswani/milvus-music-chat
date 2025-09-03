'use client'

import { useState } from 'react'
import FileUpload from '@/components/FileUpload'
import ChatInterface from '@/components/ChatInterface'
import StatsDisplay from '@/components/StatsDisplay'

export default function Home() {
  const [activeTab, setActiveTab] = useState<'upload' | 'chat' | 'stats'>('upload')
  const [isLibraryUploaded, setIsLibraryUploaded] = useState(false)

  const handleUploadSuccess = () => {
    setIsLibraryUploaded(true)
    setActiveTab('chat')
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Tab Navigation */}
      <div className="mb-8">
        <nav className="flex space-x-8" aria-label="Tabs">
          <button
            onClick={() => setActiveTab('upload')}
            className={`${
              activeTab === 'upload'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm`}
          >
            📁 Upload Library
          </button>
          <button
            onClick={() => setActiveTab('chat')}
            disabled={!isLibraryUploaded}
            className={`${
              activeTab === 'chat'
                ? 'border-primary-500 text-primary-600'
                : isLibraryUploaded
                ? 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                : 'border-transparent text-gray-300 cursor-not-allowed'
            } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm`}
          >
            💬 Chat
          </button>
          <button
            onClick={() => setActiveTab('stats')}
            disabled={!isLibraryUploaded}
            className={`${
              activeTab === 'stats'
                ? 'border-primary-500 text-primary-600'
                : isLibraryUploaded
                ? 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                : 'border-transparent text-gray-300 cursor-not-allowed'
            } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm`}
          >
            📊 Stats
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-lg shadow-lg">
        {activeTab === 'upload' && (
          <div className="p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Upload Your Music Library
            </h2>
            <p className="text-gray-600 mb-6">
              Upload a CSV file with your music library. The file should have two columns: artist and song.
            </p>
            <FileUpload onUploadSuccess={handleUploadSuccess} />
            
            <div className="mt-8 p-4 bg-blue-50 rounded-lg">
              <h3 className="text-lg font-semibold text-blue-900 mb-2">Expected CSV Format:</h3>
              <pre className="text-sm text-blue-800 bg-blue-100 p-3 rounded">
{`artist,song
Radiohead,Paranoid Android
Billie Eilish,bad guy
Arctic Monkeys,Do I Wanna Know
Frank Ocean,Pink Matter
Tame Impala,The Less I Know The Better`}
              </pre>
            </div>
          </div>
        )}

        {activeTab === 'chat' && (
          <div className="p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Chat About Your Music Taste
            </h2>
            <p className="text-gray-600 mb-6">
              Ask questions about your music taste using natural language. Try queries like:
              "What's my dominant genre?", "Explain my indie rock taste", or "What mood do I prefer?"
            </p>
            <ChatInterface />
          </div>
        )}

        {activeTab === 'stats' && (
          <div className="p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Library Statistics
            </h2>
            <p className="text-gray-600 mb-6">
              Overview of your music library with genre distribution and mood analysis.
            </p>
            <StatsDisplay />
          </div>
        )}
      </div>
    </div>
  )
}
