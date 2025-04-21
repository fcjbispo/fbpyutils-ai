"""
Docling Converter Module

This module provides a utility class for converting documents using the Docling CLI tool.
It supports multiple input and output formats with flexible configuration options.

Key Features:
- Automatic input format detection
- Support for various document formats
- OCR and PDF parsing configuration
- Temporary file handling for conversions
"""

import os
import subprocess
import tempfile
import uuid
from typing import Optional, List, Dict
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image

from fbpyutils_ai import logging


class DoclingConverter:
    """
    A utility class for converting documents using the Docling CLI tool.

    This class provides methods to convert documents between various formats,
    with support for OCR, PDF parsing, and flexible configuration.

    Attributes:
        SUPPORTED_INPUT_FORMATS (List[str]): Supported input document formats
        SUPPORTED_IMAGE_EXPORT_MODES (List[str]): Supported image export modes
        SUPPORTED_OUTPUT_FORMATS (List[str]): Supported output document formats
    """

    SUPPORTED_INPUT_FORMATS: List[str] = [
        "pdf",
        "docx",
        "pptx",
        "html",
        "image",
        "asciidoc",
        "md",
    ]
    SUPPORTED_IMAGE_EXPORT_MODES: List[str] = ["placeholder", "embedded", "referenced"]
    SUPPORTED_OUTPUT_FORMATS: List[str] = ["md", "json", "text", "doctags", "html"]
    SUPPORTED_DEVICES: List[str] = ["cpu", "cuda", "mps", "auto"]
    SUPPORTED_TABLE_MODES: List[str] = ["fast", "accurate"]

    @staticmethod
    def _validate_source(source: str) -> bool:
        """
        Validate if the source file exists and is accessible.

        Args:
            source (str): Path to the source file

        Returns:
            bool: True if file exists, otherwise raises FileNotFoundError

        Raises:
            FileNotFoundError: If source file does not exist
        """
        if not os.path.exists(source):
            logging.error(f"Source file not found: {source}")
            raise FileNotFoundError(f"Source file not found: {source}")
        return True

    @staticmethod
    def _detect_input_format(source: str) -> Optional[str]:
        """
        Automatically detect input format from file extension.

        Args:
            source (str): Path to the source file

        Returns:
            Optional[str]: Detected input format or None if not recognized
        """
        ext = Path(source).suffix.lower().replace(".", "")
        detected_format = (
            ext if ext in DoclingConverter.SUPPORTED_INPUT_FORMATS else None
        )

        if detected_format:
            logging.info(f"Detected input format: {detected_format}")
        else:
            logging.error(f"Could not detect format for file: {source}")

        return detected_format

    @staticmethod
    def _generate_image_based_pdf(source_pdf: str) -> str:
        """
        Converte um PDF em um novo PDF onde cada página é uma imagem.

        Args:
            source_pdf (str): Caminho do PDF original

        Returns:
            str: Caminho do novo PDF gerado
        """
        logging.info(f"Converting PDF to images for better OCR: {source_pdf}")

        pdf_tmpdir = tempfile.TemporaryDirectory(
            prefix=f"docling_pdf_{uuid.uuid4().hex}_"
        )
        try:
            # Generate unique prefix for image files
            image_prefix = f"page_{uuid.uuid4().hex}"

            # Convert PDF to high-quality images with unique names
            logging.debug("Converting PDF pages to images...")
            images = convert_from_path(
                source_pdf,
                dpi=300,  # High DPI for better OCR
                output_folder=pdf_tmpdir.name,
                fmt="png",  # PNG format for better quality
                output_file=image_prefix,  # Prefix for image files
            )

            # Create temporary PDF with unique name
            with tempfile.NamedTemporaryFile(
                prefix=f"docling_converted_{uuid.uuid4().hex}_",
                suffix=".pdf",
                dir=pdf_tmpdir.name,
                delete=False,
            ) as temp_pdf:
                logging.debug(f"Creating temporary PDF from images: {temp_pdf.name}")

                # Convert first image to PDF and append the rest
                images[0].save(
                    temp_pdf.name,
                    "PDF",
                    resolution=300.0,
                    save_all=True,
                    append_images=images[1:],
                )

                # Create a copy of the temporary PDF to prevent deletion
                with tempfile.NamedTemporaryFile(
                    prefix=f"docling_persistent_{uuid.uuid4().hex}_",
                    suffix=".pdf",
                    delete=False,
                ) as persistent_pdf:
                    with open(temp_pdf.name, "rb") as src_file:
                        persistent_pdf.write(src_file.read())

                    # Update source to use the persistent PDF
                    source = persistent_pdf.name
                    logging.info(
                        f"Successfully created persistent image-based PDF, path: {source}"
                    )
                    logging.debug(
                        f"Persistent PDF file exists: {os.path.exists(source)}"
                    )
                    return source
        finally:
            # Ensure the temporary directory is cleaned up
            pdf_tmpdir.cleanup()

    def convert(
        self,
        source: str,
        input_format: Optional[str] = None,
        output_format: str = "md",
        ocr: bool = True,
        ocr_engine: str = "easyocr",
        pdf_backend: str = "dlparse_v1",
        table_mode: str = "accurate",
        image_export_mode: str = "placeholder",
        artifacts_path: Optional[str] = None,
        abort_on_error: bool = False,
        num_threads: int = 4,
        device: str = "auto",
        force_image: bool = False,
    ) -> str:
        """
        Convert document using docling with flexible parameters.

        Args:
            source (str): Path to source file
            input_format (Optional[str]): Input file format
            output_format (str): Desired output format
            ocr (bool): Enable/disable OCR
            ocr_engine (str): OCR engine to use
            pdf_backend (str): PDF parsing backend
            table_mode (str): Table extraction mode
            image_export_mode (str): Image export mode
            artifacts_path (Optional[str]): Path to model artifacts
            abort_on_error (bool): Stop processing on first error
            num_threads (int): Number of threads to use
            device (str): Device to use for processing defaults to 'auto'
            force_image (bool): When True and input is PDF, converts PDF to images
                              before processing for better OCR accuracy. Defaults to False.

        Returns:
            str: Converted document content

        Raises:
            FileNotFoundError: If source file does not exist
            ValueError: If input or output format is unsupported
            subprocess.CalledProcessError: If docling conversion fails
        """
        try:
            # Validate inputs
            self._validate_source(source)

            if input_format is None:
                input_format = self._detect_input_format(source)

            if input_format not in self.SUPPORTED_INPUT_FORMATS:
                logging.error(f"Unsupported input format: {input_format}")
                raise ValueError(f"Unsupported input format: {input_format}")

            # Automatically enable OCR for PDF with force_image
            if force_image and (
                input_format == "pdf" or Path(source).suffix.lower() == ".pdf"
            ):
                logging.info("Enabling OCR for PDF due to force_image=True")
                ocr = True

            if output_format not in self.SUPPORTED_OUTPUT_FORMATS:
                logging.error(f"Unsupported output format: {output_format}")
                raise ValueError(f"Unsupported output format: {output_format}")
            if image_export_mode not in self.SUPPORTED_IMAGE_EXPORT_MODES:
                logging.error(f"Unsupported image export mode: {image_export_mode}")
                raise ValueError(f"Unsupported image export mode: {image_export_mode}")

            if table_mode not in self.SUPPORTED_TABLE_MODES:
                logging.error(f"Unsupported table mode: {table_mode}")
                raise ValueError(f"Unsupported table mode: {table_mode}")

            # Handle force_image for PDF inputs
            if force_image and (
                input_format == "pdf" or Path(source).suffix.lower() == ".pdf"
            ):
                if output_format == "image":
                    logging.warning(
                        "force_image=True with output_format='image' is redundant"
                    )
                source = self._generate_image_based_pdf(source)

            # Create temporary output directory
            with tempfile.TemporaryDirectory() as tmpdir:
                # Derive output filename based on source filename
                source_filename = Path(source).stem  # Get filename without extension
                output_filename = f"{source_filename}.{output_format}"
                output_path = os.path.join(tmpdir, output_filename)

                # Construct docling command
                cmd = [
                    "docling",
                    "--from",
                    input_format,
                    "--to",
                    output_format,
                    "--output",
                    tmpdir,  # Specify output directory
                    "--pdf-backend",
                    pdf_backend,
                    "--table-mode",
                    table_mode,
                    "--image-export-mode",
                    image_export_mode,
                ]

                if ocr:
                    cmd.extend(["--ocr", f"--ocr-engine={ocr_engine}"])

                if artifacts_path:
                    cmd.extend(["--artifacts-path", artifacts_path])

                if abort_on_error:
                    cmd.append("--abort-on-error")

                if num_threads:
                    if num_threads < 1 or num_threads > os.cpu_count():
                        logging.info("Invalid number of threads, using default value")
                        num_threads = 4
                    cmd.extend(["--num-threads", str(num_threads)])

                if device:
                    if device not in self.SUPPORTED_DEVICES:
                        logging.info(f"Invalid device specified, using default value")
                        device = "auto"
                    cmd.extend(["--device", device])

                # Debug: Check if source file exists before running docling
                logging.debug(f"Source file path before docling: {source}")
                logging.debug(
                    f"Source file exists before docling: {os.path.exists(source)}"
                )

                cmd.append(source)

                try:
                    # Run docling command with explicit UTF-8 encoding
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        check=True,
                        encoding="utf-8",
                        errors="replace",
                    )

                    # List files in temporary directory to debug
                    output_files = os.listdir(tmpdir)
                    logging.info(f"Files in temp directory: {output_files}")

                    # Find the output file in the temporary directory
                    output_file = next(
                        (f for f in output_files if f.endswith(f".{output_format}")),
                        None,
                    )

                    if not output_file:
                        raise FileNotFoundError(
                            f"No {output_format} file found in temporary directory"
                        )

                    full_output_path = os.path.join(tmpdir, output_file)

                    # Read converted file
                    with open(full_output_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    logging.info(f"Docling conversion successful: {source}")
                    return content

                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                    # Log detailed error information
                    logging.error(f"Docling conversion failed: {e}")

                    # If it's a CalledProcessError, log stdout and stderr
                    if isinstance(e, subprocess.CalledProcessError):
                        logging.error(f"Docling Command: {' '.join(e.cmd)}")
                        logging.error(f"Docling STDOUT: {e.stdout}")
                        logging.error(f"Docling STDERR: {e.stderr}")

                    raise

        except Exception as e:
            # Debug: Log temporary directory details
            logging.error(f"Conversion error in {__file__}: {str(e)}")
            logging.error(f"Temporary source file path: {source}")
            logging.error(
                f"Temporary source file exists: {os.path.exists(source) if 'source' in locals() else 'Not set'}"
            )

            raise

    @staticmethod
    def version() -> Dict[str, str]:
        """
        Get the version of the docling tool and other software used.

        Returns:
            Dict[str, str]: A dictionary containing the version information.

        Raises:
            subprocess.CalledProcessError: If docling version check fails
        """
        try:
            cmd = ["docling", "--version"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            output = result.stdout

            version_info = {}
            for line in output.splitlines():
                if "Docling version:" in line:
                    version_info["docling_version"] = line.split(": ")[1].strip()
                elif "Docling Core version:" in line:
                    version_info["docling_core_version"] = line.split(": ")[1].strip()
                elif "Docling IBM Models version:" in line:
                    version_info["docling_ibm_models_version"] = line.split(": ")[
                        1
                    ].strip()
                elif "Docling Parse version:" in line:
                    version_info["docling_parse_version"] = line.split(": ")[1].strip()

            logging.info(f"Docling version info: {version_info}")

            return version_info

        except subprocess.CalledProcessError as e:
            logging.error(f"Error getting docling version: {e}")
            raise
        except Exception as e:
            logging.error(f"Error getting docling version in {__file__}: {str(e)}")
            raise
