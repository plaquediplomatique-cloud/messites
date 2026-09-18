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
    playSound('ding')
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
        {/* Header */}
        <motion.div variants={itemVariants} className="text-center mb-12">
          <motion.div
            className="inline-block mb-6"
            animate={{ rotate: [0, -5, 5, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <Heart className="w-16 h-16 text-rose-500 fill-current" />
          </motion.div>

          <motion.h1 className="text-4xl md:text-5xl font-black mb-2 text-text-gradient">
            Bienvenue ❤️
          </motion.h1>

          <motion.p className="text-gray-600 text-lg mb-2">
            Évaluation officielle
          </motion.p>

          <motion.p className="text-sm text-gray-500 leading-relaxed">
            Cette évaluation déterminera si tu es juridiquement, scientifiquement et émotionnellement
            autorisée à être ma copine pour la vie.
          </motion.p>
        </motion.div>

        {/* Card */}
        <motion.div
          variants={itemVariants}
          className="card-base p-8 mb-8 space-y-4"
          whileHover={{ y: -4, boxShadow: '0 20px 40px rgba(236, 72, 153, 0.15)' }}
        >
          <div className="space-y-2 text-center">
            <p className="text-sm font-semibold text-rose-600">Statut : En attente</p>
            <div className="w-full h-1 bg-gray-200 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-rose-500 to-pink-500"
                animate={{ width: '0%' }}
                transition={{ duration: 0.5 }}
                style={{ width: '0%' }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-2">Prêt à tester ta loyauté ? 👀</p>
          </div>
        </motion.div>

        {/* Button */}
        <motion.button
          variants={itemVariants}
          onClick={handleStartClick}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="btn-primary-rose w-full mb-4 text-lg"
        >
          Commencer le test ❤️
        </motion.button>

        {/* Easter egg hint */}
        <motion.div
          variants={itemVariants}
          className="text-center"
          onClick={handleEasterEggClick}
          whileHover={{ scale: 1.1 }}
        >
          <button className="text-2xl cursor-pointer hover:scale-125 transition-transform" title="Easter egg">
            💔
          </button>
        </motion.div>

        {/* Footer hint */}
        <motion.p
          variants={itemVariants}
          className="text-center text-xs text-gray-400 mt-8"
        >
          Créé avec beaucoup d'amour (et un peu de folie) ✨
        </motion.p>
      </div>
    </motion.div>
  )
}

export default Landing
