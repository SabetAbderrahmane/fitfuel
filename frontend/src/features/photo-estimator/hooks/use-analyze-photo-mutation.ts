"use client";

import { useMutation } from "@tanstack/react-query";

import { analyzePhotoFile } from "@/features/photo-estimator/api/photo-estimator";
import type { PhotoAnalysisResult } from "@/features/photo-estimator/types/photo-estimator.types";

type Variables = {
  accessToken: string;
  file: File;
};

export function useAnalyzePhotoMutation() {
  return useMutation<PhotoAnalysisResult, Error, Variables>({
    mutationFn: async ({ accessToken, file }) =>
      analyzePhotoFile(accessToken, file),
  });
}