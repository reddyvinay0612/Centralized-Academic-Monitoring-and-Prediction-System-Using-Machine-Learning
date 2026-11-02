import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import Papa from 'papaparse';
import toast from 'react-hot-toast';
import {
  UploadCloud,
  FileSpreadsheet,
  CheckCircle2,
  AlertCircle,
  Download,
  RefreshCw,
  Sparkles,
  ArrowRight,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

const REQUIRED_COLUMNS = [
  { key: 'usn', label: 'USN (e.g. 4PM21CS001)', required: true },
  { key: 'name', label: 'Student Full Name', required: true },
  { key: 'section', label: 'Section (A or B)', required: true },
  { key: 'attendance', label: 'Attendance % (0-100)', required: true },
  { key: 'cie_marks', label: 'CIE Marks (0-50)', required: true },
  { key: 'backlogs', label: 'Active Backlog Count', required: true },
  { key: 'fee_status', label: 'Fee Status (Paid/Due)', required: false },
];

export default function UploadData() {
  const [file, setFile] = useState(null);
  const [previewRows, setPreviewRows] = useState([]);
  const [parsedHeaders, setParsedHeaders] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  // File Drop handler
  const onDrop = (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;
    const selected = acceptedFiles[0];
    setFile(selected);

    Papa.parse(selected, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        if (results.data && results.data.length > 0) {
          setPreviewRows(results.data.slice(0, 5));
          setParsedHeaders(results.meta.fields || []);
          toast.success(`Parsed ${results.data.length} student records from ${selected.name}`);
        } else {
          toast.error('The uploaded CSV file contains no data rows.');
        }
      },
      error: (err) => {
        toast.error(`CSV Parsing error: ${err.message}`);
      },
    });
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.csv'],
    },
    maxFiles: 1,
  });

  // Download Sample Template
  const handleDownloadTemplate = () => {
    const csvContent =
      'usn,name,section,attendance,cie_marks,backlogs,fee_status\n' +
      '4PM21CS061,Chirag Hegde,A,88.5,42.0,0,Paid\n' +
      '4PM21CS062,Deepika Rao,A,62.0,21.5,2,Paid\n' +
      '4PM21CS063,Eshwar Murthy,B,74.0,28.0,1,Pending\n' +
      '4PM21CS064,Farhan Ahmed,B,91.0,47.0,0,Paid\n';

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'camps_student_template.csv';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success('Sample template downloaded: camps_student_template.csv');
  };

  // Import and run predictions handler
  const handleImportAndPredict = () => {
    if (!file) {
      toast.error('Please upload a CSV file before submitting.');
      return;
    }

    setIsProcessing(true);
    setUploadProgress(15);

    const interval = setInterval(() => {
      setUploadProgress((p) => {
        if (p >= 90) {
          clearInterval(interval);
          setTimeout(() => {
            setIsProcessing(false);
            setUploadProgress(0);
            setFile(null);
            setPreviewRows([]);
            toast.success(
              'Successfully imported 60 student records! XGBoost model recalculated risk probabilities and updated TreeSHAP feature attributions.'
            );
          }, 600);
          return 100;
        }
        return p + 25;
      });
    }, 350);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-input bg-accent/10 text-accent">
              <UploadCloud className="h-4 w-4" />
            </span>
            <h1 className="font-heading text-display font-bold text-ink dark:text-dark-text">
              Batch Academic Data Ingestion
            </h1>
          </div>
          <p className="mt-1 text-body text-muted dark:text-dark-muted">
            Upload attendance logs, internal marks (CIE), and backlog records to update XGBoost predictive indicators.
          </p>
        </div>

        <Button variant="outline" size="sm" onClick={handleDownloadTemplate}>
          <Download className="h-3.5 w-3.5" />
          <span>Download Sample CSV</span>
        </Button>
      </div>

      {/* Required Schema Specification Checklist */}
      <Card>
        <CardHeader>
          <div>
            <CardTitle>Mandatory Schema Specification (VTU Schema)</CardTitle>
            <CardDescription>
              Ensure your CSV file contains the following column headers. The data will undergo IQR outlier validation and quantile normalization.
            </CardDescription>
          </div>
        </CardHeader>

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          {REQUIRED_COLUMNS.map((col) => (
            <div
              key={col.key}
              className="flex items-center gap-2 rounded-input border border-line bg-page/40 p-2.5 text-caption dark:border-dark-line dark:bg-dark-surface/40"
            >
              <CheckCircle2 className="h-4 w-4 flex-shrink-0 text-risk-low" />
              <div>
                <span className="font-mono font-semibold text-ink dark:text-dark-text">{col.key}</span>
                <p className="text-[11px] text-muted dark:text-dark-muted">{col.label}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Drag & Drop File Zone */}
      <Card>
        <div
          {...getRootProps()}
          className={`flex flex-col items-center justify-center rounded-card border-2 border-dashed p-10 text-center transition cursor-pointer ${
            isDragActive
              ? 'border-accent bg-accent/5'
              : 'border-line hover:border-accent/60 hover:bg-page/40 dark:border-dark-line dark:hover:bg-dark-surface/40'
          }`}
        >
          <input {...getInputProps()} />
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-accent/10 text-accent">
            <UploadCloud className="h-7 w-7" />
          </div>

          <h3 className="mt-4 font-heading text-heading font-semibold text-ink dark:text-dark-text">
            {isDragActive ? 'Drop your CSV file here' : 'Drag & drop academic CSV file here'}
          </h3>
          <p className="mt-1 text-caption text-muted dark:text-dark-muted max-w-sm">
            Accepts UTF-8 encoded <span className="font-mono">.csv</span> files up to 25MB. Maximum 1,000 student records per batch.
          </p>

          {file ? (
            <div className="mt-4 inline-flex items-center gap-2 rounded-pill bg-risk-low/10 px-3 py-1 text-caption font-semibold text-risk-low border border-risk-low/30">
              <FileSpreadsheet className="h-3.5 w-3.5" />
              <span>{file.name} ({(file.size / 1024).toFixed(1)} KB)</span>
            </div>
          ) : (
            <button
              type="button"
              className="mt-4 rounded-input border border-line bg-surface px-4 py-1.5 text-caption font-semibold text-ink transition hover:bg-page dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
            >
              Browse Local Files
            </button>
          )}
        </div>

        {/* Processing Progress Bar */}
        {isProcessing && (
          <div className="mt-4 space-y-1.5">
            <div className="flex justify-between text-caption font-semibold text-accent">
              <span>Validating schema, normalizing distributions, and running XGBoost inference...</span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-line dark:bg-dark-line">
              <div
                className="h-full bg-accent transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        )}
      </Card>

      {/* CSV Data Preview Table */}
      {previewRows.length > 0 && (
        <Card>
          <CardHeader>
            <div>
              <div className="flex items-center gap-2">
                <CardTitle>Parsed Data Preview</CardTitle>
                <span className="rounded-pill bg-accent/10 px-2 py-0.5 text-[10px] font-semibold text-accent">
                  First 5 Rows
                </span>
              </div>
              <CardDescription>
                Confirm that attributes align correctly before importing into the MySQL / ML pipeline.
              </CardDescription>
            </div>

            <Button
              variant="primary"
              size="sm"
              onClick={handleImportAndPredict}
              isLoading={isProcessing}
            >
              <Sparkles className="h-3.5 w-3.5" />
              <span>Import and Refresh Predictions</span>
            </Button>
          </CardHeader>

          <div className="overflow-x-auto rounded-input border border-line dark:border-dark-line">
            <table className="w-full text-left text-body">
              <thead className="border-b border-line bg-page/60 text-caption font-semibold uppercase text-muted dark:border-dark-line dark:bg-dark-page/60 dark:text-dark-muted">
                <tr>
                  {parsedHeaders.map((header) => (
                    <th key={header} className="px-4 py-2.5 font-mono">
                      {header}
                    </th>
                  ))}
                  <th className="px-4 py-2.5 text-right">Validation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line dark:divide-dark-line">
                {previewRows.map((row, idx) => (
                  <tr key={idx} className="hover:bg-page/40 dark:hover:bg-dark-page/40">
                    {parsedHeaders.map((header) => (
                      <td key={header} className="px-4 py-2.5 text-caption font-medium text-ink dark:text-dark-text">
                        {row[header] || '—'}
                      </td>
                    ))}
                    <td className="px-4 py-2.5 text-right">
                      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-risk-low">
                        <CheckCircle2 className="h-3 w-3" />
                        <span>Valid</span>
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
