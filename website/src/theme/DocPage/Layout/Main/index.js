import React from 'react'
import Main from '@theme-original/DocPage/Layout/Main'
import Giscus from '@giscus/react'
import { useColorMode } from '@docusaurus/theme-common'

export default function MainWrapper({ children, ...props }) {
  const { isDarkTheme } = useColorMode()

  return (
    <Main {...props}>
      {children}
      <div style={{ height: '32px' }} />
      <div className='row'>
        <div className='col'>
          <Giscus
            repo='software-mansion/protostar'
            repoId='R_kgDOGw_HxA'
            categoryId='DIC_kwDOGw_HxM4CSDJD'
            category='Documentation'
            mapping='title'
            reactionsEnabled='0'
            emitMetadata='0'
            inputPosition='top'
            theme={isDarkTheme ? 'dark' : 'light'}
            lang='en'
            loading='lazy'
          />
        </div>
        <div className='col col--3' />
      </div>
    </Main>
  )
}
