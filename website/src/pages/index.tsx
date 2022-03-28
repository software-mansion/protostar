import React from 'react'
import Layout from '@theme/Layout'
import useDocusaurusContext from '@docusaurus/useDocusaurusContext'
import { HomepageHeader } from '../components'

export default function Home(): JSX.Element {
  const { siteConfig } = useDocusaurusContext()

  return (
    <Layout
      title={`Cairo smart contract development toolchain ${siteConfig.title}`}
      description='Protostar manages your dependencies, compiles your project, and runs test.'
    >
      <HomepageHeader />
    </Layout>
  )
}
