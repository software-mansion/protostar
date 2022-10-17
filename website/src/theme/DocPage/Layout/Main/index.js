import React from 'react'
import Main from '@theme-original/DocPage/Layout/Main'
import Giscus from '@giscus/react'

export default function MainWrapper({ children, ...props }) {
  return (
    <Main {...props}>
      {children}
      <div style={{ height: '32px' }} />
      <Giscus
        repo='software-mansion/protostar'
        repoId='R_kgDOGw_HxA'
        categoryId='DIC_kwDOGw_HxM4CBC8m'
        category='Announcements'
        mapping='title'
        reactionsEnabled='1'
        emitMetadata='0'
        inputPosition='top'
        theme='light'
        lang='en'
        loading='lazy'
      />
    </Main>
  )
}
