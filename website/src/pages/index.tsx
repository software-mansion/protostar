import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Layout from "@theme/Layout";
import React from "react";
import TestIcon from "../../static/img/beaker.svg";
import PackageIcon from "../../static/img/package-dependencies.svg";
import ToolsIcon from "../../static/img/tools.svg";
import { HomepageFeature, HomepageHeader } from "../components";
import { HomepageContent } from "../components/HomepageContent/HomepageContent";

export default function Home(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();

  return (
    <Layout
      title={`Cairo smart contract development toolchain ${siteConfig.title}`}
      description="Protostar manages your dependencies, compiles your project, and runs test."
    >
      <HomepageHeader />
      <HomepageContent>
        <HomepageFeature
          renderIcon={() => (
            <TestIcon className="text-secondary" width={64} height={64} />
          )}
          title="Test"
          description="Test runner and cheatcodes make simplify testing"
        />
        <HomepageFeature
          renderIcon={() => (
            <ToolsIcon className="text-secondary" width={64} height={64} />
          )}
          title="Compile"
          description="No need for setting up Cairo and StarkNet"
        />
        <HomepageFeature
          renderIcon={() => (
            <PackageIcon className="text-secondary" width={64} height={64} />
          )}
          title="Install"
          description="Add, update, and remove dependencies"
        />
      </HomepageContent>
    </Layout>
  );
}
