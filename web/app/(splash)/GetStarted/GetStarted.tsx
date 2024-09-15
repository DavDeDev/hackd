
"use client";

import { ConvexLogo } from "@/app/(splash)/GetStarted/ConvexLogo";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { motion } from "framer-motion"; // Framer Motion for animations
import Image from "next/image";
import Link from "next/link";
import { ReactNode } from "react";

export const GetStarted = () => {
  return (
    <motion.div 
      className="flex grow flex-col" 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      transition={{ duration: 1 }}
    >
      <div className="container mb-20 flex grow flex-col justify-center">
        <motion.h1 
          className="mb-8 mt-16 flex flex-col items-center text-center text-6xl font-extrabold leading-none tracking-tight"
          initial={{ y: -50, opacity: 0 }} 
          animate={{ y: 0, opacity: 1 }} 
          transition={{ duration: 1.2 }}
        >
          Find your next big team with
          <motion.div
            whileHover={{ rotate: 360 }}
            transition={{ duration: 2, ease: "easeInOut" }}
          >
            <Image
              src="/Hackd.png"
              alt="Logo"
              width={200}
              height={200}
              className="rounded-full"
            />
          </motion.div>
        </motion.h1>
        <motion.div 
          className="mb-8 text-center text-lg text-muted-foreground"
          initial={{ opacity: 0 }} 
          animate={{ opacity: 1 }} 
          transition={{ duration: 1.5 }}
        >
          Get the best person for your <strong>HACKATHON</strong>, <strong>JOB</strong> or any issue you might have with <strong>HACKD</strong>.
        </motion.div>
        <motion.div 
          className="mb-16 flex justify-center gap-4"
          initial={{ scale: 0.8, opacity: 0 }} 
          animate={{ scale: 1, opacity: 1 }} 
          transition={{ duration: 1, ease: "backInOut" }}
        >
          <Button asChild size="lg">
            <motion.div 
              whileHover={{ scale: 1.05, boxShadow: "0px 0px 15px rgba(0, 0, 0, 0.2)" }} 
              whileTap={{ scale: 0.95 }}
            >
              <Link href="/hacker">Hackers</Link>
            </motion.div>
          </Button>
          <Button asChild size="lg" variant="outline">
            <motion.div 
              whileHover={{ scale: 1.05, boxShadow: "0px 0px 15px rgba(0, 0, 0, 0.2)" }} 
              whileTap={{ scale: 0.95 }}
            >
              <Link href="/recruiting">Recruiters</Link>
            </motion.div>
          </Button>
        </motion.div>
      </div>
    </motion.div>
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
    <motion.div
      whileHover={{ scale: 1.05, boxShadow: "0px 0px 20px rgba(0, 0, 0, 0.3)" }}
      transition={{ duration: 0.3 }}
    >
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
    </motion.div>
  );
}
