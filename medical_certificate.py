import tkinter as tk
from tkinter import ttk, font, messagebox, filedialog
from datetime import datetime
import tkinter.scrolledtext as scrolledtext
import os
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import subprocess

class MedicalCertificateWindow:
    def __init__(self, parent, patient_data=None):
        self.window = tk.Toplevel(parent)
        self.window.title("Medical Certificate")
        self.window.geometry("800x600")
        self.window.configure(bg="#f0f0f0")
        
        # Parent reference
        self.parent = parent
        
        # Patient data should include name, age, address, findings, remarks
        self.patient_data = patient_data or {
            "name": "", 
            "age": "", 
            "address": "", 
            "findings": "",
            "remarks": ""
        }
        
        self.create_widgets()
        self.generate_medical_certificate()
        
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.window, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Instructions label
        instructions = tk.Label(main_frame, text="You can edit the certificate text below before printing or saving",
                              bg="#f0f0f0", fg="#3498db", font=("Arial", 10, "italic"))
        instructions.pack(fill=tk.X, pady=(0, 5))
        
        # Rich text box with scrollbar - now editable by default
        self.rich_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=80, height=30)
        self.rich_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Button frame
        button_frame = tk.Frame(self.window, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Save to File button (new)
        self.save_button = ttk.Button(button_frame, text="Save to File", command=self.save_to_file)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # Print button (renamed from Print Certificate to Export as PDF)
        self.print_button = ttk.Button(button_frame, text="Export as PDF", command=self.export_as_pdf)
        self.print_button.pack(side=tk.LEFT, padx=5)
        
        # PDF Print button - new button for generating and printing PDF
        self.pdf_button = ttk.Button(button_frame, text="Print as PDF", command=self.print_as_pdf)
        self.pdf_button.pack(side=tk.LEFT, padx=5)
        
        # Exit button
        self.exit_button = ttk.Button(button_frame, text="Close", command=self.window.destroy)
        self.exit_button.pack(side=tk.RIGHT, padx=5)
    
    def save_to_file(self):
        """Save the certificate text to a file"""
        try:
            # Get content from the rich text widget
            content = self.rich_text.get("1.0", tk.END)
            
            # Get the patient name for the default filename
            patient_name = self.patient_data.get('name', 'Unknown').replace(' ', '_')
            default_filename = f"Medical_Certificate_{patient_name}_{datetime.now().strftime('%Y%m%d')}.txt"
            
            # Open file dialog to select save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=default_filename
            )
            
            if file_path:
                with open(file_path, 'w') as file:
                    file.write(content)
                messagebox.showinfo("Success", f"Certificate saved to:\n{file_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def export_as_pdf(self):
        """Export the certificate as a PDF file"""
        try:
            # Get the patient name for the default filename
            patient_name = self.patient_data.get('name', 'Unknown').replace(' ', '_')
            default_filename = f"Medical_Certificate_{patient_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            # Open file dialog to select save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=default_filename
            )
            
            if file_path:
                # Create a PDF document with A4 size
                self.generate_pdf(file_path)
                
                # Show success message with option to open the file
                response = messagebox.askyesno(
                    "Success", 
                    f"Certificate saved as PDF to:\n{file_path}\n\nWould you like to open it now?",
                    icon='info'
                )
                
                if response:
                    if os.name == 'nt':  # Windows
                        os.startfile(file_path)
                    else:  # macOS and Linux
                        subprocess.call(['xdg-open', file_path])
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create PDF: {str(e)}")
    
    def print_certificate(self):
        """Deprecated: This function is kept for backward compatibility"""
        self.export_as_pdf()
    
    def print_as_pdf(self):
        """Generate a PDF and open it for printing"""
        try:
            # Create a temporary PDF file
            fd, pdf_path = tempfile.mkstemp(suffix='.pdf')
            os.close(fd)
            
            # Generate the PDF
            self.generate_pdf(pdf_path)
            
            # Show a success message
            messagebox.showinfo("PDF Created", 
                "The medical certificate has been created as a PDF.\n"
                "It will open in your default PDF viewer where you can print it.")
            
            # Open with system default PDF viewer
            if os.name == 'nt':  # Windows
                os.startfile(pdf_path)
            else:  # macOS and Linux
                subprocess.call(['xdg-open', pdf_path])
                
            # Clean up temp file after delay
            self.window.after(30000, lambda: self.cleanup_temp_file(pdf_path))
                
        except Exception as e:
            messagebox.showerror("PDF Error", f"Failed to create PDF: {str(e)}")
    
    def cleanup_temp_file(self, file_path):
        """Clean up temporary files after a delay"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error cleaning up temporary file: {e}")
    
    def generate_pdf(self, pdf_path):
        """Generate a PDF file with the certificate content that matches the visual layout"""
        # Create a PDF document with A4 size
        doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=72)
        
        # Styles for different text parts
        styles = getSampleStyleSheet()
        
        # Custom styles that match the rich text display
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Heading1'],
            fontSize=18,
            fontName='Helvetica-Bold',
            textColor=colors.blue,
            spaceAfter=6
        )
        
        subheader_style = ParagraphStyle(
            'SubheaderStyle',
            parent=styles['Heading2'],
            fontSize=11,
            fontName='Helvetica-Bold',
            spaceAfter=3
        )
        
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            fontName='Helvetica-Bold',
            alignment=0,  # Left alignment to match rich text
            spaceAfter=12,
            spaceBefore=6
        )
        
        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=4
        )
        
        diagnosis_style = ParagraphStyle(
            'DiagnosisStyle',
            parent=styles['Heading3'],
            fontSize=12,
            fontName='Helvetica',
            spaceAfter=6,
            spaceBefore=6
        )
        
        remarks_style = ParagraphStyle(
            'RemarksStyle',
            parent=diagnosis_style,
            spaceBefore=24  # Add more space before remarks
        )
        
        signature_style = ParagraphStyle(
            'SignatureStyle',
            parent=styles['Normal'],
            fontSize=10,
            alignment=2  # Right alignment
        )
        
        # Get today's date for the certificate
        today_date = datetime.now().strftime("%A, %d %B %Y")
        
        # Elements to add to the PDF
        elements = []
        
        # Header section
        elements.append(Paragraph("DR. BELINDA O. CABAUATAN", header_style))
        elements.append(Paragraph("ADULT NEUROLOGY", subheader_style))
        elements.append(Paragraph("BRAIN, SPINAL CORD, NERVE AND MUSCLE SPECIALIST", subheader_style))
        elements.append(Spacer(1, 12))
        
        # Title - keep the same indentation as in the rich text
        elements.append(Paragraph("               MEDICAL CERTIFICATE", title_style))
        elements.append(Spacer(1, 12))
        
        # Patient information
        patient_info = (f"This is to certify that {self.patient_data['name']} {self.patient_data['age']} years old, "
                       f"from {self.patient_data['address']} was.")
        elements.append(Paragraph(patient_info, normal_style))
        elements.append(Paragraph(f"seen and examined in this clinic on {today_date}.", normal_style))
        elements.append(Spacer(1, 12))
        
        # Diagnosis
        elements.append(Paragraph("DIAGNOSIS:", diagnosis_style))
        diagnosis_content = self.patient_data.get('findings', '')
        if diagnosis_content:
            elements.append(Paragraph(diagnosis_content, normal_style))
        else:
            # Add empty space for diagnosis if not provided
            elements.append(Spacer(1, 40))
        
        # Add blank space between diagnosis and remarks
        elements.append(Spacer(1, 24))
        
        # Remarks section
        elements.append(Paragraph("REMARKS:", remarks_style))
        remarks_content = self.patient_data.get('remarks', '')
        if remarks_content:
            # Split by lines to preserve formatting
            for line in remarks_content.split('\n'):
                if line.strip():
                    elements.append(Paragraph(line, normal_style))
        else:
            # Add empty space for remarks if not provided
            elements.append(Spacer(1, 60))
        
        # Certification notice with proper spacing
        elements.append(Spacer(1, 24))
        elements.append(Paragraph("This certification is issued for reference use only.", normal_style))
        elements.append(Paragraph(f"Issued this {today_date} at Iriga Clinic.", normal_style))
        
        # Add space before signature
        elements.append(Spacer(1, 72))
        
        # Doctor's signature section with right alignment
        elements.append(Paragraph("DR. BELINDA O. CABAUATAN M.D.", signature_style))
        elements.append(Paragraph("NEUROLOGY", signature_style))
        elements.append(Paragraph("Lic. No.    109769", signature_style))
        elements.append(Paragraph("PTR. No.    4813787", signature_style))
        
        # Build the PDF
        doc.build(elements)
        
        return pdf_path
    
    def append_text(self, text, style="normal", alignment="left", size=10, color=None, font_name="Arial"):
        # Create a unique tag name for this text style
        tag_name = f"{style}_{alignment}_{size}_{color}_{font_name}"
        
        # Configure the font
        if style == "bold":
            text_font = font.Font(family=font_name, size=size, weight="bold")
        else:
            text_font = font.Font(family=font_name, size=size)
        
        # Configure the tag with the font and alignment
        self.rich_text.tag_configure(tag_name, font=text_font)
        
        # Set alignment
        if alignment == "left":
            self.rich_text.tag_configure(tag_name, justify="left")
        elif alignment == "right":
            self.rich_text.tag_configure(tag_name, justify="right")
        elif alignment == "center":
            self.rich_text.tag_configure(tag_name, justify="center")
        
        # Set text color if specified
        if color:
            self.rich_text.tag_configure(tag_name, foreground=color)
        
        # Insert the text with the tag
        self.rich_text.insert(tk.END, text + "\n", tag_name)
    
    def generate_medical_certificate(self):
        # Clear previous content
        self.rich_text.delete(1.0, tk.END)
        
        # Get today's date
        today_date = datetime.now().strftime("%A, %d %B %Y")
        
        # Append the doctor's name in blue
        self.append_text("DR. BELINDA O. CABAUATAN", style="bold", alignment="left", size=18, color="blue")
        
        # Append specialization
        self.append_text("ADULT NEUROLOGY", style="bold", alignment="left", size=11)
        self.append_text("BRAIN, SPINAL CORD, NERVE AND MUSCLE SPECIALIST", style="bold", alignment="left", size=11)
        
        # Empty line
        self.rich_text.insert(tk.END, "\n")
        
        # Append the heading with Algerian font (using Arial as fallback if Algerian not available)
        self.append_text("               MEDICAL CERTIFICATE", style="bold", alignment="left", size=18, font_name="Algerian")
        
        # Empty line
        self.rich_text.insert(tk.END, "\n")
        
        # Patient information
        self.append_text(f"This is to certify that {self.patient_data['name']} {self.patient_data['age']} years old, from {self.patient_data['address']} was.", 
                        style="normal", alignment="left", size=10)
        self.append_text(f"seen and examined in this clinic on {today_date}.", 
                        style="normal", alignment="left", size=10)
        
        # Empty line
        self.rich_text.insert(tk.END, "\n")
        
        # Diagnosis
        self.append_text("DIAGNOSIS:", style="normal", alignment="left", size=12)
        self.append_text(self.patient_data.get('findings', ''), style="normal", alignment="left", size=10)
        
        # Add space
        for _ in range(4):  # Reduced space since we'll add remarks content
            self.rich_text.insert(tk.END, "\n")
        
        # Remarks section
        self.append_text("REMARKS:", style="normal", alignment="left", size=12)
        
        # Add remarks content if available
        if self.patient_data.get('remarks'):
            self.append_text(self.patient_data.get('remarks'), style="normal", alignment="left", size=10)
        else:
            # Add space if no remarks
            for _ in range(8):
                self.rich_text.insert(tk.END, "\n")
        
        # Add empty line
        self.rich_text.insert(tk.END, "\n")
        
        # Certification notice
        self.append_text("This certification is issued for reference use only.", 
                        style="normal", alignment="left", size=10)
        self.append_text(f"Issued this {today_date} at Iriga Clinic.", 
                        style="normal", alignment="left", size=10)
        
        # Add space
        for _ in range(8):
            self.rich_text.insert(tk.END, "\n")
        
        # Doctor info with right alignment
        self.append_text("DR. BELINDA O. CABAUATAN M.D.", style="normal", alignment="right", size=10)
        self.append_text("NEUROLOGY", style="normal", alignment="right", size=10)
        self.append_text("Lic. No.    109769", style="normal", alignment="right", size=10)
        self.append_text("PTR. No.    4813787", style="normal", alignment="right", size=10)
