import { motion, AnimatePresence } from "framer-motion";
import { Download, Copy, Check, ThumbsUp, ThumbsDown, Send, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useState } from "react";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  onDownload?: () => void;
  isLatestAssistant?: boolean;
  isStreaming?: boolean;
  onFeedback?: (type: "good" | "bad", feedback?: string) => void;
  onRetry?: (feedback: string) => void;
}

export function ChatMessage({
  role,
  content,
  onDownload,
  isLatestAssistant,
  isStreaming,
  onFeedback,
  onRetry,
}: ChatMessageProps) {
  const isUser = role === "user";
  const [copied, setCopied] = useState(false);
  const [feedbackGiven, setFeedbackGiven] = useState<"good" | "bad" | null>(null);
  const [showFeedbackInput, setShowFeedbackInput] = useState(false);
  const [feedbackText, setFeedbackText] = useState("");

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleThumbsUp = () => {
    setFeedbackGiven("good");
    setShowFeedbackInput(false);
    onFeedback?.("good");
  };

  const handleThumbsDown = () => {
    setFeedbackGiven("bad");
    setShowFeedbackInput(true);
    onFeedback?.("bad");
  };

  const handleRetryWithFeedback = () => {
    if (feedbackText.trim()) {
      onRetry?.(feedbackText.trim());
      setShowFeedbackInput(false);
      setFeedbackText("");
      setFeedbackGiven(null);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}
    >
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center overflow-hidden ${
          isUser ? "bg-foreground" : "bg-foreground"
        }`}
      >
        {isUser ? (
          <span className="text-xs font-bold text-background">You</span>
        ) : (
          <img src="/logo.svg" alt="Udyami" className="w-5 h-5 invert" />
        )}
      </div>
      <div className={`flex-1 max-w-[85%] ${isUser ? "flex flex-col items-end" : ""}`}>
        <div
          className={`inline-block p-4 rounded-2xl ${
            isUser
              ? "bg-foreground text-background rounded-br-md"
              : "bg-muted/60 rounded-bl-md"
          }`}
        >
          {isUser ? (
            <p className="text-sm whitespace-pre-wrap leading-relaxed">{content}</p>
          ) : (
            <div className="chat-markdown text-sm">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  h1: ({ children }) => (
                    <h1 className="text-lg font-bold tracking-tight mt-4 mb-2 first:mt-0 text-foreground">{children}</h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className="text-base font-semibold tracking-tight mt-3.5 mb-1.5 first:mt-0 text-foreground">{children}</h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className="text-sm font-semibold mt-3 mb-1 first:mt-0 text-foreground">{children}</h3>
                  ),
                  h4: ({ children }) => (
                    <h4 className="text-sm font-medium mt-2.5 mb-1 first:mt-0 text-foreground">{children}</h4>
                  ),
                  p: ({ children }) => (
                    <p className="leading-relaxed mb-2 last:mb-0">{children}</p>
                  ),
                  ul: ({ children }) => (
                    <ul className="list-disc list-outside ml-4 mb-2 space-y-0.5 last:mb-0">{children}</ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="list-decimal list-outside ml-4 mb-2 space-y-0.5 last:mb-0">{children}</ol>
                  ),
                  li: ({ children }) => (
                    <li className="leading-relaxed pl-0.5">{children}</li>
                  ),
                  strong: ({ children }) => (
                    <strong className="font-semibold text-foreground">{children}</strong>
                  ),
                  em: ({ children }) => (
                    <em className="italic text-muted-foreground">{children}</em>
                  ),
                  del: ({ children }) => (
                    <del className="line-through text-muted-foreground">{children}</del>
                  ),
                  code: ({ className, children, ...props }) => {
                    const isBlock = className?.includes("language-");
                    if (isBlock) {
                      return (
                        <div className="my-2 rounded-lg overflow-hidden border border-border">
                          <div className="bg-muted/80 px-3 py-1 text-[10px] font-mono text-muted-foreground uppercase tracking-wider border-b border-border">
                            {className?.replace("language-", "") || "code"}
                          </div>
                          <pre className="p-3 overflow-x-auto bg-muted/40">
                            <code className="text-xs font-mono leading-relaxed" {...props}>{children}</code>
                          </pre>
                        </div>
                      );
                    }
                    return (
                      <code className="px-1.5 py-0.5 rounded-md bg-muted text-xs font-mono text-foreground" {...props}>
                        {children}
                      </code>
                    );
                  },
                  pre: ({ children }) => <>{children}</>,
                  blockquote: ({ children }) => (
                    <blockquote className="border-l-2 border-primary/40 pl-3 my-2 text-muted-foreground italic">
                      {children}
                    </blockquote>
                  ),
                  table: ({ children }) => (
                    <div className="my-3 overflow-x-auto rounded-lg border border-border">
                      <table className="w-full text-xs border-collapse">{children}</table>
                    </div>
                  ),
                  thead: ({ children }) => (
                    <thead className="bg-muted/70">{children}</thead>
                  ),
                  tbody: ({ children }) => (
                    <tbody className="divide-y divide-border/50">{children}</tbody>
                  ),
                  tr: ({ children }) => (
                    <tr className="hover:bg-muted/30 transition-colors">{children}</tr>
                  ),
                  th: ({ children }) => (
                    <th className="px-3 py-2 text-left font-semibold text-foreground text-xs whitespace-nowrap">{children}</th>
                  ),
                  td: ({ children }) => (
                    <td className="px-3 py-2 text-xs whitespace-nowrap">{children}</td>
                  ),
                  hr: () => <hr className="my-3 border-border" />,
                  a: ({ href, children }) => (
                    <a href={href} target="_blank" rel="noopener noreferrer" className="text-primary underline underline-offset-2 hover:text-primary/80 transition-colors">
                      {children}
                    </a>
                  ),
                }}
              >
                {content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Action bar for assistant messages */}
        {!isUser && content.length > 20 && !isStreaming && (
          <div className="mt-1.5 flex flex-col gap-1.5">
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCopy}
                className="text-xs text-muted-foreground hover:text-foreground h-7 px-2 rounded-lg"
              >
                {copied ? <Check className="w-3 h-3 mr-1" /> : <Copy className="w-3 h-3 mr-1" />}
                {copied ? "Copied" : "Copy"}
              </Button>
              {onDownload && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onDownload}
                  className="text-xs text-muted-foreground hover:text-foreground h-7 px-2 rounded-lg"
                >
                  <Download className="w-3 h-3 mr-1" />
                  PDF
                </Button>
              )}

              {/* Feedback buttons - show on latest assistant message */}
              {isLatestAssistant && onFeedback && (
                <>
                  <div className="w-px h-4 bg-border mx-1" />
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleThumbsUp}
                    className={`h-7 w-7 p-0 rounded-lg transition-all ${
                      feedbackGiven === "good"
                        ? "text-[hsl(142,71%,45%)] bg-[hsl(142,71%,45%/0.1)]"
                        : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    <ThumbsUp className="w-3.5 h-3.5" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleThumbsDown}
                    className={`h-7 w-7 p-0 rounded-lg transition-all ${
                      feedbackGiven === "bad"
                        ? "text-destructive bg-destructive/10"
                        : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    <ThumbsDown className="w-3.5 h-3.5" />
                  </Button>
                  {feedbackGiven === "good" && (
                    <motion.span
                      initial={{ opacity: 0, x: -4 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="text-[10px] text-muted-foreground ml-1"
                    >
                      Thanks for the feedback!
                    </motion.span>
                  )}
                </>
              )}
            </div>

            {/* Feedback input for bad response */}
            <AnimatePresence>
              {showFeedbackInput && onRetry && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <div className="flex gap-2 p-2.5 rounded-xl border border-border bg-background">
                    <Textarea
                      value={feedbackText}
                      onChange={(e) => setFeedbackText(e.target.value)}
                      placeholder="What was wrong? How should it improve?"
                      className="min-h-[36px] max-h-[80px] text-xs resize-none rounded-lg border-0 bg-muted/40 focus-visible:ring-1"
                      rows={1}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                          e.preventDefault();
                          handleRetryWithFeedback();
                        }
                      }}
                    />
                    <Button
                      size="sm"
                      onClick={handleRetryWithFeedback}
                      disabled={!feedbackText.trim()}
                      className="h-9 px-3 rounded-lg text-xs gap-1.5"
                    >
                      <RotateCcw className="w-3 h-3" />
                      Retry
                    </Button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      </div>
    </motion.div>
  );
}
