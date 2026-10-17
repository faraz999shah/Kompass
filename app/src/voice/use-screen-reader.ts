import { useEffect, useState } from "react";
import { AccessibilityInfo } from "react-native";

/**
 * Whether VoiceOver or TalkBack is running, kept live as the learner toggles it.
 * The layout uses this to start voice mode without the learner asking.
 */
export function useScreenReaderEnabled(): boolean {
  const [screenReaderOn, setScreenReaderOn] = useState(false);

  useEffect(() => {
    let active = true;
    const listener = AccessibilityInfo.addEventListener(
      "screenReaderChanged",
      setScreenReaderOn,
    );
    void AccessibilityInfo.isScreenReaderEnabled().then((isOn) => {
      if (active) setScreenReaderOn(isOn);
    });
    return () => {
      active = false;
      listener.remove();
    };
  }, []);

  return screenReaderOn;
}
