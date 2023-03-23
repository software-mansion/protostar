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
  return (
    <div className={styles.container}>
      <div
        className={styles.iconContainer}
      >
        {renderIcon()}
      </div>
      <h1 className="text--primary">{title}</h1>
      <span>{description}</span>
    </div>
  );
}
