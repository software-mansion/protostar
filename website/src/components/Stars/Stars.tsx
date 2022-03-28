import React from 'react'
import { StarIcon } from '../StarIcon'
import styles from './styles.module.css'

interface StarsProps {
  className?: string
  data: {
    top: number | string
    left: number | string
    opacity: number
    size: number
  }[]
}

export function Stars({ className, data }: StarsProps) {
  return (
    <div className={className}>
      <div className={styles.container}>
        {data.map((star) => {
          return (
            <StarIcon
              key={star.top.toString() + star.left.toString()}
              className={styles.star}
              style={star}
              size={star.size}
            />
          )
        })}
      </div>
    </div>
  )
}
