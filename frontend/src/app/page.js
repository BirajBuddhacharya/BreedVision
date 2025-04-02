"use client";
import React, { useState, useEffect } from "react";
import { FileUpload } from "@/components/ui/file-upload";
import { toast } from "react-toastify";
import axios from 'axios';
import { motion } from 'framer-motion'

export default function Home() {
  const [file, setFile] = useState(null);
  const [apiData, setApiData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [breedImage, setBreedImage] = useState(null)

  const handleFileUpload = (files) => {
    setFile(files[0]);
  };

  useEffect(() => {
    // only run when file is not empty 
    if (!file) return;

    const fetchData = async () => {
      setLoading(true)
      try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await axios({
          url: 'http://127.0.0.1:8000/predict/',
          method: 'POST',
          headers: {
            "Content-Type": "multipart/form-data",
          },
          data: formData
        })

        const result = response.data
        setApiData(result)

        toast.success(result['message'])

      }
      catch (error) { toast.error(`Error: ${error}`) }
      finally { setLoading(false) }
    }

    fetchData()
  }, [file])

  // Debugging: Logs breedImage only when it changes
  useEffect(() => {
    console.log("Updated breedImage:", breedImage);
  }, [breedImage]);

  return (
    <main className="flex h-screen items-center justify-center flex-col gap-10">
      { !apiData ? (<span className="text-3xl text-center w-full">Know Your Dog's Breed</span>) : null }
      <motion.div
        layout
        transition={{ type: "spring", stiffness: 200, damping: 20 }}
        className="p-4 border border-dashed bg-white dark:bg-black border-neutral-200 dark:border-neutral-800 rounded-2xl"
      >
        {!apiData ? (
          <div>
            <FileUpload onChange={handleFileUpload} loading={loading} />
          </div>
        ) : (
          <div className="h-[25rem] w-[40rem] grid grid-cols-2 gap-2">
            <div className="bg-blue-500">
              {/* <Image>

              </Image> */}
            </div>
            <div className="flex justify-center items-center flex-col gap-2">
              <span>Your dogs breed is</span>
              <div className="text-5xl font-bold">{apiData.breed}</div>
              <div className="text-center">{apiData.description}</div>
            </div>
          </div>
        )}
      </motion.div>
    </main>
  );
}
