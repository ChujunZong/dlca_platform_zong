
import React, { useId } from "react";
import "./InfoTip.css";

export default function InfoTip({
  text,
  title = "Info",
  placement = "top",
}) {
  const tipId = useId();

  return (
    <span className={`infotip infotip--${placement}`}>
      <button
        type="button"
        className="infotip__btn"
        aria-label={title}
        aria-describedby={tipId}
      >
        ?
      </button>

      <span id={tipId} role="tooltip" className="infotip__bubble">
        <span className="infotip__title">{title}</span>
        <span className="infotip__text">{text}</span>
      </span>
    </span>
  );
}