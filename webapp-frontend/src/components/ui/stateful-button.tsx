"use client";
import React, { useState } from "react";
import { motion } from "framer-motion";
import { cn } from "../../lib/utils";

interface StatefulButtonProps {
  children: React.ReactNode;
  onClick?: () => Promise<void> | void;
  disabled?: boolean;
  className?: string;
  loadingText?: string;
  successText?: string;
}

export const StatefulButton: React.FC<StatefulButtonProps> = ({
  children,
  onClick,
  disabled = false,
  className = "",
  loadingText = "Creating...",
  successText = "Created!",
}) => {
  const [buttonState, setButtonState] = useState<"idle" | "loading" | "success">("idle");

  const handleClick = async () => {
    if (buttonState !== "idle" || disabled) return;

    setButtonState("loading");
    
    try {
      if (onClick) {
        await onClick();
      }
      setButtonState("success");
    } catch (error) {
      setButtonState("idle");
      console.error("Button action failed:", error);
    }
  };

  return (
    <motion.button
      className={cn(
        "relative h-12 w-full overflow-hidden rounded-md bg-black px-6 py-2 text-white transition-colors hover:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 focus:ring-offset-gray-50",
        disabled && "cursor-not-allowed opacity-50",
        className
      )}
      onClick={handleClick}
      disabled={disabled || buttonState !== "idle"}
      whileTap={{ scale: 0.985 }}
    >
      <motion.span
        key={buttonState}
        className="relative block h-full w-full font-semibold"
        initial={{ y: buttonState === "idle" ? 0 : -25 }}
        animate={{ y: 0 }}
        exit={{ y: 25 }}
        transition={{ ease: "easeInOut", duration: 0.25 }}
      >
        {buttonState === "loading" && (
          <motion.span
            className="flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.05 }}
          >
            <motion.div
              className="mr-2 h-4 w-4 rounded-full border-2 border-white border-t-transparent"
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            />
            {loadingText}
          </motion.span>
        )}
        {buttonState === "success" && (
          <motion.span
            className="flex items-center justify-center"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.05, type: "spring", stiffness: 500, damping: 25 }}
          >
            <motion.svg
              className="mr-2 h-4 w-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ delay: 0.2, duration: 0.3, ease: "easeInOut" }}
            >
              <motion.path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </motion.svg>
            {successText}
          </motion.span>
        )}
        {buttonState === "idle" && (
          <motion.span
            className="flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.05 }}
          >
            {children}
          </motion.span>
        )}
      </motion.span>
    </motion.button>
  );
};