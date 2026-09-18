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
    if (sliderValue > 80) {
      playSound('cringe')
    } else if (sliderValue > 60) {
      playSound('fail')
    } else {
      playSound('success')
    }
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
    if (sliderValue < 95) return '🤬'
    return '💀'
  }

  const getLabel = () => {
    if (sliderValue < 20) return 'Vraiment chill... suspicieux 👀'
    if (sliderValue < 40) return "Un peu énervant mais c'est bon"
    if (sliderValue < 60) return "C'est acceptable pour un humain"
    if (sliderValue < 80) return 'OK ça devient dangereux là ngl'
    if (sliderValue < 95) return "POURQUOI TU M'AIMES AUTANT 😭😭😭"
    return "BRO T'ES DANGEREUSE T'ES OBSÉDÉE DE MOI 💀"
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
        className="card-base bg-gradient-to-br from-white/80 to-rose-50/80 p-8 space-y-6"
      >
        {/* Emoji indicator */}
        <motion.div
          animate={{
            scale: [1, 1.3, 1],
            rotate: sliderValue > 80 ? [0, -5, 5, -5, 0] : 0
          }}
          transition={{
            duration: sliderValue > 80 ? 0.4 : 0.5,
            repeat: Infinity
          }}
          className="text-center text-7xl drop-shadow-lg"
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
            className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-rose-500 shadow-md"
            style={{
              background: `linear-gradient(to right, ${sliderValue > 80 ? '#dc2626' : sliderValue > 60 ? '#f97316' : '#ec4899'} 0%, ${sliderValue > 80 ? '#dc2626' : sliderValue > 60 ? '#f97316' : '#ec4899'} ${sliderValue}%, #e5e7eb ${sliderValue}%, #e5e7eb 100%)`
            }}
          />

          <div className="flex justify-between text-xs text-gray-600 font-bold">
            <span>😇 Ange</span>
            <motion.span
              key={sliderValue}
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 0.3 }}
              className="text-rose-600 font-black"
            >
              {sliderValue}
            </motion.span>
            <span>Démon 😈</span>
          </div>
        </div>

        {/* Label */}
        <motion.p
          key={sliderValue}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`text-center font-bold text-lg ${
            sliderValue > 80 ? 'text-red-600' : sliderValue > 60 ? 'text-orange-600' : 'text-gray-700'
          }`}
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
