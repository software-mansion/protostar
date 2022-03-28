import React from 'react'
import ThemedImage from '@theme/ThemedImage'
import useBaseUrl from '@docusaurus/useBaseUrl'

interface StarIconProps {
  className?: string
  size?: number
  style?: React.CSSProperties
}

export function StarIcon({ size = 24, className, style }: StarIconProps) {
  return (
    <ThemedImage
      className={className}
      sources={{
        light: useBaseUrl('/img/star--dark.png'),
        dark: useBaseUrl('/img/star--light.png'),
      }}
      height={size}
      width={size}
      alt='star'
      style={style}
    />
  )
}
