import { useState, useEffect } from 'react'
import { AnimatePresence } from 'framer-motion'
import Landing from './screens/Landing'
import Quiz from './screens/Quiz'
import Result from './screens/Result'
import { useSound } from './hooks/useSound'

export type Screen = 'landing' | 'quiz' | 'result'

export interface QuizAnswers {
  rating?: number
  beautiful?: string
  dispute?: string
  annoying?: number
  kisses?: number
  reaction?: string
  future?: string
  annoyed?: string
}

function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('landing')
  const [answers, setAnswers] = useState<QuizAnswers>({})
  const [easterEggCount, setEasterEggCount] = useState(0)
  const { playSound } = useSound()

  useEffect(() => {
    // Add subtle background music or audio cues
    playSound('ambient')
  }, [])

  const handleStartQuiz = () => {
    playSound('click')
    setCurrentScreen('quiz')
  }

  const handleCompleteQuiz = (finalAnswers: QuizAnswers) => {
    playSound('success')
    setAnswers(finalAnswers)
    setCurrentScreen('result')
  }

  const handleRestart = () => {
    playSound('click')
    setCurrentScreen('landing')
    setAnswers({})
  }

  const handleEasterEgg = () => {
    setEasterEggCount(prev => prev + 1)
    playSound('ding')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50 via-white to-pink-50 overflow-hidden">
      {/* Background decoration */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-10 right-10 w-72 h-72 bg-rose-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse-slow" />
        <div className="absolute bottom-10 left-10 w-72 h-72 bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse-slow" />
        <div className="absolute top-1/2 left-1/3 w-96 h-96 bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-pulse-slow" />
      </div>

      {/* Main content */}
      <div className="relative z-10">
        <AnimatePresence mode="wait">
          {currentScreen === 'landing' && (
            <Landing
              key="landing"
              onStart={handleStartQuiz}
              onEasterEgg={handleEasterEgg}
            />
          )}
          {currentScreen === 'quiz' && (
            <Quiz
              key="quiz"
              onComplete={handleCompleteQuiz}
              onEasterEgg={handleEasterEgg}
            />
          )}
          {currentScreen === 'result' && (
            <Result
              key="result"
              answers={answers}
              onRestart={handleRestart}
              onEasterEgg={handleEasterEgg}
            />
          )}
        </AnimatePresence>
      </div>

      {/* Easter egg counter (secret) */}
      {easterEggCount > 0 && (
        <div className="fixed bottom-4 left-4 text-xs text-gray-300 pointer-events-none">
          🥚 {easterEggCount}
        </div>
      )}
    </div>
  )
}

export default App
