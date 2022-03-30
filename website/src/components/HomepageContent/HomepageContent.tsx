import clsx from "clsx";
import React from "react";
import styles from "./styles.module.css";

interface HomepageContentProps {
  children: JSX.Element | JSX.Element[];
}

export function HomepageContent({ children }: HomepageContentProps) {
  return (
    <div className={clsx(["container", styles.container])}>{children}</div>
  );
}
