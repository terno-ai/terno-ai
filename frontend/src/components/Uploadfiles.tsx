import { useState } from "react";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../components/ui/AlertDialog";
import CSRFToken from "../utils/csrftoken";
import { fileUpload } from "../utils/api";

const Uploadfiles = ({
  open,
  setOpen,
  dsId,
}: {
  open: boolean;
  setOpen: (open: boolean) => void;
  dsId: string;
}) => {
  const [files, setFiles] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files;
    setFiles(selectedFiles);
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    if (files) {
      const formData = new FormData();
      for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
      }
      formData.append("dsId", dsId);

      const response = await fileUpload(formData);
      if (response["status"] === "success") {
        console.log("done");
      } else {
        setError(response["error"]);
      }
    }
    setLoading(false);
    setOpen(false);
  };

  return (
    <AlertDialog
      open={open}
      onOpenChange={(isOpen) => {
        setOpen(isOpen);
      }}
    >
      <AlertDialogContent className="bg-white m-2">
        <AlertDialogHeader>
          <AlertDialogTitle className="text-center">
            Add CSV File
          </AlertDialogTitle>
          <AlertDialogDescription>
            <div className="w-[400px]">
              <form method="post">
                <CSRFToken />
                <div className="my-4">
                  <label
                    htmlFor="name"
                    className="my-4 text-black text-base font-semibold leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                  >
                    Choose CSV files to upload:
                  </label>
                  <div className="rounded-md bg-slate-100 hover:drop-shadow-sm focus-within:ring-1 focus-within:ring-sky-500 focus-within:hover:drop-shadow-none">
                    <input
                      type="file"
                      accept=".csv"
                      multiple
                      onChange={handleFileInput}
                    />
                  </div>
                </div>

                {error && (
                  <div className="text-red-500 text-sm mt-2">{error}</div>
                )}
                <div className="">
                  <AlertDialogFooter>
                    <div
                      onClick={() => {
                        console.log("Closing modal...");
                        setTimeout(() => {
                          setOpen(false);
                        }, 50);
                      }}
                      className="cursor-pointer px-4 py-2 border rounded-md bg-gray-200 hover:bg-gray-300 transition-colors"
                    >
                      Cancel
                    </div>
                    <button
                      type="submit"
                      onClick={handleUpload}
                      className="btn px-4 py-1 text-white border rounded-md bg-slate-800 hover:bg-slate-700 transition-colors"
                    >
                      {loading ? "Submitting..." : "Upload"}
                    </button>
                  </AlertDialogFooter>
                </div>
              </form>
            </div>
          </AlertDialogDescription>
        </AlertDialogHeader>
      </AlertDialogContent>
    </AlertDialog>
  );
};

export default Uploadfiles;
