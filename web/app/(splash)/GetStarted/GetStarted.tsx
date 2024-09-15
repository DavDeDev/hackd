import { ConvexLogo } from "@/app/(splash)/GetStarted/ConvexLogo";
import { Code } from "@/components/Code";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  CodeIcon,
  MagicWandIcon,
  PlayIcon,
  StackIcon,
} from "@radix-ui/react-icons";
import Image from "next/image";
import Link from "next/link";
import { ReactNode } from "react";

export const GetStarted = () => {
  return (
    <div className="flex grow flex-col">
      <div className="container mb-20 flex grow flex-col justify-center">
        <h1 className="mb-8 mt-16 flex flex-col items-center  text-center text-6xl font-extrabold leading-none tracking-tight">
          Find your next big team with
          {/* <ConvexLogo width={377} height={44} /> */}
          <Image
            src="/Hackd.png"
            alt="Logo"
            width={200}
            height={200}
            className="rounded-full"/>
        </h1>
        <div className="mb-8 text-center text-lg text-muted-foreground">
          Get the best person for your, <strong>HACKATHON</strong>, <strong>JOB</strong> or any issue you might have with <strong>HACKD</strong>
        </div>
        <div className="mb-16 flex justify-center gap-4">
          <Button asChild size="lg">
            <Link href="/hacker">Hackers</Link>
          </Button>
          <Button asChild size="lg" variant="outline">
            <Link href="https://docs.convex.dev/home">Recruiters</Link>
          </Button>
        </div>
      </div>
    </div>
  );
};

function Resource({
  title,
  children,
  href,
}: {
  title: string;
  children: ReactNode;
  href: string;
}) {
  return (
    <Button
      asChild
      variant="secondary"
      className="flex h-auto flex-col items-start justify-start gap-4 whitespace-normal p-4 font-normal"
    >
      <Link href={href}>
        <div className="text-sm font-bold">{title}</div>
        <div className="text-muted-foreground">{children}</div>
      </Link>
    </Button>
  );
}
