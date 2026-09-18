import { useState, useEffect } from 'react'
import { AnimatePresence } from 'framer-motion'
import Landing from './screens/Landing'
import Quiz from './screens/Quiz'
import Result from './screens/Result'
import BackgroundElements from './components/BackgroundElements'
import ParticleEffect from './components/ParticleEffect'
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
  const [particleTrigger, setParticleTrigger] = useState(false)
  const { playSound } = useSound()

  useEffect(() => {
    playSound('ambient')
  }, [playSound])

  const handleStartQuiz = () => {
    playSound('click')
    setCurrentScreen('quiz')
  }

  const handleCompleteQuiz = (finalAnswers: QuizAnswers) => {
    playSound('success')
    setAnswers(finalAnswers)
    setCurrentScreen('result')
    setParticleTrigger(!particleTrigger)
  }

  const handleRestart = () => {
    playSound('click')
    setCurrentScreen('landing')
    setAnswers({})
  }

  const handleEasterEgg = () => {
    setEasterEggCount(prev => prev + 1)
    playSound('dab')
    setParticleTrigger(!particleTrigger)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50 via-white to-pink-50 overflow-hidden relative">
      {/* Premium background elements */}
      <BackgroundElements />

      {/* Particle effects */}
      <ParticleEffect trigger={particleTrigger} type="mixed" count={40} />

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

      {/* Easter egg counter (secret) - enhanced */}
      {easterEggCount > 0 && (
        <div className="fixed bottom-6 left-6 text-xs text-gray-400 pointer-events-none font-bold">
          🥚 {easterEggCount} eggs found
        </div>
      )}
    </div>
  )
}

export default App
