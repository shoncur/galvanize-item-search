# List of regex patterns for various number formats
list_of_patterns = [
    r'\d{3}-\d{5}-\d{3}',
    r'\d{3}-\d{5}-\d{2}(?!\d)',
    r'\d{3}-\d{5}(?!-)',
    r'(?<!(\d|-))\d{2}-\d{5}',
    r'ECO-\d{2}-\d{5}',
    r'ACM-\d{5}-\d{2}',
    r'ACM-\d{5}(?!-)',
    r'CER-\d{5}-\d{2}',
    r'CER-\d{5}(?!-)',
    r'CEP-\d{5}-\d{2}',
    r'CEP-\d{5}(?!-)',
    r'CSP-\d{5}-\d{2}',
    r'CSP-\d{5}(?!-)',
    r'CSR-\d{5}-\d{2}',
    r'CSR-\d{5}(?!-)',
    r'CLN-\d{5}-\d{2}',
    r'CLN-\d{5}(?!-)',
    r'DDP-\d{5}',
    r'(?<!\w)DP-\d{4}',
    r'DCD-\d{5}-\d{2}',
    r'DCD-\d{5}(?!-)',
    r'DHF-\d{5}-[A-Z0-9]{2}',
    r'DHF-\d{5}(?!-)',
    r'DMR-\d{5}-[A-Z0-9]{2}',
    r'DMR-\d{5}(?!-)',
    r'DOT-\d{5}-\d{2}',
    r'DOT-\d{5}(?!-)',
    r'EDR-\d{5}(?!-)',
    r'FRM-\d{5}(?!-)',
    r'LRP-\d{5}(?!-)',
    r'LRR-\d{5}(?!-)',
    r'LHR-\d{5}(?!-)',
    r'LHR-\d{5}-\d{2}',
    r'LHR-\d{5}-\d{3}',
    r'MPI-\d{5}(?!-)',
    r'MKG-\d{5}(?!-)',
    r'MKG-\d{5}-\d{2}',
    r'MA-\d{5}(?!-)',
    r'PCP-\d{5}-\d{2}',
    r'PCR-\d{5}(?!-)',
    r'PMSP-\d{5}(?!-)',
    r'PMSR-\d{5}(?!-)',
    r'PSUR-\d{5}(?!-)',
    r'QPL-\d{5}(?!-)',
    r'RAD-\d{5}(?!-)',
    r'RSK-\d{5}(?!-)',
    r'SLS-\d{5}(?!-)',
    r'SWP-\d{5}(?!-)',
    r'SOP-\d{5}(?!-)',
    r'STM-\d{5}(?!-)',
    r'TFN-\d{5}(?!-)',
    r'TFN-\d{5}-\d{2}',
    r'TP-\d{5}(?!-)',
    r'TP-\d{5}-\d{2}',
    r'TR-\d{5}(?!-)',
    r'TR-\d{5}-\d{2}',
    r'WRK-\d{5}(?!-)',
    r'FAB-\d{5}-\d{3}-\d{3}',
    r'BRD-\d{5}-\d{3}-\d{3}',
    r'GTI-\d{5}-\d{2}',
    r'EQP-\d{5}',
    r'PRT-\d{5}-\d{3}-\d{3}',
    r'PRT-\d{5}-\d{3}',
    r'LBL-\d{5}-\d{3}',
    r'OTS-\d{5}-\d{3}',
    r'SCH-\d{5}-\d{3}-\d{3}',
    r'SW-\d{5}-\d{3}-\d{3}',
    r'TFX-\d{5}-\d{3}-\d{3}'
]