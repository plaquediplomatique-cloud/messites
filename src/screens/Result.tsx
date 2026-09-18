import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Heart, Sparkles, Award } from 'lucide-react'
import { QuizAnswers } from '../App'
import { triggerConfetti, triggerHeartConfetti } from '../utils/confetti'
import { useSound } from '../hooks/useSound'

interface ResultProps {
  answers: QuizAnswers
  onRestart: () => void
  onEasterEgg: () => void
}

const Result: React.FC<ResultProps> = ({ onRestart, onEasterEgg }) => {
  const [phase, setPhase] = useState<'celebration' | 'contract' | 'personal'>('celebration')
  const { playSound } = useSound()

  useEffect(() => {
    triggerConfetti('heavy')
    triggerHeartConfetti()
    playSound('success')

    const timer1 = setTimeout(() => setPhase('contract'), 3500)
    const timer2 = setTimeout(() => setPhase('personal'), 7000)

    return () => {
      clearTimeout(timer1)
      clearTimeout(timer2)
    }
  }, [playSound])

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.2,
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

  if (phase === 'celebration') {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="min-h-screen flex items-center justify-center px-4"
      >
        <div className="text-center">
          <motion.div
            animate={{ scale: [0.5, 1.2, 1], rotate: [0, 360, 360] }}
            transition={{ duration: 1.5, ease: 'easeOut' }}
            className="inline-block mb-8"
          >
            <Heart className="w-32 h-32 text-rose-500 fill-current" />
          </motion.div>

          <motion.h1
            animate={{ scale: [0.8, 1.1, 1] }}
            transition={{ duration: 1 }}
            className="text-6xl md:text-7xl font-black text-gradient mb-4"
          >
            JE LE SAVAIS ❤️
          </motion.h1>

          <motion.p
            animate={{ opacity: [0, 1] }}
            transition={{ duration: 1, delay: 1 }}
            className="text-xl text-gray-700 font-semibold"
          >
            ✨ Félicitations ✨
          </motion.p>
        </div>
      </motion.div>
    )
  }

  if (phase === 'contract') {
    return (
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="min-h-screen flex items-center justify-center px-4 py-8"
      >
        <div className="w-full max-w-2xl">
          {/* Main message */}
          <motion.div
            variants={itemVariants}
            className="card-base p-8 mb-8 text-center"
          >
            <motion.div
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="mb-6"
            >
              <Award className="w-12 h-12 text-rose-500 mx-auto" />
            </motion.div>

            <h2 className="text-3xl font-black text-gray-800 mb-4">
              Contrat Officiel ⚖️
            </h2>

            <p className="text-gray-700 font-semibold text-lg mb-2">
              Félicitations, tu viens officiellement de renouveler ton abonnement à moi
            </p>

            <p className="text-gray-600 text-sm">
              pour une durée indéterminée.
            </p>
          </motion.div>

          {/* Contract details */}
          <motion.div
            variants={containerVariants}
            className="space-y-3 mb-8"
          >
            {[
              { label: 'Durée du contrat', value: '♾️ (infini)' },
              { label: 'Résiliation', value: '❌ Impossible' },
              { label: 'Support client', value: '🤕 Moi' },
              { label: 'Bisous inclus', value: '💋 Illimités' },
              { label: 'Câlins inclus', value: '🤗 À la demande' },
              { label: 'Disputes autorisées', value: '✅ Oui (avec résolution garantie)' },
            ].map((item, index) => (
              <motion.div
                key={index}
                variants={itemVariants}
                className="card-base p-4 flex items-center justify-between hover:bg-rose-50 transition-colors"
              >
                <span className="font-semibold text-gray-700">{item.label}</span>
                <span className="font-bold text-gradient">{item.value}</span>
              </motion.div>
            ))}
          </motion.div>

          {/* Footer */}
          <motion.div
            variants={itemVariants}
            className="card-base p-6 bg-gradient-to-r from-rose-50 to-pink-50"
          >
            <p className="text-center text-sm text-gray-600">
              Signé électroniquement le {new Date().toLocaleDateString('fr-FR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </p>
          </motion.div>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="min-h-screen flex items-center justify-center px-4 py-8"
    >
      <div className="w-full max-w-2xl space-y-8">
        {/* Main message */}
        <motion.div variants={itemVariants} className="card-base p-8 text-center">
          <motion.div
            animate={{ rotate: [0, 5, -5, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="mb-6"
          >
            <Sparkles className="w-12 h-12 text-rose-500 mx-auto" />
          </motion.div>

          <h2 className="text-3xl font-bold text-gray-800 mb-4">
            Un message sincère... 💕
          </h2>

          <motion.div
            variants={itemVariants}
            className="space-y-4 text-gray-700 leading-relaxed"
          >
            <p>
              Au-delà de tout ce goofy et cet humour absurde, tu dois savoir que tu es vraiment
              importante pour moi.
            </p>

            <p>
              Merci d'être toi. Merci de rire avec moi, même quand je fais des choses ridicules.
              Merci de rendre mes jours meilleurs juste en étant là.
            </p>

            <p>
              C'est facile de faire des blagues sur notre relation, mais la vérité, c'est que
              tu es ma personne préférée. Et je ne veux pas juste être ta copine pour la vie —
              je veux la vivre entièrement avec toi.
            </p>

            <p className="text-rose-600 font-bold text-lg pt-4">
              Je t'aime. Pour de vrai. 💗
            </p>
          </motion.div>
        </motion.div>

        {/* Buttons */}
        <motion.div variants={itemVariants} className="flex gap-4">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => triggerConfetti('medium')}
            className="flex-1 btn-primary-rose"
          >
            Encore des confettis 🎉
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onRestart}
            className="btn-ghost"
          >
            Recommencer
          </motion.button>
        </motion.div>

        {/* Easter egg hint */}
        <motion.div variants={itemVariants} className="text-center">
          <button
            onClick={onEasterEgg}
            className="text-3xl cursor-pointer hover:scale-125 transition-transform"
            title="Easter egg"
          >
            🎪
          </button>
        </motion.div>
      </div>
    </motion.div>
  )
}

export default Result
