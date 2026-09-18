import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useSound } from '../../hooks/useSound'

interface Question4Props {
  onAnswer: (answer: number) => void
  onEasterEgg: () => void
}

const Question4: React.FC<Question4Props> = ({ onAnswer, onEasterEgg }) => {
  const [sliderValue, setSliderValue] = useState(50)
  const [hasAnswered, setHasAnswered] = useState(false)
  const { playSound } = useSound()

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value)
    setSliderValue(value)
  }

  const handleSubmit = () => {
    playSound('success')
    setHasAnswered(true)
    onEasterEgg()

    setTimeout(() => {
      onAnswer(sliderValue)
    }, 800)
  }

  const getEmoji = () => {
    if (sliderValue < 20) return '😇'
    if (sliderValue < 40) return '🤨'
    if (sliderValue < 60) return '😑'
    if (sliderValue < 80) return '😤'
    return '🤬'
  }

  const getLabel = () => {
    if (sliderValue < 20) return 'Presque pas insupportable'
    if (sliderValue < 40) return 'Un peu énervant'
    if (sliderValue < 60) return 'C\'est acceptable'
    if (sliderValue < 80) return 'Franchement insupportable'
    return 'ARRÊTE JE T\'AIME TROP 😭'
  }

  return (
    <div className="space-y-6">
      {/* Question */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="card-base p-6 text-center"
      >
        <p className="text-2xl font-black text-gray-800">
          À quel point suis-je insupportable ? 🤪
        </p>
      </motion.div>

      {/* Content */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="card-base p-8 space-y-6"
      >
        {/* Emoji indicator */}
        <motion.div
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 0.5, repeat: Infinity }}
          className="text-center text-6xl"
        >
          {getEmoji()}
        </motion.div>

        {/* Slider */}
        <div className="space-y-4">
          <input
            type="range"
            min="0"
            max="100"
            value={sliderValue}
            onChange={handleSliderChange}
            className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-rose-500"
            style={{
              background: `linear-gradient(to right, #fecdd3 0%, #fecdd3 ${sliderValue}%, #e5e7eb ${sliderValue}%, #e5e7eb 100%)`
            }}
          />

          <div className="flex justify-between text-xs text-gray-500 font-semibold">
            <span>Ange</span>
            <span>{sliderValue}</span>
            <span>Démon</span>
          </div>
        </div>

        {/* Label */}
        <motion.p
          key={sliderValue}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center text-gray-700 font-semibold"
        >
          {getLabel()}
        </motion.p>

        {/* Submit button */}
        {!hasAnswered && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleSubmit}
            className="btn-primary-rose w-full"
          >
            Valider ✓
          </motion.button>
        )}

        {/* Success message */}
        {hasAnswered && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="card-base bg-gradient-to-r from-green-50 to-emerald-50 p-4 text-center border-green-200"
          >
            <p className="text-green-600 font-bold">C'est noté 📝</p>
          </motion.div>
        )}
      </motion.div>
    </div>
  )
}

export default Question4
