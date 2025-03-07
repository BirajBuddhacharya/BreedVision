"use client";
import React, { useState } from "react";
import { FileUpload } from "@/components/ui/file-upload";

export default function Home() {
  const [files, setFiles] = useState([]);
  const handleFileUpload = (files) => {
    setFiles(files);
    console.log(files);
  };

  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start">
        <div className="text-3xl text-center w-full">Know your dogs breed</div>
        <div
          className="w-[30rem] max-w-4xl mx-auto min-h-70 border border-dashed bg-white dark:bg-black border-neutral-200 dark:border-neutral-800 rounded-2xl">
          <FileUpload onChange={handleFileUpload} />
        </div>
      </main>
    </div>
  );
}
