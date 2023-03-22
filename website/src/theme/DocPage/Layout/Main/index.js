import React from 'react'
import Main from '@theme-original/DocPage/Layout/Main'
import Giscus from '@giscus/react'
import { useColorMode } from '@docusaurus/theme-common'
import useDocusaurusContext from '@docusaurus/useDocusaurusContext'
import { useLocation } from 'react-router-dom'

export default function MainWrapper({ children, ...props }) {
  const { colorMode } = useColorMode()
  const { siteConfig } = useDocusaurusContext()
  const location = useLocation()

  return (
    <Main {...props}>
      {children}
      <div className='row margin-top--md'>
        <div className='col'>
          <Giscus
            key={location.pathname}
            repo='software-mansion/protostar'
            repoId='R_kgDOGw_HxA'
            categoryId='DIC_kwDOGw_HxM4CSDJD'
            category='Documentation'
            mapping='pathname'
            reactionsEnabled='0'
            emitMetadata='0'
            inputPosition='top'
            theme={colorMode}
            lang={siteConfig.i18n.defaultLocale}
            loading='lazy'
            strict
          />
        </div>
        <div className='col col--3' />
      </div>
    </Main>
  )
}
