import React from 'react'
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
              width={star.size}
            />
          )
        })}
      </div>
    </div>
  )
}

function StarIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 189 188" fill="none" xmlns="http://www.w3.org/2000/svg" {...props}>
      <path
        d="M92.6409 9.68751C93.3086 8.00397 95.6914 8.00397 96.3591 9.68751L119.494 68.0196C119.698 68.5346 120.107 68.9418 120.623 69.1441L179.252 92.1381C180.946 92.802 180.946 95.1979 179.252 95.8619L120.623 118.856C120.107 119.058 119.698 119.465 119.494 119.98L96.3591 178.312C95.6914 179.996 93.3086 179.996 92.6409 178.312L69.5058 119.98C69.3015 119.465 68.8928 119.058 68.3769 118.856L9.74752 95.8619C8.05449 95.198 8.05448 92.8021 9.74751 92.1381L68.3769 69.1441C68.8927 68.9418 69.3015 68.5346 69.5058 68.0196L92.6409 9.68751Z"
        fill="#87CCE8"/>
    </svg>
  )
}
