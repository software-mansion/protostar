import { useColorMode } from "@docusaurus/theme-common";
import clsx from "clsx";
import React from "react";
import styles from "./styles.module.css";

type HomepageFeatureProps = {
  title: string;
  description: string;
  renderIcon: () => JSX.Element;
};

export function HomepageFeature({
  title,
  description,
  renderIcon,
}: HomepageFeatureProps) {
  const { isDarkTheme } = useColorMode();

  return (
    <div className={styles.container}>
      <div
        className={clsx([
          styles.iconContainer,
          { [styles["bg-primary"]]: !isDarkTheme },
        ])}
      >
        {renderIcon()}
      </div>
      <h1>{title}</h1>
      <span>{description}</span>
    </div>
  );
}
