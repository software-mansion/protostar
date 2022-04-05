import Link from '@docusaurus/Link'
import useDocusaurusContext from '@docusaurus/useDocusaurusContext'
import clsx from 'clsx'
import React from 'react'
import styles from './styles.module.css'
import { useThemeConfig } from '@docusaurus/theme-common'
import ThemedImage from '@theme/ThemedImage'
import { Stars } from '../Stars'
import useBaseUrl from '@docusaurus/useBaseUrl'

export function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext()

  const { navbar } = useThemeConfig()
  const { logo } = navbar

  return (
    <header className={clsx('hero', styles.heroBanner)}>
      <Stars
        className={clsx(styles.stars)}
        data={[
          { top: '20%', left: '20%', opacity: 0.7, size: 16 },
          { top: '25%', left: '95%', opacity: 0.4, size: 8 },
          { top: '40%', left: '60%', opacity: 0.4, size: 18 },
          { top: '80%', left: '70%', opacity: 0.25, size: 10 },
          { top: '90%', left: '10%', opacity: 0.7, size: 20 },
        ]}
      />
      <div className={clsx(styles.contentContainer)}>
        <div className={styles.logoContentContainer}>
          <ThemedImage
            sources={{
              light: useBaseUrl(logo.src),
              dark: useBaseUrl(logo.srcDark),
            }}
            height={96}
            width={96}
            alt={logo.alt}
          />
          <ThemedImage
            style={{ margin: '12px 0 24px 0' }}
            sources={{
              light: useBaseUrl('img/protostar-title--dark.svg'),
              dark: useBaseUrl('img/protostar-title--light.svg'),
            }}
            width={224}
          />
        </div>

        <p className='hero__subtitle'>{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className='button button--secondary button--lg'
            to='/docs/tutorials/introduction'
          >
            Get Started
          </Link>
        </div>
      </div>
      <Stars
        className={clsx(styles.stars)}
        data={[
          { top: '0%', left: '80%', opacity: 0.4, size: 16 },
          { top: '10%', left: '10%', opacity: 0.2, size: 8 },
          { top: '40%', left: '40%', opacity: 0.4, size: 12 },
          { top: '90%', left: '0%', opacity: 0.4, size: 16 },
          { top: '100%', left: '90%', opacity: 0.7, size: 16 },
        ]}
      />
    </header>
  )
}
