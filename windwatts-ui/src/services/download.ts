export const downloadBlobAsFile = (blob: Blob, filename: string) => {
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = filename;

    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);
};

export const generateWindDataFilename = (gridLat: number, gridLng: number) =>{
    if (gridLat === undefined || gridLng === undefined){
        return `wind_data_${Date.now()}.csv`; // fallback with timestamp
    }
    return `wind_data_${gridLat.toFixed(3)}_${gridLng.toFixed(3)}.csv`
}

export const downloadWindDataCSV = async (
  response: Response,
  gridLat: number,
  gridLng: number
) => {
  try {
    const blob = await response.blob();
    const filename = generateWindDataFilename(gridLat, gridLng);
    downloadBlobAsFile(blob, filename);
    return { success: true, filename };
  } catch (error) {
    console.error('Failed to process download:', error);
    throw error;
  }
};