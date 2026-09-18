import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Heart } from 'lucide-react'
import LoadingSequence from '../components/LoadingSequence'
import { useSound } from '../hooks/useSound'

interface LandingProps {
  onStart: () => void
  onEasterEgg: () => void
}

const Landing: React.FC<LandingProps> = ({ onStart, onEasterEgg }) => {
  const [isLoading, setIsLoading] = useState(true)
  const [loadingProgress, setLoadingProgress] = useState(0)
  const { playSound } = useSound()

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 4500)

    const interval = setInterval(() => {
      setLoadingProgress(p => (p < 100 ? p + Math.random() * 30 : 100))
    }, 400)

    return () => {
      clearTimeout(timer)
      clearInterval(interval)
    }
  }, [])

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6, ease: 'easeOut' },
    },
  }

  const handleStartClick = () => {
    playSound('click')
    onStart()
  }

  const handleEasterEggClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    onEasterEgg()
    playSound('dab')
  }

  if (isLoading) {
    return <LoadingSequence progress={Math.min(loadingProgress, 99)} />
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="min-h-screen flex items-center justify-center px-4 py-8"
    >
      <div className="w-full max-w-md">
        {/* Header - Premium Style */}
        <motion.div variants={itemVariants} className="text-center mb-12 space-y-6">
          <motion.div
            className="inline-block"
            animate={{ rotate: [0, -8, 8, -8, 0], scale: [1, 1.1, 1] }}
            transition={{ duration: 2.5, repeat: Infinity }}
          >
            <Heart className="w-24 h-24 text-rose-500 fill-current drop-shadow-2xl" />
          </motion.div>

          <motion.h1
            animate={{ y: [0, -5, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="text-5xl md:text-6xl font-black text-gradient leading-tight"
          >
            Bienvenue ❤️
          </motion.h1>

          <motion.div
            animate={{ opacity: [0.7, 1, 0.7] }}
            transition={{ duration: 2.5, repeat: Infinity }}
          >
            <p className="text-gray-600 text-xl font-bold">Évaluation Officielle</p>
          </motion.div>

          <motion.p
            animate={{ scale: [1, 1.02, 1] }}
            transition={{ duration: 3, repeat: Infinity }}
            className="text-sm text-gray-600 leading-relaxed font-medium max-w-sm mx-auto"
          >
            Cette évaluation déterminera si tu es juridiquement, scientifiquement et émotionnellement
            autorisée à être ma copine pour la vie.
            <span className="block mt-2 text-xs text-gray-500">
              (Spoiler: tu vas réussir 😏)
            </span>
          </motion.p>
        </motion.div>

        {/* Card - Premium */}
        <motion.div
          variants={itemVariants}
          className="card-premium p-8 mb-8 space-y-6 border-3 border-rose-200 shadow-2xl"
          whileHover={{
            y: -8,
            boxShadow: '0 30px 60px rgba(236, 72, 153, 0.25)',
          }}
        >
          <div className="space-y-3 text-center">
            <motion.p
              animate={{ opacity: [0.8, 1, 0.8] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="text-sm font-bold text-rose-600 uppercase tracking-widest"
            >
              Statut : En Attente
            </motion.p>
            <div className="w-full h-2 bg-gray-300 rounded-full overflow-hidden shadow-inner">
              <motion.div
                className="h-full bg-gradient-to-r from-rose-500 via-pink-500 to-rose-500"
                animate={{
                  width: ['0%', '30%', '0%'],
                  opacity: [0.5, 1, 0.5],
                }}
                transition={{ duration: 2, repeat: Infinity }}
              />
            </div>
            <p className="text-sm text-gray-600 font-semibold">
              Prêt à tester ta loyauté ? 👀
            </p>
          </div>
        </motion.div>

        {/* Button - PREMIUM & ANIMATED */}
        <motion.button
          variants={itemVariants}
          onClick={handleStartClick}
          whileHover={{
            scale: 1.08,
            y: -5,
          }}
          whileTap={{ scale: 0.92 }}
          animate={{ y: [0, -3, 0] }}
          transition={{ duration: 1.8, repeat: Infinity }}
          className="btn-primary-rose w-full mb-6 text-2xl font-black py-6 shadow-2xl relative overflow-hidden"
        >
          <motion.span
            animate={{ opacity: [1, 0.7, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
            className="inline-block"
          >
            Commencer le test ❤️
          </motion.span>
        </motion.button>

        {/* Easter egg hint - Interactive */}
        <motion.div
          variants={itemVariants}
          className="text-center"
          onClick={handleEasterEggClick}
          whileHover={{ scale: 1.2, rotate: 10 }}
          whileTap={{ scale: 0.8, rotate: -10 }}
        >
          <motion.button
            animate={{ rotate: [0, -10, 10, 0], y: [0, -3, 0] }}
            transition={{ duration: 3, repeat: Infinity }}
            className="text-4xl cursor-pointer hover:drop-shadow-lg transition-all"
            title="Easter egg"
          >
            💔
          </motion.button>
        </motion.div>

        {/* Footer hint */}
        <motion.p
          variants={itemVariants}
          animate={{ opacity: [0.6, 1, 0.6] }}
          transition={{ duration: 3, repeat: Infinity }}
          className="text-center text-xs text-gray-500 mt-8 font-medium"
        >
          Créé avec beaucoup d'amour (et un peu de folie) ✨
        </motion.p>
      </div>
    </motion.div>
  )
}

export default Landing
