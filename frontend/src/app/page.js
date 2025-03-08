"use client";
import React, { useState, useEffect } from "react";
import { FileUpload } from "@/components/ui/file-upload";

export default function Home() {
  const [file, setFile] = useState(null);
  const [apiData, setApiData] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleFileUpload = (f) => {
    setFile(f);
  };

  useEffect(() => {
    // only run when file is not empty 
    if (!file) return;

    const fetchData = async () => {
      setLoading(true)
      try {
        const response = await fetch('http://127.0.0.1:8000/test')
        if (!response.ok) {
          throw new Error("Error fetching data")
        }

        const result = await response.json()
        setApiData(result)
        console.log(result['message'])

      }
      catch (error) { console.log(error) }
      finally { setLoading(false) }
    }

    fetchData()
  }, [file])

  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start">
        <div className="text-3xl text-center w-full">Know your dogs breed</div>
        {apiData ? (
          <div>{apiData.message}</div>
        ) : (
          <div className="w-[30rem] max-w-4xl mx-auto min-h-70 border border-dashed bg-white dark:bg-black border-neutral-200 dark:border-neutral-800 rounded-2xl">
            <FileUpload onChange={handleFileUpload} loading={loading} />
          </div>
        )}
      </main>
    </div>
  );
}
