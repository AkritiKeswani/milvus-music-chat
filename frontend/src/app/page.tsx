'use client'

import { useState, useRef, useEffect } from 'react'
import axios from 'axios'

interface TrackInfo {
  artist: string
  song: string
  primary_genre: string
  mood: string
}

interface Message {
  type: 'user' | 'assistant'
  content: string
  tracks?: TrackInfo[]
  insights?: string[]
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      type: 'assistant',
      content: '👋 Hey! I know your music taste from your Spotify library. Ask me anything about your music preferences!\n\n💡 Try asking:\n• "What\'s my dominant genre?"\n• "Show me my country songs"\n• "What indie rock should I listen to?"\n• "Analyze my mood in music"'
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
      const response = await axios.post('http://localhost:8000/chat', {
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
        content: 'Sorry, I had trouble processing that. Make sure the backend is running on localhost:8000!'
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const suggestedQueries = [
    "What's my dominant music genre?",
    "Show me my country music taste",
    "What do I listen to when I'm sad?",
    "Recommend some indie rock from my library",
    "What's my most romantic song?",
    "Analyze my electronic music taste"
  ]

  const handleSuggestedQuery = (query: string) => {
    setInputValue(query)
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white rounded-2xl shadow-xl min-h-[80vh] flex flex-col">
        
        {/* Chat Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6 rounded-t-2xl">
          <h1 className="text-2xl font-bold">🎵 Your Music Taste Assistant</h1>
          <p className="text-purple-100 mt-1">I know your Spotify library - ask me anything about your music!</p>
        </div>

        {/* Messages Container */}
        <div className="flex-1 p-6 overflow-y-auto max-h-[60vh] space-y-4">
          {messages.map((message, index) => (
            <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] px-4 py-3 rounded-2xl ${
                message.type === 'user' 
                  ? 'bg-blue-600 text-white ml-auto' 
                  : 'bg-gray-100 text-gray-800 mr-auto'
              }`}>
                <div className="whitespace-pre-wrap text-sm leading-relaxed">
                  {message.content}
                </div>
                
                {/* Show relevant tracks */}
                {message.tracks && message.tracks.length > 0 && (
                  <div className="mt-3 space-y-2">
                    <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Your Songs:</p>
                    {message.tracks.slice(0, 4).map((track, trackIndex) => (
                      <div key={trackIndex} className="text-xs bg-white/80 p-2 rounded-lg border">
                        <p className="font-medium text-gray-900">{track.artist} - {track.song}</p>
                        <p className="text-gray-600 capitalize">
                          {track.primary_genre} • {track.mood}
                        </p>
                      </div>
                    ))}
                  </div>
                )}

                {/* Show insights */}
                {message.insights && message.insights.length > 0 && (
                  <div className="mt-3">
                    <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">Insights:</p>
                    <ul className="text-xs text-gray-600 space-y-1">
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
              <div className="bg-gray-100 text-gray-800 px-4 py-3 rounded-2xl max-w-[85%]">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
                  <span className="text-sm">Analyzing your music taste...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Queries */}
        {messages.length === 1 && (
          <div className="px-6 pb-4">
            <p className="text-sm text-gray-600 mb-3 font-medium">💡 Try asking:</p>
            <div className="grid grid-cols-2 gap-2">
              {suggestedQueries.map((query, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestedQuery(query)}
                  className="text-xs bg-purple-50 text-purple-700 px-3 py-2 rounded-lg hover:bg-purple-100 transition-colors text-left border border-purple-200"
                >
                  {query}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input Form */}
        <div className="border-t bg-gray-50 p-6 rounded-b-2xl">
          <form onSubmit={handleSendMessage} className="flex space-x-3">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask about your music taste..."
              className="flex-1 px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !inputValue.trim()}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-sm font-medium"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}