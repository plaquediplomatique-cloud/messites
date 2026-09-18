import React from 'react'
import { motion } from 'framer-motion'

const BackgroundElements: React.FC = () => {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden">
      {/* Animated gradient orbs */}
      <motion.div
        className="absolute top-20 right-10 w-96 h-96 bg-gradient-to-br from-rose-200 to-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
        animate={{
          scale: [1, 1.1, 0.9, 1],
          x: [0, 50, -30, 0],
          y: [0, 30, -50, 0],
        }}
        transition={{ duration: 8, repeat: Infinity }}
      />

      <motion.div
        className="absolute bottom-20 left-10 w-80 h-80 bg-gradient-to-tr from-purple-200 to-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-15"
        animate={{
          scale: [1, 0.9, 1.1, 1],
          x: [0, -40, 30, 0],
          y: [0, -40, 50, 0],
        }}
        transition={{ duration: 10, repeat: Infinity, delay: 1 }}
      />

      <motion.div
        className="absolute top-1/2 left-1/3 w-96 h-96 bg-gradient-to-br from-yellow-100 to-rose-100 rounded-full mix-blend-multiply filter blur-3xl opacity-10"
        animate={{
          scale: [1, 1.15, 0.85, 1],
          x: [0, 60, -50, 0],
        }}
        transition={{ duration: 12, repeat: Infinity, delay: 2 }}
      />

      {/* Floating stars */}
      {[...Array(15)].map((_, i) => (
        <motion.div
          key={`star-${i}`}
          className="absolute text-3xl"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0, 0.7, 0],
            scale: [0.5, 1.2, 0.5],
          }}
          transition={{
            duration: Math.random() * 3 + 2,
            repeat: Infinity,
            delay: Math.random() * 5,
          }}
        >
          ✨
        </motion.div>
      ))}

      {/* Grid pattern - subtle */}
      <div
        className="absolute inset-0 opacity-5"
        style={{
          backgroundImage: 'linear-gradient(rgba(236, 72, 153, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(236, 72, 153, 0.1) 1px, transparent 1px)',
          backgroundSize: '50px 50px',
        }}
      />
    </div>
  )
}

export default BackgroundElements
