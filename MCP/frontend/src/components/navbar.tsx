import { cn } from "@/lib/utils";
import Link from "next/link";
import { Button } from "./ui/button";
import {
  SignedIn,
  SignedOut,
  SignInButton,
  SignUpButton,
  UserButton,
} from "@clerk/nextjs";

const Navbar = () => {
  return (
    <nav className="flex justify-between items-center max-w-7xl mx-auto mt-5 mb-2">
      <div className="flex items-center gap-6">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-orange-500 to-yellow-500 bg-clip-text text-transparent">
          Udyami AI
        </h1>
      </div>
      <div className="flex gap-4 items-center">
        <SignedOut>
          <SignInButton mode="modal">
            <Button
              className={cn(
                "font-bold uppercase font-mono tracking-wide cursor-pointer",
              )}
              variant="outline"
            >
              Login
            </Button>
          </SignInButton>
          <SignUpButton mode="modal">
            <Button
              className={cn(
                "font-bold uppercase font-mono tracking-wide cursor-pointer",
              )}
              variant="default"
            >
              Create Account
            </Button>
          </SignUpButton>
        </SignedOut>
        <SignedIn>
          <Link href="/dashboard">
            <Button
              className={cn(
                "font-bold uppercase font-mono tracking-wide cursor-pointer",
              )}
              variant="default"
            >
              Dashboard
            </Button>
          </Link>
          <UserButton />
        </SignedIn>
      </div>
    </nav>
  );
};

export default Navbar;
