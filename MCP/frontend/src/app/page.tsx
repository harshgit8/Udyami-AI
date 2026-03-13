"use client";

import { ArrowUpRight, Upload, Link as LinkIcon, Search } from "lucide-react";
import { Button, buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import Link from "next/link";
import Navbar from "@/components/navbar";
import { SignedIn, SignedOut, SignUpButton } from "@clerk/nextjs";

export default function Home() {
  return (
    <main className="min-h-screen">
      <Navbar />
      
      {/* Hero Section */}
      <section className="container mx-auto px-6 py-20 md:py-32">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-orange-500 to-yellow-500 bg-clip-text text-transparent">
            Udyami AI
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground mb-4">
            L1 Cache for Your LLMs
          </p>
          <p className="text-lg text-muted-foreground mb-10 max-w-2xl mx-auto">
            Upload your files and links, and Udyami AI ensures your AI never forgets.
            Lightning-fast search powered by Cerebras keeps your AI context sharp and always accessible.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <SignedOut>
              <SignUpButton mode="modal">
                <Button size="lg" className="text-base">
                  Get Started <ArrowUpRight className="ml-2 h-5 w-5" />
                </Button>
              </SignUpButton>
            </SignedOut>
            <SignedIn>
              <Link
                href="/dashboard"
                className={cn(buttonVariants({ size: "lg" }), "text-base")}
              >
                Go to Dashboard <ArrowUpRight className="ml-2 h-5 w-5" />
              </Link>
            </SignedIn>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-6 py-20 border-t">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
            How It Works
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-orange-100 dark:bg-orange-900/20 mb-4">
                <Upload className="h-8 w-8 text-orange-600 dark:text-orange-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Upload Content</h3>
              <p className="text-muted-foreground">
                Drop your documents, media files, or paste URLs. We support 20+ file types including PDF, DOCX, MP3, MP4, and more.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-yellow-100 dark:bg-yellow-900/20 mb-4">
                <LinkIcon className="h-8 w-8 text-yellow-600 dark:text-yellow-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Process & Store</h3>
              <p className="text-muted-foreground">
                Your content is automatically processed, summarized, and tagged using AI. Everything is securely stored and organized.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-orange-100 dark:bg-orange-900/20 mb-4">
                <Search className="h-8 w-8 text-orange-600 dark:text-orange-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3">AI-Powered Search</h3>
              <p className="text-muted-foreground">
                Connect via MCP to ChatGPT, Claude, or Cursor. Your AI assistants can now access your personal knowledge base instantly.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-6 py-20 border-t">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Supercharge Your AI?
          </h2>
          <p className="text-lg text-muted-foreground mb-8">
            Start building your personal knowledge base today.
          </p>
          
          <SignedOut>
            <SignUpButton mode="modal">
              <Button size="lg" className="text-base">
                Create Account <ArrowUpRight className="ml-2 h-5 w-5" />
              </Button>
            </SignUpButton>
          </SignedOut>
          <SignedIn>
            <Link
              href="/dashboard"
              className={cn(buttonVariants({ size: "lg" }), "text-base")}
            >
              Go to Dashboard <ArrowUpRight className="ml-2 h-5 w-5" />
            </Link>
          </SignedIn>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8">
        <div className="container mx-auto px-6 text-center text-sm text-muted-foreground">
          <p>© 2026 Udyami AI. All rights reserved.</p>
        </div>
      </footer>
    </main>
  );
}
