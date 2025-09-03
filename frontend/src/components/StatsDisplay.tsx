'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'

interface StatsData {
  total_tracks: number
  genres: Record<string, number>
  moods: Record<string, number>
  top_artists: Array<{ artist: string; count: number }>
}

export default function StatsDisplay() {
  const [stats, setStats] = useState<StatsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await axios.get<StatsData>('http://localhost:8000/stats')
      setStats(response.data)
    } catch (err: any) {
      setError('Failed to load statistics')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-900">{error}</p>
      </div>
    )
  }

  if (!stats) return null

  return (
    <div className="space-y-6">
      {/* Overview */}
      <div className="bg-primary-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-primary-900 mb-2">Library Overview</h3>
        <p className="text-3xl font-bold text-primary-600">{stats.total_tracks}</p>
        <p className="text-primary-700">Total Tracks</p>
      </div>

      {/* Genres */}
      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Genre Distribution</h3>
        <div className="space-y-3">
          {Object.entries(stats.genres).map(([genre, count]) => (
            <div key={genre} className="flex items-center justify-between">
              <span className="text-gray-700 capitalize">{genre}</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-500 h-2 rounded-full"
                    style={{ width: `${(count / stats.total_tracks) * 100}%` }}
                  ></div>
                </div>
                <span className="text-sm text-gray-600 w-8 text-right">{count}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Moods */}
      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Mood Distribution</h3>
        <div className="space-y-3">
          {Object.entries(stats.moods).map(([mood, count]) => (
            <div key={mood} className="flex items-center justify-between">
              <span className="text-gray-700 capitalize">{mood}</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full"
                    style={{ width: `${(count / stats.total_tracks) * 100}%` }}
                  ></div>
                </div>
                <span className="text-sm text-gray-600 w-8 text-right">{count}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Top Artists */}
      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Artists</h3>
        <div className="space-y-2">
          {stats.top_artists.slice(0, 10).map((artist, index) => (
            <div key={artist.artist} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="text-sm text-gray-500 w-6">#{index + 1}</span>
                <span className="text-gray-700">{artist.artist}</span>
              </div>
              <span className="text-sm text-gray-600">{artist.count} tracks</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
