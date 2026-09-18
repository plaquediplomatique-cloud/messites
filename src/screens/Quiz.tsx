import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { QuizAnswers } from '../App'
import Question1 from '../components/questions/Question1'
import Question2 from '../components/questions/Question2'
import Question3 from '../components/questions/Question3'
import Question4 from '../components/questions/Question4'
import Question5 from '../components/questions/Question5'
import Question6 from '../components/questions/Question6'
import Question7 from '../components/questions/Question7'
import FinalQuestion from '../components/questions/FinalQuestion'
import { useSound } from '../hooks/useSound'

interface QuizProps {
  onComplete: (answers: QuizAnswers) => void
  onEasterEgg: () => void
}

const Quiz: React.FC<QuizProps> = ({ onComplete, onEasterEgg }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState<QuizAnswers>({})
  const { playSound } = useSound()

  const questions = [
    { id: 'rating', component: Question1 },
    { id: 'beautiful', component: Question2 },
    { id: 'dispute', component: Question3 },
    { id: 'annoying', component: Question4 },
    { id: 'kisses', component: Question5 },
    { id: 'reaction', component: Question6 },
    { id: 'annoyed', component: Question7 },
    { id: 'final', component: FinalQuestion },
  ]

  const handleAnswer = (answer: any) => {
    playSound('success')
    const updatedAnswers = { ...answers, [questions[currentQuestion].id]: answer }
    setAnswers(updatedAnswers)

    if (currentQuestion < questions.length - 1) {
      setTimeout(() => {
        setCurrentQuestion(prev => prev + 1)
      }, 300)
    } else {
      setTimeout(() => {
        onComplete(updatedAnswers)
      }, 300)
    }
  }

  const handlePrevious = () => {
    playSound('click')
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1)
    }
  }

  const CurrentComponent = questions[currentQuestion].component

  const progress = ((currentQuestion + 1) / questions.length) * 100

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="min-h-screen flex flex-col items-center justify-center px-4 py-8"
    >
      {/* Progress bar */}
      <motion.div className="w-full max-w-md mb-8">
        <div className="flex items-center gap-2 mb-4">
          <div className="flex-1 h-1 bg-gray-200 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-rose-500 to-pink-500"
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
          <p className="text-xs font-semibold text-gray-600 w-12 text-right">
            {currentQuestion + 1}/{questions.length}
          </p>
        </div>
      </motion.div>

      {/* Question content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentQuestion}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
          className="w-full max-w-md"
        >
          <CurrentComponent
            onAnswer={handleAnswer}
            onEasterEgg={onEasterEgg}
          />
        </motion.div>
      </AnimatePresence>

      {/* Navigation */}
      {currentQuestion > 0 && (
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={handlePrevious}
          className="mt-8 btn-ghost text-sm"
        >
          ← Retour
        </motion.button>
      )}
    </motion.div>
  )
}

export default Quiz
