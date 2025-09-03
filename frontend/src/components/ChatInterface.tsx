'use client'

import { useState, useRef, useEffect } from 'react'
import axios from 'axios'

interface TrackInfo {
  artist: string
  song: string
  primary_genre: string
  mood: string
  similarity_score?: number
}

interface ChatResponse {
  response: string
  relevant_tracks: TrackInfo[]
  insights: string[]
}

interface Message {
  type: 'user' | 'assistant'
  content: string
  tracks?: TrackInfo[]
  insights?: string[]
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      type: 'assistant',
      content: 'Hi! I\'m ready to analyze your music taste. Ask me anything about your music preferences, genres, or mood patterns!'
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputValue.trim() || isLoading) return

    const userMessage = inputValue.trim()
    setInputValue('')
    
    // Add user message
    setMessages(prev => [...prev, { type: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      const response = await axios.post<ChatResponse>('http://localhost:8000/chat', {
        query: userMessage
      })

      // Add assistant response
      setMessages(prev => [...prev, {
        type: 'assistant',
        content: response.data.response,
        tracks: response.data.relevant_tracks,
        insights: response.data.insights
      }])
    } catch (error: any) {
      setMessages(prev => [...prev, {
        type: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Make sure the backend is running and your music library is uploaded.'
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const suggestedQueries = [
    "What's my dominant music genre?",
    "Explain my indie rock taste",
    "What mood do I prefer in music?",
    "Show me my most energetic songs",
    "Analyze my melancholic tracks"
  ]

  const handleSuggestedQuery = (query: string) => {
    setInputValue(query)
  }

  return (
    <div className="flex flex-col h-96">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 p-4 bg-gray-50 rounded-lg">
        {messages.map((message, index) => (
          <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
              message.type === 'user' 
                ? 'bg-primary-500 text-white' 
                : 'bg-white text-gray-800 shadow-sm border'
            }`}>
              <p className="text-sm">{message.content}</p>
              
              {/* Show relevant tracks */}
              {message.tracks && message.tracks.length > 0 && (
                <div className="mt-3 space-y-2">
                  <p className="text-xs font-semibold text-gray-600">Relevant Tracks:</p>
                  {message.tracks.slice(0, 3).map((track, trackIndex) => (
                    <div key={trackIndex} className="text-xs bg-gray-100 p-2 rounded">
                      <p className="font-medium">{track.artist} - {track.song}</p>
                      <p className="text-gray-600">
                        {track.primary_genre} • {track.mood}
                        {track.similarity_score && (
                          <span className="ml-2">({(track.similarity_score * 100).toFixed(0)}% match)</span>
                        )}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {/* Show insights */}
              {message.insights && message.insights.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-semibold text-gray-600">Insights:</p>
                  <ul className="text-xs text-gray-600 mt-1 space-y-1">
                    {message.insights.map((insight, insightIndex) => (
                      <li key={insightIndex}>• {insight}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white text-gray-800 shadow-sm border px-4 py-2 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-primary-500"></div>
                <span className="text-sm">Analyzing...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Queries */}
      {messages.length === 1 && (
        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2">Try asking:</p>
          <div className="flex flex-wrap gap-2">
            {suggestedQueries.map((query, index) => (
              <button
                key={index}
                onClick={() => handleSuggestedQuery(query)}
                className="text-xs bg-primary-100 text-primary-700 px-3 py-1 rounded-full hover:bg-primary-200 transition-colors"
              >
                {query}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSendMessage} className="flex space-x-2">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask about your music taste..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !inputValue.trim()}
          className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Send
        </button>
      </form>
    </div>
  )
}
